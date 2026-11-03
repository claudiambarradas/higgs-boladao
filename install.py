#!/usr/bin/env python3
"""Instala somente os arquivos da skill; não autentica serviços nem instala dependências."""
from __future__ import annotations
import argparse
import shutil
from datetime import datetime
from pathlib import Path

NAME = "higgs-boladao"
ROOT_FILES = {"SKILL.md", "README.md", "COMECE-AQUI.md", "CHANGELOG.md", "TESTES.md",
              "requirements.txt", "install.py", ".gitignore", ".env.example", "VERSION"}
ROOT_DIRS = {"agents", "scripts", "references", "examples", "tests"}

def destinations(agent: str, scope: str, project: Path | None = None,
                 home: Path | None = None) -> list[Path]:
    base = (home or Path.home()) if scope == "user" else (project or Path.cwd())
    paths = []
    if agent in ("claude", "both"):
        paths.append(base / ".claude" / "skills" / NAME)
    if agent in ("codex", "both"):
        paths.append(base / ".agents" / "skills" / NAME)
    return paths

def copy_skill(source: Path, dest: Path, force: bool = False, dry_run: bool = False) -> str:
    source, dest = source.resolve(), dest.resolve()
    if source == dest:
        return f"Já está instalada em {dest}"
    if dest.is_relative_to(source):
        raise ValueError("Não instalar dentro da própria pasta da skill; escolha a raiz do projeto ou o escopo user.")
    if dest.exists() and not force:
        raise ValueError(f"Destino já existe: {dest}. Use --force somente após revisar; será criado backup fora da pasta skills.")
    if dry_run:
        return f"SIMULAÇÃO: copiar {source} → {dest} (nenhum arquivo alterado)"
    dest.parent.mkdir(parents=True, exist_ok=True)
    backup = None
    if dest.exists():
        # Backups fora de skills não são carregados como uma segunda skill.
        backup = dest.parent.parent / "skill-backups" / f"{NAME}-{datetime.now().strftime('%Y%m%d-%H%M%S-%f')}"
        backup.parent.mkdir(parents=True, exist_ok=True)
        dest.rename(backup)
    try:
        dest.mkdir()
        for child in source.iterdir():
            if child.name in ROOT_FILES and child.is_file() and not child.is_symlink():
                shutil.copy2(child, dest / child.name)
            elif child.name in ROOT_DIRS and child.is_dir() and not child.is_symlink():
                shutil.copytree(child, dest / child.name,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".env", "*.lock", "*.request-state.json", "*.higgs-state.json"))
        if not (dest / "SKILL.md").is_file():
            raise ValueError("SKILL.md ausente; instalação cancelada.")
    except Exception:
        shutil.rmtree(dest, ignore_errors=True)
        if backup is not None:
            backup.rename(dest)
        raise
    return f"Instalada: {dest}" + (f"\nBackup: {backup}" if backup else "")

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--agent", choices=["claude", "codex", "both"], required=True)
    p.add_argument("--scope", choices=["user", "project"], default="user")
    p.add_argument("--project", type=Path)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--force", action="store_true")
    a = p.parse_args()
    try:
        targets = destinations(a.agent, a.scope, a.project)
        source = Path(__file__).resolve().parent
        # Verificar ambos antes de começar para reduzir instalações parciais.
        for target in targets:
            copy_skill(source, target, a.force, dry_run=True)
        for target in targets:
            print(copy_skill(source, target, a.force, a.dry_run))
        print("Conexões e dependências são configuradas separadamente. Consulte COMECE-AQUI.md.")
    except (ValueError, OSError) as exc:
        p.exit(2, f"ERRO: {exc}\n")
if __name__ == "__main__":
    main()
