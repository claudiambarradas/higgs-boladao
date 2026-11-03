#!/usr/bin/env python3
"""Ponte para o CLI oficial. Não inventa endpoints, IDs de modelo ou parâmetros."""
from __future__ import annotations
import argparse
import json
import math
import re
import shutil
import subprocess
from pathlib import Path
from _common import (SkillError, load_json, relative_file, save_json, utc_now,
                     reserve_attempt, finish_attempt, exclusive_lock, sha256)
from verificar_referencias import validate_prompt

FLAG = re.compile(r"[a-zA-Z][a-zA-Z0-9_-]*\Z")
IDENTIFIER = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9_.:-]*\Z")

def run_cli(args: list[str], timeout: float = 120) -> subprocess.CompletedProcess[str]:
    binary = shutil.which("higgsfield")
    if not binary:
        raise SkillError("CLI Higgsfield não encontrado. Consulte references/instalacao.md.")
    try:
        return subprocess.run([binary] + args, capture_output=True, text=True,
                              encoding="utf-8", errors="replace", shell=False, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        raise SkillError("Timeout no CLI: o serviço pode ter recebido o pedido. Não reenviar; consultar tarefa/histórico.") from exc

def safe_identifier(value: object) -> str:
    if not isinstance(value, str) or not IDENTIFIER.fullmatch(value):
        raise SkillError("Identificador inválido; copie o ID real retornado pelo serviço.")
    return value

def build_command(plan_path: Path) -> tuple[list[str], dict]:
    plan = load_json(plan_path)
    root = plan_path.resolve().parent
    operation = plan.get("operation")
    if operation not in ("model", "workflow"):
        raise SkillError("operation precisa ser model ou workflow.")
    model = safe_identifier(plan.get("id"))
    if plan.get("mode") != "automatic":
        raise SkillError("O plano não está em modo automatic. O modo manual nunca envia geração de vídeo.")
    review = plan.get("review", {})
    for flag in ("schema_verified", "supports_video_edit", "references_reviewed",
                 "source_properties_checked", "input_mapping_verified"):
        if review.get(flag) is not True:
            raise SkillError(f"Revisão obrigatória ausente: {flag}.")
    schema_file = relative_file(root, plan.get("schema_file"))
    if not schema_file.read_text(encoding="utf-8-sig").strip():
        raise SkillError("O esquema consultado está vazio.")
    if not review.get("notes"):
        raise SkillError("Registre a verificação real do esquema e da associação das referências.")
    video = relative_file(root, plan.get("video"))
    images = [relative_file(root, f) for f in plan.get("images", [])]
    if not images:
        raise SkillError("Faltam imagens finais no plano de edição.")
    prompt = relative_file(root, plan.get("prompt_file")).read_text(encoding="utf-8-sig").strip()
    errors = validate_prompt(prompt, len(images), plan.get("max_prompt_chars"))
    if errors:
        raise SkillError("\n".join(errors))
    mapping = plan.get("input_mapping", {})
    video_flag, image_flag = mapping.get("video_flag"), mapping.get("image_flag")
    for field in (video_flag, image_flag):
        if not isinstance(field, str) or not FLAG.fullmatch(field):
            raise SkillError("Os nomes dos campos de mídia devem ser copiados do esquema atual, sem '--'.")
    reserved = {"prompt", "wait", "json", "help", "version", "api-key", "token", video_flag, image_flag}
    if video_flag == image_flag or video_flag in {"prompt", "wait", "json", "help"} or image_flag in {"prompt", "wait", "json", "help"}:
        raise SkillError("Mapeamento de mídia conflitante.")
    command = ["generate", "create" if operation == "model" else "workflow", model,
               "--prompt", prompt, "--" + video_flag, str(video)]
    for image in images:
        command += ["--" + image_flag, str(image)]
    parameters = plan.get("parameters", {})
    if not isinstance(parameters, dict):
        raise SkillError("parameters precisa ser um objeto.")
    for key, value in parameters.items():
        if not FLAG.fullmatch(key) or key in reserved:
            raise SkillError(f"Parâmetro reservado ou inválido: {key}.")
        values = value if isinstance(value, list) else [value]
        for item in values:
            if not isinstance(item, (str, int, float, bool)) or (isinstance(item, float) and not math.isfinite(item)):
                raise SkillError(f"Valor inválido em {key}.")
            command += ["--" + key, str(item).lower() if isinstance(item, bool) else str(item)]
    command += ["--json"]
    plan["_schema_sha256"] = sha256(schema_file)
    return command, plan

def job_id_from_response(data: object) -> str | None:
    if not isinstance(data, dict):
        return None
    for key in ("job_id", "job_set_id", "id"):
        value = data.get(key)
        if isinstance(value, str) and IDENTIFIER.fullmatch(value):
            return value
    for key in ("job", "job_set", "data"):
        value = job_id_from_response(data.get(key))
        if value:
            return value
    return None

def submit(plan_path: Path, ledger: Path, max_calls: int, quoted_credits: float,
           max_credits: float, timeout: float = 180) -> dict:
    command, plan = build_command(plan_path)
    if (not all(math.isfinite(n) for n in (quoted_credits, max_credits))
            or quoted_credits < 0 or max_credits < 0 or quoted_credits > max_credits):
        raise SkillError("A estimativa registrada ultrapassa o limite autorizado ou é inválida.")
    if not shutil.which("higgsfield"):
        raise SkillError("CLI Higgsfield não encontrado; não reservar cobrança.")
    state_path = plan_path.resolve().with_suffix(".higgs-state.json")
    with exclusive_lock(state_path.with_suffix(".lock")):
        if state_path.exists():
            raise SkillError(f"Este plano já tem registro: {state_path.name}. Consulte a tarefa; nunca reenvie só por timeout.")
        token = reserve_attempt(ledger, max_calls, "higgsfield", "video_edit")
        state = {"created_at": utc_now(), "status": "submitting_or_uncertain", "attempt": token,
                 "plan_sha256": sha256(plan_path), "schema_sha256": plan["_schema_sha256"],
                 "id": plan["id"], "quoted_credits": quoted_credits, "max_credits": max_credits,
                 "budget_note": "Limite local baseado na estimativa informada; não é bloqueio de cobrança no provedor."}
        save_json(state_path, state)
        try:
            response = run_cli(command, timeout)
            raw_path = plan_path.resolve().with_suffix(".higgs-response.txt")
            raw_path.write_text(response.stdout, encoding="utf-8")
            state.update(returncode=response.returncode, response_file=raw_path.name)
            try:
                payload = json.loads(response.stdout)
            except ValueError:
                payload = None
            job_id = job_id_from_response(payload)
            state["job_id"] = job_id
            state["status"] = "submitted_not_completed" if response.returncode == 0 and job_id else "uncertain_do_not_resubmit"
            save_json(state_path, state)
            finish_attempt(ledger, token, state["status"])
            if state["status"] == "uncertain_do_not_resubmit":
                raise SkillError(f"Envio incerto. Examine {raw_path.name} e o histórico da conta antes de outra geração.")
            return state
        except (SkillError, OSError) as exc:
            state["status"] = "uncertain_do_not_resubmit"
            save_json(state_path, state)
            finish_attempt(ledger, token, state["status"])
            raise exc

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    listing = sub.add_parser("list", help="Consulta catálogo; não gera vídeo")
    listing.add_argument("--operation", choices=["model", "workflow"], default="model")
    inspect = sub.add_parser("inspect", help="Salva esquema atual; não gera vídeo")
    inspect.add_argument("id")
    inspect.add_argument("--operation", choices=["model", "workflow"], default="model")
    inspect.add_argument("--out", required=True, type=Path)
    send = sub.add_parser("submit")
    send.add_argument("plan", type=Path)
    send.add_argument("--execute", action="store_true")
    send.add_argument("--ledger", type=Path)
    send.add_argument("--max-calls", type=int)
    send.add_argument("--quoted-credits", type=float)
    send.add_argument("--max-credits", type=float)
    for cmd in ("get", "wait"):
        read = sub.add_parser(cmd)
        read.add_argument("job_id")
        read.add_argument("--out", type=Path)
        read.add_argument("--timeout", type=float, default=900 if cmd == "wait" else 120)
    a = p.parse_args()
    try:
        if a.command == "submit":
            command, _ = build_command(a.plan)
            if not a.execute:
                print(json.dumps({"mode": "dry_run_no_generation", "argv": ["higgsfield"] + command}, ensure_ascii=False, indent=2)); return
            if any(x is None for x in (a.ledger, a.max_calls, a.quoted_credits, a.max_credits)):
                raise SkillError("Envio pago exige --ledger, --max-calls, --quoted-credits e --max-credits autorizados.")
            print(json.dumps(submit(a.plan, a.ledger, a.max_calls, a.quoted_credits, a.max_credits), ensure_ascii=False, indent=2)); return
        if a.command == "list":
            response = run_cli([a.operation, "list", "--json"])
        elif a.command == "inspect":
            if a.out.exists():
                raise SkillError("O arquivo de esquema já existe; use outro nome.")
            response = run_cli([a.operation, "get", safe_identifier(a.id), "--json"])
        else:
            response = run_cli(["generate", a.command, safe_identifier(a.job_id), "--json"], a.timeout)
        if response.returncode:
            raise SkillError(f"Consulta ao CLI falhou ({response.returncode}); confira autenticação e comandos com higgsfield --help.")
        if getattr(a, "out", None):
            a.out.parent.mkdir(parents=True, exist_ok=True)
            with a.out.open("x", encoding="utf-8") as stream:
                stream.write(response.stdout)
        print(response.stdout)
    except (SkillError, OSError, ValueError, TypeError) as exc:
        p.exit(2, f"ERRO: {exc}\n")
if __name__ == "__main__":
    main()
