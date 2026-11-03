#!/usr/bin/env python3
"""Confere e monta a entrega manual: imagens editadas reais + prompt + mapa + ZIP."""
from __future__ import annotations
import argparse
import json
import math
import shutil
import tempfile
import zipfile
from pathlib import Path
from PIL import Image, ImageChops
from _common import (SkillError, load_json, relative_file, probe_video, save_json,
                     sha256, utc_now)
from verificar_referencias import validate_prompt

def validate_manifest(path: Path) -> dict:
    path = path.resolve()
    data = load_json(path)
    if data.get("schema_version") != 1:
        raise SkillError("O manifesto precisa usar schema_version: 1.")
    if not str(data.get("requested_change", "")).strip():
        raise SkillError("Registre a transformação solicitada no manifesto.")
    video = relative_file(path.parent, data.get("video"))
    meta = probe_video(video)
    analysis = data.get("analysis", {})
    if analysis.get("full_timeline_reviewed") is not True:
        raise SkillError("A análise de toda a linha do tempo não foi concluída pelo agente.")
    if analysis.get("method") not in ("native_video", "temporal_sampling"):
        raise SkillError("Registre o método real de análise: native_video ou temporal_sampling.")
    if not analysis.get("notes"):
        raise SkillError("Registre as observações e limitações da análise.")
    if abs(float(analysis.get("duration_seconds", -1)) - meta["duration_seconds"]) > max(.1, 2/max(meta["fps"], 1)):
        raise SkillError("A duração analisada não corresponde à duração do vídeo.")
    model = data.get("video_model", {})
    if not model.get("id") or model.get("schema_verified") is not True or not model.get("verification_note"):
        raise SkillError("Falta registrar o modelo e a verificação real dos controles/limites disponíveis.")
    if not isinstance(model.get("parameters"), dict):
        raise SkillError("video_model.parameters precisa ser um objeto, mesmo quando vazio.")
    limit = model.get("max_reference_images")
    if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1:
        raise SkillError("Registre o número máximo de imagens aceitas pelo modelo consultado.")
    entries = data.get("images")
    if not isinstance(entries, list) or not 1 <= len(entries) <= limit:
        raise SkillError("Quantidade de referências inválida para o limite registrado do modelo.")
    prompt_path = relative_file(path.parent, data.get("prompt_file"))
    prompt = prompt_path.read_text(encoding="utf-8-sig").strip()
    errors = validate_prompt(prompt, len(entries), model.get("max_prompt_chars"))
    if errors:
        raise SkillError("\n".join(errors))
    files = []
    hashes = set()
    for n, entry in enumerate(entries, 1):
        if entry.get("label") != f"@imagem{n}":
            raise SkillError(f"O item {n} precisa usar @imagem{n}.")
        edited = relative_file(path.parent, entry.get("file"))
        source = relative_file(path.parent, entry.get("source_frame"))
        if edited.suffix.lower() not in (".png", ".jpg", ".jpeg"):
            raise SkillError("Converta as referências finais para PNG ou JPG sem mudar a composição.")
        if entry.get("visual_review_passed") is not True or not entry.get("review_notes") or not entry.get("role"):
            raise SkillError(f"@imagem{n}: falta revisão visual real, observações ou função da referência.")
        time = float(entry.get("timestamp_seconds", -1))
        if not math.isfinite(time) or not 0 <= time < meta["duration_seconds"]:
            raise SkillError(f"@imagem{n}: instante fora do vídeo.")
        digest = sha256(edited)
        if digest == sha256(source) or digest in hashes:
            raise SkillError(f"@imagem{n}: print original não editado ou referência duplicada.")
        hashes.add(digest)
        with Image.open(edited) as image, Image.open(source) as original:
            image.load(); original.load()
            if image.format not in ("PNG", "JPEG"):
                raise SkillError(f"@imagem{n}: conteúdo incompatível com PNG/JPG.")
            if image.size == original.size and ImageChops.difference(image.convert("RGB"), original.convert("RGB")).getbbox() is None:
                raise SkillError(f"@imagem{n}: pixels idênticos aos do print original.")
            image_ratio = image.width / image.height
            if abs(image_ratio / meta["display_ratio"] - 1) > .01:
                if not entry.get("aspect_adaptation_approved") or not entry.get("aspect_adaptation_note"):
                    raise SkillError(f"@imagem{n}: proporção difere do vídeo em mais de 1%. Não esticar nem cortar silenciosamente; regenerar ou registrar adaptação aprovada.")
            extension = ".png" if image.format == "PNG" else ".jpg"
            files.append({"path": edited, "name": f"imagem{n}{extension}", "sha256": digest,
                          "width": image.width, "height": image.height, "entry": entry})
    return {"manifest": data, "video": video, "metadata": meta, "prompt": prompt,
            "images": files}

