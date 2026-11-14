"""Leitura, normalização e validação da fonte documental."""
from __future__ import annotations
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable
import yaml
from jsonschema import Draft202012Validator
from .caminhos import RAIZ, SCHEMA, FONTES_PADRAO
PADRAO_ID_REFERENCIA = re.compile(r'[A-Za-z0-9][A-Za-z0-9_.:-]*\Z')
@dataclass(frozen=True)
class Documento:
    caminho: Path
    metadados: dict[str, Any]
    corpo: str


class ErroDocumento(ValueError):
    """Erro de entrada com mensagem adequada para pessoas e para CI."""


def normalizar_documento(documento: Documento) -> Documento:
    """Omissão explícita de campos opcionais sem conteúdo, sem criar valores."""
    schema = ler_schema()
    obrigatorios = set(schema["required"])
    conhecidos = set(schema["properties"])
    metadados = {}
    for chave, valor in documento.metadados.items():
        contrato = schema["properties"].get(chave, {})
        alternativas = contrato.get("oneOf", [contrato])
        tipos = {item.get("type") for item in alternativas}
        if chave not in obrigatorios and chave in conhecidos:
            if valor is None:
                continue
            if isinstance(valor, str) and not valor.strip() and "string" in tipos:
                continue
            if valor == [] and "array" in tipos:
                continue
        metadados[chave] = valor
    return Documento(documento.caminho, metadados, documento.corpo)


class _YamlUnico(yaml.SafeLoader):
    """Não aceita perda silenciosa de campos repetidos no cabeçalho."""


def _mapa_unico(loader: _YamlUnico, node: yaml.MappingNode) -> dict:
    pares = loader.construct_pairs(node)
    resultado = {}
    for chave, valor in pares:
        if not isinstance(chave, str):
            raise ErroDocumento("YAML: as chaves devem ser texto")
        if chave in resultado:
            raise ErroDocumento(f"YAML: campo duplicado: {chave}")
        resultado[chave] = valor
    return resultado


_YamlUnico.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _mapa_unico)


def ler_schema() -> dict[str, Any]:
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
        metadados = yaml.load(partes[0][4:], Loader=_YamlUnico)
    except ErroDocumento as erro:
        raise ErroDocumento(f"{caminho}: {erro}") from erro
    except yaml.YAMLError as erro:
        raise ErroDocumento(f"{caminho}: YAML inválido: {erro}") from erro
    if not isinstance(metadados, dict):
        raise ErroDocumento(f"{caminho}: o cabeçalho YAML deve ser um objeto")
    return metadados, partes[1]


def carregar_documento(caminho: Path) -> Documento:
    metadados, corpo = separar_front_matter(caminho.read_text(encoding="utf-8"), caminho)
    return normalizar_documento(Documento(caminho=caminho, metadados=metadados, corpo=corpo))


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
    # A mesma leitura de AST cobre imagens comuns, por referência e arquivo=.
    from .geracao import interpretar_ast
    interpretar_ast("pandoc", normalizar_documento(documento))


def caminhos_bibliografia(documento: Documento) -> list[Path]:
    informados = documento.metadados.get("bibliografia", [])
    if isinstance(informados, str):
        informados = [informados]
    return [(documento.caminho.parent / caminho).resolve() for caminho in informados]


def validar_bibliografia(documento: Documento) -> list[str]:
    """Valida o subconjunto CSL-YAML/JSON e a unicidade das chaves entre arquivos."""
    identificadores: set[str] = set()
    for caminho in caminhos_bibliografia(documento):
        if not caminho.is_file():
            raise ErroDocumento(f"{documento.caminho}: bibliografia não encontrada: {caminho}")
        if caminho.suffix.lower() not in {".yaml", ".yml", ".json"}:
            raise ErroDocumento(f"{caminho}: use bibliografia estruturada CSL-YAML ou CSL-JSON")
        try:
            texto = caminho.read_text(encoding="utf-8")
            dados = json.loads(texto) if caminho.suffix.lower() == ".json" else yaml.safe_load(texto)
        except (yaml.YAMLError, json.JSONDecodeError) as erro:
            raise ErroDocumento(f"{caminho}: bibliografia inválida: {erro}") from erro
        if caminho.suffix.lower() == ".json":
            referencias = dados
        else:
            referencias = dados.get("references") if isinstance(dados, dict) else None
        if not isinstance(referencias, list) or not referencias:
            raise ErroDocumento(f"{caminho}: a bibliografia deve conter uma lista não vazia de references")
        for referencia in referencias:
            if not isinstance(referencia, dict):
                raise ErroDocumento(f"{caminho}: cada referência deve ser um objeto CSL")
            identificador = referencia.get("id")
            if not isinstance(identificador, str) or not PADRAO_ID_REFERENCIA.fullmatch(identificador):
                raise ErroDocumento(f"{caminho}: referência com id ausente ou inválido")
            if identificador.startswith(("fig:", "gra:", "tab:", "eq:")):
                raise ErroDocumento(f"{caminho}: id bibliográfico reservado para objeto: {identificador}")
            if identificador in identificadores:
                raise ErroDocumento(f"{caminho}: id bibliográfico duplicado: {identificador}")
            identificadores.add(identificador)
            if not isinstance(referencia.get("title"), str) or not referencia["title"].strip():
                raise ErroDocumento(f"{caminho}: referência {identificador} sem title")
            if not isinstance(referencia.get("type"), str) or not referencia["type"].strip():
                raise ErroDocumento(f"{caminho}: referência {identificador} sem type CSL")
    return sorted(identificadores)


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


def caminho_relativo(entrada: Path) -> Path:
    for diretorio in FONTES_PADRAO:
        try:
            return Path(diretorio.name) / entrada.relative_to(diretorio)
        except ValueError:
            continue
    return Path(entrada.name)


def exibir_caminho(caminho: Path) -> str:
    """Exibe caminhos locais sem impedir saídas e entradas fora do checkout."""
    try:
        return str(caminho.relative_to(RAIZ))
    except ValueError:
        return str(caminho)
