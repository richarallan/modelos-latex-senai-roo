#!/usr/bin/env python3
"""Gera LaTeX, PDF e DOCX a partir dos documentos Markdown do projeto."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


RAIZ = Path(__file__).resolve().parents[1]
DOCUMENTOS = RAIZ / "documentos"
SAIDA_PADRAO = RAIZ / "dist"
FILTRO = RAIZ / "filtros" / "bloco-senai.lua"
CABECALHO_LATEX = RAIZ / "templates" / "blocos-senai.tex"
FORMATOS = ("tex", "pdf", "docx")


def criar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Renderiza documentos Markdown em LaTeX, PDF e DOCX.",
    )
    parser.add_argument(
        "entradas",
        nargs="*",
        type=Path,
        help="Arquivos Markdown; por padrão, usa todos em documentos/.",
    )
    parser.add_argument(
        "--formato",
        choices=(*FORMATOS, "todos"),
        default="todos",
        help="Formato de saída (padrão: todos).",
    )
    parser.add_argument(
        "--saida",
        type=Path,
        default=SAIDA_PADRAO,
        help="Diretório de saída (padrão: dist/).",
    )
    parser.add_argument(
        "--pandoc",
        default="pandoc",
        help="Executável do Pandoc (padrão: pandoc).",
    )
    return parser


def resolver_entradas(informadas: list[Path]) -> list[Path]:
    if informadas:
        entradas = [
            caminho.resolve() if caminho.is_absolute() else (Path.cwd() / caminho).resolve()
            for caminho in informadas
        ]
    else:
        entradas = sorted(DOCUMENTOS.rglob("*.md"))

    if not entradas:
        raise ValueError("nenhum arquivo Markdown foi encontrado em documentos/")

    invalidas = [
        caminho
        for caminho in entradas
        if not caminho.is_file() or caminho.suffix.lower() != ".md"
    ]
    if invalidas:
        lista = ", ".join(str(caminho) for caminho in invalidas)
        raise ValueError(f"entradas inexistentes ou não Markdown: {lista}")

    return entradas


def caminho_relativo_da_saida(entrada: Path) -> Path:
    try:
        return entrada.relative_to(DOCUMENTOS)
    except ValueError:
        return Path(entrada.name)


def comando_base(pandoc: str, entrada: Path) -> list[str]:
    caminhos_de_recursos = os.pathsep.join(
        (str(entrada.parent), str(RAIZ), str(RAIZ / "templates"))
    )
    return [
        pandoc,
        str(entrada),
        "--from=markdown+fenced_divs",
        "--standalone",
        "--toc",
        "--number-sections",
        f"--lua-filter={FILTRO}",
        f"--resource-path={caminhos_de_recursos}",
        "--metadata=lang:pt-BR",
    ]


def comando_para_formato(
    pandoc: str,
    entrada: Path,
    formato: str,
    destino: Path,
) -> list[str]:
    comando = comando_base(pandoc, entrada)

    if formato in {"tex", "pdf"}:
        comando.append(f"--include-in-header={CABECALHO_LATEX}")

    if formato == "tex":
        comando.extend(("--to=latex", f"--output={destino}"))
    elif formato == "pdf":
        comando.extend(
            ("--to=pdf", "--pdf-engine=xelatex", f"--output={destino}")
        )
    elif formato == "docx":
        comando.extend(("--to=docx", f"--output={destino}"))
    else:
        raise ValueError(f"formato não suportado: {formato}")

    return comando


def renderizar(
    pandoc: str,
    entradas: list[Path],
    formatos: tuple[str, ...],
    diretorio_saida: Path,
) -> None:
    for entrada in entradas:
        relativa = caminho_relativo_da_saida(entrada)
        for formato in formatos:
            destino = (diretorio_saida / relativa).with_suffix(f".{formato}")
            destino.parent.mkdir(parents=True, exist_ok=True)
            comando = comando_para_formato(pandoc, entrada, formato, destino)
            print(f"[renderizar] {entrada.name} -> {destino.relative_to(RAIZ)}")
            subprocess.run(comando, cwd=RAIZ, check=True)


def main() -> int:
    args = criar_parser().parse_args()
    pandoc = shutil.which(args.pandoc)
    if pandoc is None:
        print(
            "Erro: Pandoc não encontrado. Instale o Pandoc ou informe "
            "--pandoc /caminho/para/pandoc.",
            file=sys.stderr,
        )
        return 2

    try:
        entradas = resolver_entradas(args.entradas)
        formatos = FORMATOS if args.formato == "todos" else (args.formato,)
        diretorio_saida = (
            args.saida.resolve()
            if args.saida.is_absolute()
            else (Path.cwd() / args.saida).resolve()
        )
        renderizar(pandoc, entradas, formatos, diretorio_saida)
    except (ValueError, subprocess.CalledProcessError) as erro:
        print(f"Erro: {erro}", file=sys.stderr)
        return 1

    print("[renderizar] concluído com sucesso")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
