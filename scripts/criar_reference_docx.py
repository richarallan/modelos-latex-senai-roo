#!/usr/bin/env python3
"""Recria o reference.docx neutro usado pelo renderizador Pandoc."""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_BREAK
from docx.shared import Cm, Pt, RGBColor


RAIZ = Path(__file__).resolve().parents[1]
DESTINO = RAIZ / "templates" / "docx" / "reference.docx"

ESTILOS = {
    "Objetivo SENAI": "244A64",
    "Situacao-problema SENAI": "244A64",
    "Questao SENAI": "244A64",
    "Seguranca SENAI": "8A2E2E",
    "Rubrica SENAI": "2F6549",
    "Pratica SENAI": "2F6549",
    "Atencao SENAI": "8A2E2E",
}


def adicionar_estilo(documento: Document, nome: str, cor: str) -> None:
    estilos = documento.styles
    if nome in estilos:
        estilo = estilos[nome]
    else:
        estilo = estilos.add_style(nome, WD_STYLE_TYPE.PARAGRAPH)
    estilo.base_style = estilos["Normal"]
    estilo.font.name = "Arial"
    estilo.font.size = Pt(10.5)
    estilo.font.color.rgb = RGBColor.from_string(cor)
    estilo.paragraph_format.space_before = Pt(6)
    estilo.paragraph_format.space_after = Pt(6)
    estilo.paragraph_format.left_indent = Cm(0.35)


def main() -> int:
    documento = Document()
    secao = documento.sections[0]
    secao.top_margin = Cm(2.5)
    secao.bottom_margin = Cm(2.5)
    secao.left_margin = Cm(2.5)
    secao.right_margin = Cm(2.5)

    normal = documento.styles["Normal"]
    normal.font.name = "Arial"
    normal.font.size = Pt(11)
    normal.paragraph_format.space_after = Pt(6)

    for nome, cor in ESTILOS.items():
        adicionar_estilo(documento, nome, cor)

    # Um documento de referência precisa conter os estilos; o conteúdo é
    # descartado pelo Pandoc, mas a quebra garante um pacote DOCX válido.
    documento.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    documento.save(DESTINO)
    print(f"Reference DOCX criado em {DESTINO.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
