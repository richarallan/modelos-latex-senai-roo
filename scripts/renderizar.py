#!/usr/bin/env python3
"""Valida Markdown e gera TEX/PDF, com DOCX disponível para os modelos legados."""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse

import yaml
from jsonschema import Draft202012Validator


RAIZ = Path(__file__).resolve().parents[1]
FONTES_PADRAO = (RAIZ / "documentos", RAIZ / "exemplos")
SAIDA_PADRAO = RAIZ / "dist"
SCHEMA = RAIZ / "schemas" / "documento.schema.json"
FILTRO = RAIZ / "filtros" / "blocos-senai.lua"
CLASSES_LATEX = RAIZ / "templates" / "latex" / "classes"
REFERENCE_DOCX = RAIZ / "templates" / "docx" / "reference.docx"
TEMPLATE_ARTIGO = RAIZ / "templates" / "artigo" / "artigo.latex"
LOGO_ARTIGO = RAIZ / "templates" / "artigo" / "recursos" / "logo-senai.png"
FORMATOS = ("tex", "pdf", "docx")
PADRAO_IMAGEM = re.compile(r"!\[[^\]]*\]\((?P<destino>[^)\s]+)(?:\s+[^)]*)?\)")


@dataclass(frozen=True)
class Documento:
    caminho: Path
    metadados: dict[str, Any]
    corpo: str


class ErroDocumento(ValueError):
    """Erro de entrada com mensagem adequada para pessoas e para CI."""


def criar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Valida Markdown/YAML e gera LaTeX/PDF; DOCX é opcional nos modelos legados.",
    )
    parser.add_argument(
        "entradas",
        nargs="*",
        type=Path,
        help="Arquivos Markdown; sem argumentos, usa documentos/ e exemplos/.",
    )
    parser.add_argument(
        "--formato",
        default="tex,pdf",
        help="tex, pdf, docx, lista separada por vírgulas ou todos (padrão: tex,pdf).",
    )
    parser.add_argument(
        "--saida",
        type=Path,
        default=SAIDA_PADRAO,
        help="Diretório de saída (padrão: dist/).",
    )
    parser.add_argument(
        "--validar-apenas",
        action="store_true",
        help="Valida metadados e recursos sem executar o Pandoc.",
    )
    parser.add_argument(
        "--pandoc",
        default="pandoc",
        help="Executável do Pandoc (padrão: pandoc).",
    )
    return parser


def ler_schema() -> dict[str, Any]:
    import json

    with SCHEMA.open(encoding="utf-8") as arquivo:
        return json.load(arquivo)


def separar_front_matter(texto: str, caminho: Path) -> tuple[dict[str, Any], str]:
    normalizado = texto.replace("\r\n", "\n")
    if not normalizado.startswith("---\n"):
        raise ErroDocumento(f"{caminho}: cabeçalho YAML inicial não encontrado")
    partes = normalizado.split("\n---\n", 1)
    if len(partes) != 2:
        raise ErroDocumento(f"{caminho}: cabeçalho YAML não foi encerrado com ---")
    try:
        metadados = yaml.safe_load(partes[0][4:])
    except yaml.YAMLError as erro:
        raise ErroDocumento(f"{caminho}: YAML inválido: {erro}") from erro
    if not isinstance(metadados, dict):
        raise ErroDocumento(f"{caminho}: o cabeçalho YAML deve ser um objeto")
    return metadados, partes[1]


def carregar_documento(caminho: Path) -> Documento:
    metadados, corpo = separar_front_matter(caminho.read_text(encoding="utf-8"), caminho)
    return Documento(caminho=caminho, metadados=metadados, corpo=corpo)


def validar_metadados(documento: Documento, schema: dict[str, Any]) -> None:
    erros = sorted(
        Draft202012Validator(schema).iter_errors(documento.metadados),
        key=lambda erro: list(erro.absolute_path),
    )
    if not erros:
        return
    detalhes = []
    for erro in erros:
        campo = ".".join(str(item) for item in erro.absolute_path) or "metadados"
        detalhes.append(f"{campo}: {erro.message}")
    raise ErroDocumento(f"{documento.caminho}: " + "; ".join(detalhes))


