#!/usr/bin/env python3
"""Valida @video1 e @imagem1..N; não corrige referências silenciosamente."""
from __future__ import annotations
import argparse
import re
from pathlib import Path

VALID = re.compile(r"@(video1|imagem[1-9][0-9]*)(?![\w\-])", re.UNICODE)
PLACEHOLDER = re.compile(r"\{\{.*?\}\}|\[(?:INSIRA|PREENCHA|COLOQUE|TODO)\b.*?\]|<[^>]*(?:AQUI|INSIRA|PREENCHA)[^>]*>", re.I)

def validate_prompt(text: str, images: int, max_chars: int | None = None) -> list[str]:
    errors: list[str] = []
    if images < 1:
        errors.append("É necessária pelo menos uma imagem final editada.")
    if not text.strip():
        errors.append("O prompt está vazio.")
    labels = []
    for match in re.finditer("@", text):
        valid = VALID.match(text, match.start())
        if valid is None:
            errors.append(f"Referência inválida perto de {text[match.start():match.start()+24]!r}; use @video1 ou @imagemN, com N numérico, sem espaço.")
        else:
            labels.append(valid.group(0))
    expected = {"@video1"} | {f"@imagem{i}" for i in range(1, max(images, 0) + 1)}
    actual = set(labels)
    for missing in sorted(expected - actual):
        errors.append(f"Referência ausente: {missing}.")
    for extra in sorted(actual - expected):
        errors.append(f"Referência sem arquivo correspondente: {extra}.")
    if PLACEHOLDER.search(text):
        errors.append("Há um campo para preencher no prompt final.")
    if max_chars is not None and len(text) > max_chars:
        errors.append(f"O prompt tem {len(text)} caracteres; limite informado: {max_chars}.")
    return errors

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("prompt", type=Path)
    p.add_argument("--images", required=True, type=int)
    p.add_argument("--max-chars", type=int)
    a = p.parse_args()
    try:
        text = a.prompt.read_text(encoding="utf-8-sig")
        errors = validate_prompt(text, a.images, a.max_chars)
        if errors:
            p.exit(2, "\n".join("ERRO: " + e for e in errors) + "\n")
        print(f"OK: @video1 e {a.images} imagens; {len(text)} caracteres. A existência e o conteúdo das imagens são verificados pelo empacotador e pelo agente.")
    except OSError as exc:
        p.exit(2, f"ERRO: {exc}\n")
if __name__ == "__main__":
    main()