def package(manifest_path: Path, out: Path, *, include_video: bool = False,
            make_zip: bool = True) -> dict:
    checked = validate_manifest(manifest_path)
    out = out.resolve()
    archive = out.parent / f"{out.name}.zip"
    if out.exists() or (make_zip and archive.exists()):
        raise SkillError("A pasta ou ZIP de saída já existe. Use um novo nome para preservar a entrega anterior.")
    out.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=".higgs-entrega-", dir=out.parent))
    data, meta = checked["manifest"], checked["metadata"]
    try:
        (temporary / "prompt.txt").write_text(checked["prompt"] + "\n", encoding="utf-8")
        video_name = checked["video"].name
        if include_video:
            video_name = "video1" + checked["video"].suffix.lower()
            shutil.copy2(checked["video"], temporary / video_name)
        lines = ["# Pacote manual — Higgs-boladao", "",
                 "As imagens abaixo já contêm a edição solicitada. Faça upload dos arquivos individuais, não de uma folha de contatos.", "",
                 f"**@video1** → `{video_name}` (vídeo original" + (", incluído neste pacote)." if include_video else "; use o seu arquivo original, não incluído para evitar duplicação)."), ""]
        safe_images = []
        for item in checked["images"]:
            shutil.copy2(item["path"], temporary / item["name"])
            entry = item["entry"]
            lines.append(f"**{entry['label']}** → `{item['name']}` — {entry['role']}; origem aproximada: {entry['timestamp_seconds']} s.")
            safe_images.append({"label": entry["label"], "file": item["name"],
                                "role": entry["role"], "timestamp_seconds": entry["timestamp_seconds"],
                                "sha256": item["sha256"], "width": item["width"], "height": item["height"],
                                "review_notes": entry["review_notes"],
                                "aspect_adaptation_note": entry.get("aspect_adaptation_note")})
        lines += ["", "## Configurações", f"Modelo verificado: **{data['video_model']['id']}**.",
                  f"Proporção de exibição do original: **{meta['aspect_ratio']}**. Duração: **{meta['duration_seconds']:.3f} s**.",
                  f"Áudio no original: **{'sim' if meta['has_audio'] else 'não'}**.",
                  "Consulte `configuracoes.json` para os parâmetros realmente verificados.", "",
                  "## Envio", "1. Abra a operação de edição do modelo escolhido e envie o vídeo original.",
                  "2. Envie as imagens na ordem do mapa e associe as referências no seletor da interface.",
                  "3. Cole TODO o conteúdo de `prompt.txt` e confira os parâmetros antes de gerar.",
                  "", "Arrobas escritas não fazem upload nem garantem associação automática. Se o seletor usar outro nome interno, confira a correspondência antes de iniciar.",
                  "", "## O que foi conferido", "O empacotador verifica arquivos, dimensões, rótulos e presença dos registros de revisão. A revisão visual é feita pelo agente; não é uma certificação automática de fidelidade.",
                  f"Análise: {data['analysis']['method']}. {data['analysis']['notes']}"]
        (temporary / "MAPA-DE-UPLOAD.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        save_json(temporary / "configuracoes.json", {
            "video_model": data["video_model"], "source_aspect_ratio": meta["aspect_ratio"],
            "source_duration_seconds": meta["duration_seconds"], "source_has_audio": meta["has_audio"],
            "audio_policy": data.get("audio_policy", "preservar_original"),
            "warnings": meta["warnings"]})
        save_json(temporary / "MANIFESTO.json", {"schema_version": 1, "created_at": utc_now(),
            "requested_change": data["requested_change"], "video_label": "@video1", "video_file": video_name,
            "video_included": include_video, "analysis": data["analysis"], "images": safe_images,
            "status": "manual_package_files_verified_agent_visual_review_recorded"})
        temporary.rename(out)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
    if make_zip:
        with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_DEFLATED) as z:
            for file in sorted(out.iterdir()):
                z.write(file, arcname=f"{out.name}/{file.name}")
    return {"output_directory": str(out), "zip": str(archive) if make_zip else None,
            "images": [item["name"] for item in checked["images"]],
            "note": "Disponibilize links reais das imagens, do prompt e do ZIP ao usuário."}

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("manifest", type=Path)
    p.add_argument("--out", type=Path)
    p.add_argument("--check-only", action="store_true")
    p.add_argument("--include-video", action="store_true")
    p.add_argument("--no-zip", action="store_true")
    a = p.parse_args()
    try:
        if a.check_only:
            data = validate_manifest(a.manifest)
            print(f"OK: {len(data['images'])} imagens finais, prompt e registros verificados.")
        else:
            if a.out is None:
                raise SkillError("Indique --out para montar o pacote.")
            print(json.dumps(package(a.manifest, a.out, include_video=a.include_video,
                                     make_zip=not a.no_zip), ensure_ascii=False, indent=2))
    except (SkillError, OSError, ValueError, TypeError, KeyError) as exc:
        p.exit(2, f"ERRO: {exc}\n")
if __name__ == "__main__":
    main()
