"""Perfis declarativos selecionam apresentação, sem reinterpretar o conteúdo."""
from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path
from jsonschema import Draft202012Validator

from .caminhos import PERFIS, RAIZ
from .documento import Documento, ErroDocumento


@dataclass(frozen=True)
class Perfil:
    id: str
    tipos_documentais: tuple[str, ...]
    template: Path | None
    classe: str
    opcoes_classe: tuple[str, ...]
    formatos: tuple[str, ...]
    sumario: bool
    pre_textuais: bool
    recursos: dict[str, Path]


def carregar_perfil(documento: Documento) -> Perfil:
    identificador = documento.metadados.get("modelo", documento.metadados.get("tipo_documento"))
    if not isinstance(identificador, str) or not identificador.replace("_", "").isalnum():
        raise ErroDocumento(f"{documento.caminho}: modelo inválido: {identificador!r}")
    caminho = PERFIS / f"{identificador}.json"
    if not caminho.is_file():
        raise ErroDocumento(f"{documento.caminho}: perfil documental não encontrado: {identificador}")
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
        schema = json.loads((RAIZ / "schemas" / "perfil.schema.json").read_text(encoding="utf-8"))
        erros = list(Draft202012Validator(schema).iter_errors(dados))
        if erros:
            raise ValueError("; ".join(f"{'.'.join(map(str, erro.path)) or 'perfil'}: {erro.message}" for erro in erros))
        if dados["versao"] != 1 or dados["id"] != identificador:
            raise ValueError("versão ou identificador incompatível")
        template = (RAIZ / dados["template"]).resolve() if dados["template"] else None
        if template and (not template.is_relative_to(RAIZ) or not template.is_file()):
            raise ValueError("template inexistente ou fora do repositório")
        recursos = {chave: (RAIZ / valor).resolve() for chave, valor in dados.get("recursos", {}).items()}
        for chave, recurso in recursos.items():
            if not recurso.is_relative_to(RAIZ) or not recurso.is_file():
                raise ValueError(f"recurso {chave} inexistente ou fora do repositório: {recurso}")
        perfil = Perfil(identificador, tuple(dados["tipos_documentais"]), template,
                        dados["classe"], tuple(dados["opcoes_classe"]),
                        tuple(dados["formatos"]), dados["sumario"], dados["pre_textuais"], recursos)
    except (ValueError, KeyError, TypeError) as erro:
        raise ErroDocumento(f"{caminho}: perfil inválido: {erro}") from erro
    if documento.metadados.get("tipo_documento") not in perfil.tipos_documentais:
        raise ErroDocumento(f"{documento.caminho}: tipo_documento não permitido pelo perfil {perfil.id}")
    return perfil
