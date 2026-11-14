"""Localização dos contratos, interpretadores e recursos compartilhados."""
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
FONTES_PADRAO = (RAIZ / "documentos", RAIZ / "exemplos")
SAIDA_PADRAO = RAIZ / "dist"
SCHEMA = RAIZ / "schemas" / "documento.schema.json"
PERFIS = RAIZ / "perfis"
FILTRO_SEMANTICO = RAIZ / "filtros" / "semantica.lua"
FILTRO_APRESENTACAO = RAIZ / "filtros" / "apresentacao.lua"
ESTILO_CITACOES = RAIZ / "templates" / "bibliografia" / "abnt-autor-data.csl"
CLASSES_LATEX = RAIZ / "templates" / "latex" / "classes"
REFERENCE_DOCX = RAIZ / "templates" / "docx" / "reference.docx"
TEMPLATE_ARTIGO = RAIZ / "templates" / "artigo" / "artigo.latex"
LOGO_ARTIGO = RAIZ / "templates" / "artigo" / "recursos" / "logo-senai.png"