def validar_recursos(documento: Documento) -> None:
    ausentes: list[str] = []
    for correspondencia in PADRAO_IMAGEM.finditer(documento.corpo):
        destino = correspondencia.group("destino").strip("<>")
        parsed = urlparse(destino)
        if parsed.scheme or destino.startswith("#"):
            continue
        recurso = (documento.caminho.parent / destino).resolve()
        if not recurso.is_file():
            ausentes.append(destino)
    if ausentes:
        raise ErroDocumento(
            f"{documento.caminho}: recurso(s) não encontrado(s): " + ", ".join(ausentes)
        )


def resolver_entradas(informadas: Iterable[Path]) -> list[Path]:
    lista = list(informadas)
    if lista:
        entradas = [
            caminho.resolve() if caminho.is_absolute() else (Path.cwd() / caminho).resolve()
            for caminho in lista
        ]
    else:
        entradas = sorted(
            caminho
            for diretorio in FONTES_PADRAO
            if diretorio.exists()
            for caminho in diretorio.rglob("*.md")
        )
    if not entradas:
        raise ErroDocumento("nenhum arquivo Markdown foi encontrado")
    invalidas = [
        caminho for caminho in entradas if not caminho.is_file() or caminho.suffix.lower() != ".md"
    ]
    if invalidas:
        raise ErroDocumento(
            "entradas inexistentes ou não Markdown: " + ", ".join(map(str, invalidas))
        )
    return entradas


def interpretar_formatos(valor: str) -> tuple[str, ...]:
    if valor.strip().lower() == "todos":
        return FORMATOS
    solicitados = tuple(dict.fromkeys(item.strip().lower() for item in valor.split(",") if item.strip()))
    invalidos = [item for item in solicitados if item not in FORMATOS]
    if not solicitados or invalidos:
        raise ErroDocumento(
            "formato inválido; use tex, pdf, docx, uma lista separada por vírgulas ou todos"
        )
    return solicitados


def caminho_relativo(entrada: Path) -> Path:
    for diretorio in FONTES_PADRAO:
        try:
            return Path(diretorio.name) / entrada.relative_to(diretorio)
        except ValueError:
            continue
    return Path(entrada.name)


def metadados_pandoc(documento: Documento) -> list[str]:
    metadados = documento.metadados
    mapeamento = {
        "title": metadados["titulo"],
        "author": metadados["autor"],
        "date": metadados.get("data", ""),
        "lang": metadados.get("idioma", "pt-BR"),
        "tipo-documento": metadados["tipo_documento"],
        "instituicao": metadados["instituicao"],
        "unidade-operacional": metadados["unidade_operacional"],
        "unidade-curricular": metadados["unidade_curricular"],
    }
    if metadados.get("subtitulo"):
        mapeamento["subtitle"] = metadados["subtitulo"]
    if metadados.get("modelo") == "artigo":
        mapeamento.update(
            {
                "curso": metadados.get("curso", metadados["unidade_curricular"]),
                "habilitacao": metadados.get("habilitacao", metadados["unidade_curricular"]),
                "local": metadados.get("local", metadados["unidade_operacional"]),
                "data-aprovacao": metadados.get("data_aprovacao", ""),
            }
        )
    argumentos: list[str] = []
    for chave, valor in mapeamento.items():
        argumentos.append(f"--metadata={chave}:{valor}")
    return argumentos


def exibir_caminho(caminho: Path) -> str:
    """Exibe caminhos locais sem impedir saídas e entradas fora do checkout."""
    try:
        return str(caminho.relative_to(RAIZ))
    except ValueError:
        return str(caminho)


