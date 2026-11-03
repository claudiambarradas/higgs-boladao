#!/usr/bin/env python3
"""Edição real de imagem via API OpenAI. Simula por padrão; cobra apenas com --execute."""
from __future__ import annotations
import argparse
import base64
import io
import json
import os
from contextlib import ExitStack
from pathlib import Path
import requests
from PIL import Image
from _common import (SkillError, require_file, reserve_attempt, finish_attempt,
                     save_json, utc_now, exclusive_lock)

ENDPOINT = "https://api.openai.com/v1/images/edits"

def parse_result(payload: dict) -> bytes:
    data = payload.get("data", [])
    if not data or not isinstance(data[0], dict) or not data[0].get("b64_json"):
        raise SkillError("A API não retornou uma imagem em b64_json; não repetir automaticamente.")
    try:
        raw = base64.b64decode(data[0]["b64_json"], validate=True)
        with Image.open(io.BytesIO(raw)) as im:
            im.load()
            buffer = io.BytesIO()
            im.save(buffer, format="PNG")
            return buffer.getvalue()
    except (ValueError, OSError) as exc:
        raise SkillError("A resposta não contém uma imagem válida.") from exc

def edit_image(images: list[Path], prompt: str, out: Path, model: str,
               size: str, quality: str, ledger: Path, max_calls: int,
               timeout: float = 300) -> dict:
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise SkillError("Defina OPENAI_API_KEY no ambiente; não envie sua chave no chat.")
    if not model.strip() or not prompt.strip():
        raise SkillError("Modelo e prompt são obrigatórios.")
    out = out.resolve()
    if out.suffix.lower() != ".png":
        raise SkillError("A saída deste utilitário precisa ter extensão .png.")
    out.parent.mkdir(parents=True, exist_ok=True)
    receipt = out.with_suffix(".request-state.json")
    with exclusive_lock(out.with_suffix(".generation.lock")):
        if out.exists() or receipt.exists():
            raise SkillError("Já há saída ou registro desta imagem. Inspecione o estado; não reenviar a mesma operação automaticamente.")
        token = reserve_attempt(ledger, max_calls, "openai", "image_edit")
        state = {"attempt": token, "model": model, "status": "submitting_or_uncertain",
                 "created_at": utc_now(), "output": out.name}
        save_json(receipt, state)
        try:
            with ExitStack() as stack:
                files = []
                for i, path in enumerate(images):
                    im = Image.open(path)
                    mime = Image.MIME.get(im.format, "application/octet-stream")
                    im.close()
                    stream = stack.enter_context(path.open("rb"))
                    files.append(("image[]", (f"input-{i+1}{path.suffix.lower()}", stream, mime)))
                response = requests.post(ENDPOINT,
                    headers={"Authorization": f"Bearer {api_key}"},
                    data={"model": model, "prompt": prompt, "n": "1", "size": size,
                          "quality": quality, "output_format": "png"},
                    files=files, timeout=(30, timeout), allow_redirects=False)
            state["request_id"] = response.headers.get("x-request-id")
            if response.status_code != 200:
                # Não registrar corpo/headers, que podem conter dados sensíveis.
                state.update(status="failed_or_uncertain", http_status=response.status_code)
                save_json(receipt, state)
                raise SkillError(f"A API retornou HTTP {response.status_code}. Consulte o request_id e a conta antes de repetir.")
            payload = response.json()
            raw = parse_result(payload)
            with out.open("xb") as stream:
                stream.write(raw)
            with Image.open(out) as im:
                width, height = im.size
            state.update(status="image_generated_not_visually_reviewed", width=width,
                         height=height, usage=payload.get("usage"), completed_at=utc_now())
            save_json(receipt, state)
            finish_attempt(ledger, token, "response_received")
            return state
        except (requests.RequestException, ValueError, OSError, SkillError) as exc:
            if state["status"] == "submitting_or_uncertain":
                state.update(status="uncertain_do_not_resubmit", error_type=type(exc).__name__)
                save_json(receipt, state)
            finish_attempt(ledger, token, "failed_or_uncertain")
            if isinstance(exc, SkillError):
                raise
            raise SkillError(f"Falha {type(exc).__name__}; confira {receipt.name}. Nenhuma repetição automática foi feita.") from exc

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--image", type=Path, required=True, help="Frame original deste ângulo (primeira imagem)")
    p.add_argument("--reference", type=Path, action="append", default=[], help="Âncora editada ou referência adicional; repetível")
    p.add_argument("--prompt-file", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--model", default=os.environ.get("OPENAI_IMAGE_MODEL"))
    p.add_argument("--size", default="auto")
    p.add_argument("--quality", default="high", choices=["auto", "low", "medium", "high", "xhigh", "max"])
    p.add_argument("--execute", action="store_true")
    p.add_argument("--ledger", type=Path)
    p.add_argument("--max-calls", type=int)
    p.add_argument("--timeout", type=float, default=300)
    a = p.parse_args()
    try:
        if not a.model:
            raise SkillError("Escolha --model ou configure OPENAI_IMAGE_MODEL com um modelo de imagem disponível na conta.")
        images = [require_file(a.image)] + [require_file(x) for x in a.reference]
        for path in images:
            with Image.open(path) as im:
                im.verify()
            if path.stat().st_size >= 50 * 1024 * 1024:
                raise SkillError(f"Imagem muito grande: {path.name}. Confira o limite atual do modelo.")
        prompt = require_file(a.prompt_file).read_text(encoding="utf-8-sig")
        if not prompt.strip():
            raise SkillError("O prompt de imagem está vazio.")
        if not a.execute:
            print(json.dumps({"mode": "dry_run_no_charge", "model": a.model,
                              "inputs": [p.name for p in images], "size": a.size,
                              "quality": a.quality, "output": str(a.out),
                              "note": "Para enviar: --execute --ledger CAMINHO --max-calls LIMITE_AUTORIZADO"}, ensure_ascii=False, indent=2))
            return
        if a.ledger is None or a.max_calls is None:
            raise SkillError("Geração paga exige --ledger e --max-calls previamente autorizados.")
        print(json.dumps(edit_image(images, prompt, a.out, a.model, a.size, a.quality,
                                    a.ledger, a.max_calls, a.timeout), ensure_ascii=False, indent=2))
    except (SkillError, OSError, ValueError) as exc:
        p.exit(2, f"ERRO: {exc}\n")
if __name__ == "__main__":
    main()
