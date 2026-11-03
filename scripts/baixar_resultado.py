#!/usr/bin/env python3
"""Baixa um URL HTTPS realmente retornado pelo serviço; não envia credenciais."""
from __future__ import annotations
import argparse
import ipaddress
import socket
from pathlib import Path
from urllib.parse import urlparse, urljoin
import requests
from _common import SkillError, probe_video, save_json

def validate_url(url: str) -> None:
    parts = urlparse(url)
    if parts.scheme != "https" or not parts.hostname or parts.username or parts.password:
        raise SkillError("É necessário um URL HTTPS sem credenciais embutidas.")
    if parts.port not in (None, 443):
        raise SkillError("Somente HTTPS na porta padrão é aceito.")
    try:
        addresses = socket.getaddrinfo(parts.hostname, 443, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise SkillError("Não foi possível resolver o host do resultado.") from exc
    if not addresses or any(not ipaddress.ip_address(a[4][0]).is_global for a in addresses):
        raise SkillError("Download de endereço local/privado não permitido.")

def download(url: str, out: Path, max_mb: int = 1024) -> dict:
    if out.exists():
        raise SkillError("A saída já existe; escolha um novo arquivo.")
    if max_mb < 1:
        raise SkillError("Limite de download inválido.")
    out.parent.mkdir(parents=True, exist_ok=True)
    partial = out.with_suffix(out.suffix + ".part")
    if partial.exists():
        raise SkillError("Há download parcial; inspecione-o antes de tentar novamente.")
    response = None
    try:
        for _ in range(6):
            validate_url(url)
            response = requests.get(url, stream=True, allow_redirects=False, timeout=(30, 120))
            if response.status_code in (301, 302, 303, 307, 308):
                location = response.headers.get("Location")
                response.close()
                if not location:
                    raise SkillError("Redirecionamento sem destino.")
                url = urljoin(url, location)
                continue
            break
        else:
            raise SkillError("Excesso de redirecionamentos.")
        if response is None or response.status_code != 200:
            raise SkillError(f"Download falhou (HTTP {response.status_code if response else 'desconhecido'}). O link pode ter expirado.")
        limit = max_mb * 1024 * 1024
        total = 0
        with partial.open("xb") as stream:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                total += len(chunk)
                if total > limit:
                    raise SkillError("Resultado ultrapassa o limite autorizado de download.")
                stream.write(chunk)
        metadata = probe_video(partial)
        partial.rename(out)
        metadata["file"] = str(out.resolve())
        save_json(out.with_suffix(".metadata.json"), metadata)
        return metadata
    finally:
        if response is not None:
            response.close()
        partial.unlink(missing_ok=True)

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--url", required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--max-mb", type=int, default=1024)
    a = p.parse_args()
    try:
        meta = download(a.url, a.out, a.max_mb)
        print(f"Vídeo obtido: {a.out}; {meta['duration_seconds']:.3f}s. Ainda requer revisão visual/sonora.")
    except (SkillError, requests.RequestException, OSError, ValueError) as exc:
        p.exit(2, f"ERRO: {type(exc).__name__}: download não concluído. Verifique conexão, URL e metadados.\n")
if __name__ == "__main__":
    main()
