"""Utilitários locais. Não há geração paga ou acesso de rede neste módulo."""
from __future__ import annotations
import hashlib
import json
import math
import os
import shutil
import subprocess
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterator

class SkillError(Exception):
    """Erro operacional que pode ser mostrado sem traceback."""

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        raise SkillError(f"JSON inválido ou inacessível: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SkillError(f"O JSON precisa ser um objeto: {path}")
    return value

def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".higgs-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.write("\n")
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)

def require_file(path: str | Path) -> Path:
    result = Path(path).expanduser().resolve()
    if not result.is_file():
        raise SkillError(f"Arquivo não encontrado: {result}")
    return result

def relative_file(base: Path, value: Any) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise SkillError("Falta um caminho de arquivo obrigatório no manifesto.")
    path = Path(value).expanduser()
    return require_file(path if path.is_absolute() else base / path)

def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def run_command(args: list[str], timeout: float = 180) -> subprocess.CompletedProcess[str]:
    if not args or not shutil.which(args[0]):
        raise SkillError(f"Executável não encontrado: {args[0] if args else '(vazio)'}")
    try:
        result = subprocess.run(args, capture_output=True, text=True,
                                encoding="utf-8", errors="replace", timeout=timeout,
                                shell=False)
    except subprocess.TimeoutExpired as exc:
        raise SkillError(f"Tempo limite excedido em {args[0]}; verifique o estado antes de repetir.") from exc
    if result.returncode != 0:
        raise SkillError(f"{args[0]} falhou ({result.returncode}): {result.stderr[-2500:]}")
    return result

def number(value: Any, default: float = 0.0) -> float:
    try:
        result = float(value)
        return result if math.isfinite(result) else default
    except (TypeError, ValueError):
        return default

def probe_video(path: Path) -> dict[str, Any]:
    result = run_command(["ffprobe", "-v", "error", "-show_format", "-show_streams",
                          "-of", "json", str(require_file(path))])
    data = json.loads(result.stdout)
    video = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"
                  and not s.get("disposition", {}).get("attached_pic")), None)
    if video is None:
        raise SkillError("Não há um fluxo de vídeo utilizável no arquivo.")
    duration = number(video.get("duration")) or number(data.get("format", {}).get("duration"))
    if duration <= 0:
        raise SkillError("Não foi possível determinar a duração; verifique o vídeo.")
    width, height = int(video["width"]), int(video["height"])
    sar = video.get("sample_aspect_ratio", "1:1")
    try:
        pixel_ratio = Fraction(sar.replace(":", "/"))
        if pixel_ratio <= 0:
            pixel_ratio = Fraction(1)
    except (ValueError, ZeroDivisionError):
        pixel_ratio = Fraction(1)
    rotation = number(video.get("tags", {}).get("rotate"))
    for side in video.get("side_data_list", []):
        if "rotation" in side:
            rotation = number(side["rotation"])
    display_width = width * float(pixel_ratio)
    display_height = float(height)
    if int(round(rotation)) % 180 == 90:
        display_width, display_height = display_height, display_width
    ratio = Fraction(display_width / display_height).limit_denominator(10000)
    try:
        fps = float(Fraction(video.get("avg_frame_rate", "0/1")))
    except (ValueError, ZeroDivisionError):
        fps = 0.0
    color_transfer = video.get("color_transfer", "unknown")
    warnings = []
    if color_transfer in ("smpte2084", "arib-std-b67"):
        warnings.append("Vídeo HDR: extração PNG pode mudar a aparência. Conferir cor; não aplicar tone mapping sem decisão explícita.")
    if abs(rotation % 90) > 0.01:
        warnings.append("Rotação não ortogonal: conferir proporção e enquadramento manualmente.")
    return {"file": str(path.resolve()), "duration_seconds": duration,
            "width": width, "height": height,
            "display_width": round(display_width), "display_height": round(display_height),
            "aspect_ratio": f"{ratio.numerator}:{ratio.denominator}",
            "display_ratio": display_width / display_height,
            "rotation_degrees": rotation, "sample_aspect_ratio": sar,
            "fps": fps, "has_audio": any(s.get("codec_type") == "audio" for s in data["streams"]),
            "video_codec": video.get("codec_name"), "color_transfer": color_transfer,
            "color_space": video.get("color_space"), "warnings": warnings}

@contextmanager
def exclusive_lock(path: Path) -> Iterator[None]:
    """Falha fechada: um lock órfão exige inspeção, nunca reenvio automático."""
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise SkillError(f"Operação em andamento ou lock órfão: {path}. Verifique antes de remover.") from exc
    try:
        with os.fdopen(fd, "w") as stream:
            stream.write(str(os.getpid()))
        yield
    finally:
        path.unlink(missing_ok=True)

def reserve_attempt(ledger: Path, max_calls: int, provider: str, operation: str) -> str:
    if max_calls < 1:
        raise SkillError("O limite de chamadas pagas precisa ser positivo e autorizado.")
    ledger = ledger.expanduser().resolve()
    with exclusive_lock(ledger.with_suffix(ledger.suffix + ".lock")):
        data = load_json(ledger) if ledger.exists() else {"version": 1, "attempts": []}
        attempts = data.get("attempts")
        if not isinstance(attempts, list):
            raise SkillError("Registro de gastos inválido; não será sobrescrito.")
        if len(attempts) >= max_calls:
            raise SkillError(f"Limite local atingido: {len(attempts)}/{max_calls} tentativas. Não gerar novamente sem autorização.")
        token = f"{len(attempts)+1}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f')}"
        attempts.append({"id": token, "provider": provider, "operation": operation,
                         "reserved_at": utc_now(), "status": "reserved_or_uncertain"})
        save_json(ledger, data)
        return token

def finish_attempt(ledger: Path, token: str, status: str) -> None:
    ledger = ledger.expanduser().resolve()
    with exclusive_lock(ledger.with_suffix(ledger.suffix + ".lock")):
        data = load_json(ledger)
        for item in data["attempts"]:
            if item["id"] == token:
                item.update(status=status, updated_at=utc_now())
                save_json(ledger, data)
                return
        raise SkillError("Tentativa não encontrada no registro local.")
