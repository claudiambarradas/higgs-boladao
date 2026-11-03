#!/usr/bin/env python3
"""Extrai prints reais e folhas de análise. Não decide sozinho quais ângulos usar."""
from __future__ import annotations
import argparse
import json
import math
import re
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps, ImageFilter, ImageStat
from _common import SkillError, probe_video, require_file, run_command, save_json

def candidate_times(duration: float, fps: float = 25, *, count: int | None = None,
                    every: float | None = None, explicit: list[float] | None = None,
                    start: float = 0, end: float | None = None) -> list[float]:
    rate = fps if fps > 0 else 25.0
    last = max(0, duration - max(1 / rate, 0.01))
    end = last if end is None else end
    if not 0 <= start <= end <= last + 1e-6:
        raise SkillError(f"Intervalo inválido; use instantes entre 0 e {last:.4f} segundos.")
    if explicit is not None:
        values = explicit
        if not values or any(not math.isfinite(t) or t < 0 or t >= duration for t in values):
            raise SkillError("Instantes precisam ser finitos, >= 0 e menores que a duração.")
    elif count is not None:
        if count < 1:
            raise SkillError("--count precisa ser >= 1.")
        values = [(start + end) / 2] if count == 1 else [start + (end - start) * i / (count - 1) for i in range(count)]
    else:
        step = every if every is not None else 1.0
        if not math.isfinite(step) or step <= 0:
            raise SkillError("--every precisa ser positivo e finito.")
        if (end - start) / step > 100000:
            raise SkillError("Amostragem excessiva; refine um trecho menor.")
        values = [start + i * step for i in range(int((end - start) / step) + 1)] + [end]
    return sorted(set(round(t, 6) for t in values))

def scene_times(video: Path, threshold: float, timeout: float) -> list[float]:
    if not 0 < threshold < 1:
        raise SkillError("O limiar de cenas precisa estar entre 0 e 1.")
    result = run_command(["ffmpeg", "-hide_banner", "-nostdin", "-i", str(video),
                          "-vf", f"select='gt(scene,{threshold})',showinfo", "-an", "-sn",
                          "-f", "null", "-"], timeout=timeout)
    return sorted(set(float(s) for s in re.findall(r"pts_time:([0-9.]+)", result.stderr)))

def contact_sheets(paths: list[Path], times: list[float], directory: Path) -> list[str]:
    output = []
    for sheet_index, offset in enumerate(range(0, len(paths), 20), 1):
        batch = paths[offset:offset + 20]
        rows = math.ceil(len(batch) / 4)
        sheet = Image.new("RGB", (4 * 320, rows * 220), "white")
        draw = ImageDraw.Draw(sheet)
        for j, path in enumerate(batch):
            with Image.open(path) as im:
                thumb = ImageOps.contain(im.convert("RGB"), (308, 182))
            x, y = (j % 4) * 320, (j // 4) * 220
            sheet.paste(thumb, (x + (320 - thumb.width) // 2, y + 4))
            draw.text((x + 8, y + 190), f"frame {offset+j+1:04d} | ~{times[offset+j]:.3f}s", fill="black")
        name = f"analise-{sheet_index:03d}.jpg"
        sheet.save(directory / name, quality=88)
        output.append(name)
    return output

def extract(video: Path, out: Path, times: list[float], metadata: dict,
            sheets: bool = True) -> dict:
    if out.exists() and any(out.iterdir()):
        raise SkillError("A pasta de frames precisa estar vazia. Use outra pasta para não sobrescrever prints.")
    out.mkdir(parents=True, exist_ok=True)
    items, paths = [], []
    for i, time in enumerate(times, 1):
        path = out / f"frame-{i:04d}-{time:010.3f}s.png"
        run_command(["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-n",
                     "-ss", f"{time:.6f}", "-i", str(video), "-frames:v", "1",
                     "-vf", "scale=round(iw*sar):ih,setsar=1", "-threads", "1", str(path)])
        if not path.exists():
            raise SkillError(f"Sem imagem em {time:.3f}s; refine o instante. A saída está incompleta.")
        with Image.open(path) as im:
            im.load()
            dims = im.size
            # Indicador comparativo, não um detector de rosto nem de pose.
            edges = im.convert("L").resize((256, 256)).filter(ImageFilter.FIND_EDGES)
            sharpness = ImageStat.Stat(edges).var[0]
        paths.append(path)
        items.append({"file": path.name, "requested_timestamp_seconds": time,
                      "width": dims[0], "height": dims[1],
                      "sharpness_hint": round(sharpness, 2)})
    info = {"video": metadata, "frames": items,
            "analysis_complete": False,
            "note": "Instantes são alvos de busca, não PTS medidos. Abra TODAS as folhas e aprofunde trechos rápidos. O script não analisa semanticamente o vídeo.",
            "contact_sheets": contact_sheets(paths, times, out) if sheets else []}
    save_json(out / "frames.json", info)
    return info

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("video", type=Path)
    p.add_argument("--out", type=Path)
    p.add_argument("--probe-only", action="store_true")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--every", type=float)
    g.add_argument("--count", type=int)
    g.add_argument("--times", type=float, nargs="+")
    p.add_argument("--start", type=float, default=0)
    p.add_argument("--end", type=float)
    p.add_argument("--max-frames", type=int, default=240)
    p.add_argument("--scene-detect", action="store_true")
    p.add_argument("--scene-threshold", type=float, default=0.30)
    p.add_argument("--scan-timeout", type=float, default=300)
    p.add_argument("--no-sheets", action="store_true")
    a = p.parse_args()
    try:
        video = require_file(a.video)
        meta = probe_video(video)
        if a.probe_only:
            print(json.dumps(meta, ensure_ascii=False, indent=2)); return
        if a.out is None:
            raise SkillError("Use --out para indicar a pasta de extração.")
        times = candidate_times(meta["duration_seconds"], meta["fps"], count=a.count,
                                every=a.every, explicit=a.times, start=a.start, end=a.end)
        if a.scene_detect:
            found = scene_times(video, a.scene_threshold, a.scan_timeout)
            upper = a.end if a.end is not None else meta["duration_seconds"]
            times = sorted(set(times + [t for t in found if a.start <= t < upper]))
        if not 1 <= len(times) <= a.max_frames:
            raise SkillError(f"{len(times)} frames excedem o limite {a.max_frames}. Amplie o limite conscientemente ou use intervalos; nada foi truncado.")
        data = extract(video, a.out.resolve(), times, meta, sheets=not a.no_sheets)
        print(json.dumps({"frames": len(data["frames"]), "out": str(a.out.resolve()),
                          "sheets": data["contact_sheets"], "warnings": meta["warnings"]}, ensure_ascii=False, indent=2))
    except (SkillError, OSError, ValueError) as exc:
        p.exit(2, f"ERRO: {exc}\n")
if __name__ == "__main__":
    main()
