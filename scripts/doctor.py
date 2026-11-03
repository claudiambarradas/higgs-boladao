#!/usr/bin/env python3
"""Diagnóstico local: não mostra chaves e não faz pedidos pagos."""
from __future__ import annotations
import importlib.metadata
import json
import os
import shutil
import sys
from pathlib import Path

def main() -> None:
    root = Path(__file__).resolve().parents[1]
    report = {"python": sys.version.split()[0], "python_ok": sys.version_info >= (3, 10),
              "skill_md": (root / "SKILL.md").is_file(), "executables": {}, "packages": {},
              "openai_api_key_present": bool(os.getenv("OPENAI_API_KEY")),
              "image_model_configured": bool(os.getenv("OPENAI_IMAGE_MODEL")),
              "network_tested": False, "paid_generation_tested": False}
    for exe in ("ffmpeg", "ffprobe", "higgsfield"):
        report["executables"][exe] = bool(shutil.which(exe))
    for module in ("Pillow", "requests"):
        try:
            report["packages"][module] = importlib.metadata.version(module)
        except importlib.metadata.PackageNotFoundError:
            report["packages"][module] = None
    report["local_processing_ready"] = bool(report["python_ok"] and report["skill_md"]
        and all(report["executables"].get(x) for x in ("ffmpeg", "ffprobe"))
        and all(report["packages"].values()))
    report["notes"] = ["Autenticação, saldo, ferramentas nativas e disponibilidade de modelos precisam ser verificados pelo agente.",
                       "OPENAI_API_KEY é necessária apenas na rota API direta; uma ferramenta nativa de imagem pode substituí-la.",
                       "Higgsfield CLI é necessário só na rota CLI de automação, não na entrega manual."]
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not report["local_processing_ready"]:
        sys.exit(2)
if __name__ == "__main__":
    main()