def comando_pandoc(
    pandoc: str,
    documento: Documento,
    formato: str,
    destino: Path,
) -> list[str]:
    recursos = os.pathsep.join((str(documento.caminho.parent), str(RAIZ)))
    comando = [
        pandoc,
        str(documento.caminho),
        "--from=markdown+fenced_divs+fenced_code_attributes",
        "--standalone",
        "--number-sections",
        f"--lua-filter={FILTRO}",
        f"--resource-path={recursos}",
        *metadados_pandoc(documento),
    ]
    artigo = documento.metadados.get("modelo") == "artigo"
    if artigo and formato == "docx":
        raise ErroDocumento(
            "modelo artigo: a saída Word/DOCX ficará para uma próxima etapa; "
            "use --formato tex,pdf"
        )
    if not artigo:
        comando.append("--toc")
    elif formato in {"tex", "pdf"}:
        comando.append(f"--template={TEMPLATE_ARTIGO}")
        comando.append(f"--variable=logo-artigo:{LOGO_ARTIGO.as_posix()}")
        if documento.metadados.get("pre_textuais", True):
            comando.append("--variable=pre-textuais:true")
    if formato == "tex":
        comando.extend(("--to=latex", "--variable=documentclass:senaiarticle"))
    elif formato == "pdf":
        comando.extend(
            ("--to=pdf", "--pdf-engine=xelatex", "--variable=documentclass:senaiarticle")
        )
    elif formato == "docx":
        comando.extend(("--to=docx", f"--reference-doc={REFERENCE_DOCX}"))
    else:
        raise ErroDocumento(f"formato não suportado: {formato}")
    comando.append(f"--output={destino}")
    return comando


def ambiente_compilacao() -> dict[str, str]:
    ambiente = os.environ.copy()
    anterior = ambiente.get("TEXINPUTS", "")
    ambiente["TEXINPUTS"] = f"{CLASSES_LATEX}{os.pathsep}{anterior}"
    return ambiente


def validar_formatos(documentos: Iterable[Documento], formatos: tuple[str, ...]) -> None:
    if "docx" in formatos and any(doc.metadados.get("modelo") == "artigo" for doc in documentos):
        raise ErroDocumento(
            "modelo artigo: a saída Word/DOCX ficará para uma próxima etapa; "
            "use --formato tex,pdf (nenhum documento foi renderizado)"
        )


def renderizar(
    pandoc: str,
    documentos: Iterable[Documento],
    formatos: tuple[str, ...],
    diretorio_saida: Path,
) -> None:
    documentos = list(documentos)
    validar_formatos(documentos, formatos)
    if "docx" in formatos and not REFERENCE_DOCX.is_file():
        raise ErroDocumento(
            f"arquivo de referência DOCX não encontrado: {REFERENCE_DOCX.relative_to(RAIZ)}"
        )
    for documento in documentos:
        relativa = caminho_relativo(documento.caminho)
        for formato in formatos:
            destino = (diretorio_saida / relativa).with_suffix(f".{formato}")
            destino.parent.mkdir(parents=True, exist_ok=True)
            print(f"[renderizar] {documento.caminho.name} -> {exibir_caminho(destino)}")
            subprocess.run(
                comando_pandoc(pandoc, documento, formato, destino),
                cwd=RAIZ,
                env=ambiente_compilacao(),
                check=True,
            )


def main() -> int:
    args = criar_parser().parse_args()
    try:
        entradas = resolver_entradas(args.entradas)
        schema = ler_schema()
        documentos = [carregar_documento(caminho) for caminho in entradas]
        for documento in documentos:
            validar_metadados(documento, schema)
            validar_recursos(documento)
            print(f"[validar] {exibir_caminho(documento.caminho)}: OK")

        if args.validar_apenas:
            print("[validar] todos os documentos são válidos")
            return 0

        pandoc = shutil.which(args.pandoc)
        if pandoc is None:
            raise ErroDocumento(
                "Pandoc não encontrado; instale-o ou informe --pandoc /caminho/para/pandoc"
            )
        formatos = interpretar_formatos(args.formato)
        saida = args.saida.resolve() if args.saida.is_absolute() else (Path.cwd() / args.saida).resolve()
        renderizar(pandoc, documentos, formatos, saida)
    except (ErroDocumento, OSError, subprocess.CalledProcessError) as erro:
        print(f"Erro: {erro}", file=sys.stderr)
        return 1
    print("[renderizar] concluído com sucesso")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
