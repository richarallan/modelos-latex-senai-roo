"""Markdown → representação semântica única → apresentação → Pandoc/XeLaTeX.

Os perfis não interpretam elementos. TEX, PDF e DOCX recebem o mesmo AST JSON.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path
from typing import Iterable

import yaml

from .caminhos import (
    RAIZ, FILTRO_SEMANTICO, FILTRO_APRESENTACAO, ESTILO_CITACOES,
    CLASSES_LATEX, REFERENCE_DOCX,
)
from .documento import (
    Documento, ErroDocumento, normalizar_documento, validar_metadados,
    validar_bibliografia, caminhos_bibliografia, ler_schema,
    caminho_relativo, exibir_caminho,
)
from .perfis import carregar_perfil

FORMATOS = ("tex", "pdf", "docx")
IDIOMAS_BABEL = {"pt-BR": "brazilian", "en": "english", "es": "spanish"}


def interpretar_formatos(valor: str) -> tuple[str, ...]:
    if valor.strip().lower() == "todos":
        return FORMATOS
    solicitados = tuple(dict.fromkeys(item.strip().lower() for item in valor.split(",") if item.strip()))
    if not solicitados or any(item not in FORMATOS for item in solicitados):
        raise ErroDocumento("formato inválido; use tex, pdf, docx, uma lista separada por vírgulas ou todos")
    return solicitados


def metadados_pandoc(documento: Documento) -> list[str]:
    meta = documento.metadados
    nomes = {
        "titulo": "title", "subtitulo": "subtitle", "autor": "author", "data": "date",
        "idioma": "lang", "tipo_documento": "tipo-documento",
        "instituicao": "instituicao", "unidade_operacional": "unidade-operacional",
        "unidade_curricular": "unidade-curricular", "local": "local",
        "data_aprovacao": "data-aprovacao",
    }
    valores = {destino: meta[origem] for origem, destino in nomes.items() if origem in meta}
    valores.setdefault("lang", "pt-BR")
    # Curso/habilitação compartilham o contexto informado, sem completar pessoas.
    for campo in ("curso", "habilitacao"):
        if meta.get(campo, meta.get("unidade_curricular")):
            valores[campo] = meta.get(campo, meta.get("unidade_curricular"))
    return [f"--metadata={chave}:{item}" for chave, valor in valores.items()
            for item in (valor if isinstance(valor, list) else [valor])]


def _recursos(documento: Documento) -> str:
    return os.pathsep.join((str(documento.caminho.resolve().parent), str(RAIZ)))


def _bibliografias(documento: Documento) -> list[str]:
    caminhos = caminhos_bibliografia(documento)
    if not caminhos:
        return []
    return [f"--csl={ESTILO_CITACOES}", *[f"--bibliography={p}" for p in caminhos]]


def _executar(comando: list[str], documento: Documento, entrada: str | None = None) -> str:
    try:
        resultado = subprocess.run(comando, input=entrada, capture_output=True, text=True,
                                   cwd=RAIZ, env=ambiente_compilacao(), check=True)
    except subprocess.CalledProcessError as erro:
        detalhes = (erro.stderr or erro.stdout or str(erro)).strip()
        raise ErroDocumento(f"{documento.caminho}: {detalhes}") from erro
    if resultado.stderr.strip():
        # Os avisos não fatais da engine continuam visíveis; Pandoc warnings são fatais.
        import sys
        print(resultado.stderr, end="", file=sys.stderr)
    return resultado.stdout


def interpretar_ast(pandoc: str, documento: Documento) -> dict:
    """Lê/valida os elementos uma vez, preservando o Markdown nativo na AST."""
    ids = validar_bibliografia(documento)
    meta = {**documento.metadados,
            "senai-diretorio-fonte": str(documento.caminho.resolve().parent),
            "senai-bibliografia-ids": ids,
            "senai-validar-citacoes": True}
    fonte = "---\n" + yaml.safe_dump(meta, allow_unicode=True, sort_keys=False) + "---\n" + documento.corpo
    comando = [pandoc, "--from=markdown+fenced_divs+fenced_code_attributes", "--to=json",
               "--fail-if-warnings", f"--lua-filter={FILTRO_SEMANTICO}",
               f"--resource-path={_recursos(documento)}", *metadados_pandoc(documento),
               *_bibliografias(documento)]
    return json.loads(_executar(comando, documento, fonte))


def interpretar_documento(pandoc: str, documento: Documento) -> dict:
    documento = normalizar_documento(documento)
    validar_metadados(documento, ler_schema())
    carregar_perfil(documento)
    return interpretar_ast(pandoc, documento)


def _apresentacao(documento: Documento, formato: str, tem_titulos: bool) -> list[str]:
    perfil = carregar_perfil(documento)
    if formato not in perfil.formatos:
        raise ErroDocumento(f"modelo {perfil.id}: a saída Word/DOCX ficará para uma próxima etapa; use --formato tex,pdf")
    comando = ["--standalone", "--number-sections", "--fail-if-warnings", "--citeproc",
               "--metadata=link-citations:true", "--metadata=reference-section-title:Referências",
               f"--resource-path={_recursos(documento)}", *_bibliografias(documento)]
    if documento.metadados.get("sumario", perfil.sumario) and tem_titulos:
        comando.append("--toc")
    if perfil.template and formato in {"tex", "pdf"}:
        comando.extend([f"--template={perfil.template}",
                        f"--variable=babel-lang:{IDIOMAS_BABEL[documento.metadados.get('idioma', 'pt-BR')]}"])
        comando.extend(f"--variable={chave}:{valor.as_posix()}" for chave, valor in perfil.recursos.items())
    if perfil.pre_textuais and documento.metadados.get("pre_textuais", True):
        comando.append("--variable=pre-textuais:true")
        for campo in ("capa", "folha_rosto"):
            if documento.metadados.get(campo, True):
                comando.append(f"--variable=mostrar-{campo.replace('_', '-')}:true")
        if documento.metadados.get("aprovacao", True) and any(
            documento.metadados.get(campo) for campo in ("coordenacao", "banca", "data_aprovacao")
        ):
            comando.append("--variable=mostrar-aprovacao:true")
    if formato in {"tex", "pdf"}:
        comando.append(f"--variable=documentclass:{perfil.classe}")
        comando.extend(f"--variable=classoption:{opcao}" for opcao in perfil.opcoes_classe)
        comando.append("--to=latex" if formato == "tex" else "--to=pdf")
        if formato == "pdf":
            comando.append("--pdf-engine=xelatex")
    else:
        comando.extend(["--to=docx", f"--reference-doc={REFERENCE_DOCX}"])
    return comando


def comando_pandoc(pandoc: str, documento: Documento, formato: str, destino: Path) -> list[str]:
    """Fachada compatível para consumidores anteriores; usa os filtros comuns."""
    documento = normalizar_documento(documento)
    return [pandoc, str(documento.caminho), "--from=markdown+fenced_divs+fenced_code_attributes",
            f"--lua-filter={FILTRO_SEMANTICO}", f"--lua-filter={FILTRO_APRESENTACAO}",
            f"--metadata=senai-diretorio-fonte:{documento.caminho.resolve().parent}",
            *metadados_pandoc(documento),
            *_apresentacao(documento, formato, bool(re.search(r"^#{1,6}\s", documento.corpo, re.M))),
            f"--output={destino}"]


def ambiente_compilacao() -> dict[str, str]:
    ambiente = os.environ.copy()
    ambiente["TEXINPUTS"] = f"{CLASSES_LATEX}{os.pathsep}{ambiente.get('TEXINPUTS', '')}"
    return ambiente


def validar_formatos(documentos: Iterable[Documento], formatos: tuple[str, ...]) -> None:
    for documento in documentos:
        perfil = carregar_perfil(documento)
        if any(formato not in perfil.formatos for formato in formatos):
            raise ErroDocumento(f"modelo {perfil.id}: a saída Word/DOCX ficará para uma próxima etapa; "
                                "use --formato tex,pdf (nenhum documento foi renderizado)")


def _tem_titulos(valor: object) -> bool:
    if isinstance(valor, dict):
        return valor.get("t") == "Header" or any(_tem_titulos(v) for v in valor.values())
    return isinstance(valor, list) and any(_tem_titulos(v) for v in valor)


def _gerar_ir(pandoc: str, documento: Documento, ir: dict, formato: str, destino: Path) -> None:
    _executar([pandoc, "--from=json", f"--lua-filter={FILTRO_APRESENTACAO}",
               *_apresentacao(documento, formato, _tem_titulos(ir["blocks"])),
               f"--output={destino}"], documento, json.dumps(ir, ensure_ascii=False))


def validar_documentos(pandoc: str, documentos: Iterable[Documento]) -> None:
    for fonte in documentos:
        documento = normalizar_documento(fonte)
        ir = interpretar_documento(pandoc, documento)
        _gerar_ir(pandoc, documento, ir, "tex", Path(os.devnull))


def renderizar(pandoc: str, documentos: Iterable[Documento], formatos: tuple[str, ...], diretorio_saida: Path) -> None:
    documentos = [normalizar_documento(doc) for doc in documentos]
    validar_formatos(documentos, formatos)
    if "docx" in formatos and not REFERENCE_DOCX.is_file():
        raise ErroDocumento(f"arquivo de referência DOCX não encontrado: {REFERENCE_DOCX.relative_to(RAIZ)}")
    # O lote inteiro é interpretado antes de gravar qualquer documento de saída.
    interpretados = [(doc, interpretar_documento(pandoc, doc)) for doc in documentos]
    destinos = [(doc, ir, formato, (diretorio_saida / caminho_relativo(doc.caminho)).with_suffix(f".{formato}"))
                for doc, ir in interpretados for formato in formatos]
    caminhos = [destino for _, _, _, destino in destinos]
    if len(set(caminhos)) != len(caminhos):
        raise ErroDocumento("entradas produzem o mesmo destino; renomeie os arquivos de origem")
    for documento, ir, formato, destino in destinos:
        destino.parent.mkdir(parents=True, exist_ok=True)
        print(f"[renderizar] {documento.caminho.name} -> {exibir_caminho(destino)}")
        _gerar_ir(pandoc, documento, ir, formato, destino)
