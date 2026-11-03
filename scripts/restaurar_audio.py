#!/usr/bin/env python3
"""Recoloca o áudio original somente depois de confirmar a correspondência temporal."""
from __future__ import annotations
import argparse
from pathlib import Path
from _common import SkillError, probe_video, require_file, run_command

def restore(original: Path, edited: Path, out: Path, timing_confirmed: bool) -> None:
    if not timing_confirmed:
        raise SkillError("Durações iguais não garantem sincronismo. Confira gestos/fala e use --timing-confirmed.")
    src, dst = probe_video(original), probe_video(edited)
    if not src["has_audio"]:
        raise SkillError("O original não tem áudio.")
    tolerance = max(.1, 2 / max(src["fps"], dst["fps"], 1))
    if abs(src["duration_seconds"] - dst["duration_seconds"]) > tolerance:
        raise SkillError("As durações diferem. Não cortar nem acelerar áudio automaticamente.")
    if out.exists() or out.resolve() in (original.resolve(), edited.resolve()):
        raise SkillError("A saída deve ser um novo arquivo.")
    if out.suffix.lower() != ".mp4":
        raise SkillError("Use saída .mp4 neste utilitário.")
    out.parent.mkdir(parents=True, exist_ok=True)
    run_command(["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-n",
                 "-i", str(edited), "-i", str(original), "-map", "0:v:0", "-map", "1:a:0",
                 "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out)])
    final = probe_video(out)
    if not final["has_audio"]:
        raise SkillError("O arquivo de saída não contém áudio; não entregar como concluído.")

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--original", type=Path, required=True)
    p.add_argument("--edited", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--timing-confirmed", action="store_true")
    a = p.parse_args()
    try:
        restore(require_file(a.original), require_file(a.edited), a.out, a.timing_confirmed)
        print(f"Áudio recolocado: {a.out}. Ouça o resultado completo antes de entregar.")
    except (SkillError, OSError, ValueError) as exc:
        p.exit(2, f"ERRO: {exc}\n")
if __name__ == "__main__":
    main()
