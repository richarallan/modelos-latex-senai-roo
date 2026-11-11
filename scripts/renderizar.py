#!/usr/bin/env python3
"""CLI e fachada compatível do núcleo documental compartilhado."""
from __future__ import annotations
import argparse
import shutil
import sys
from pathlib import Path

# Permite executar este arquivo diretamente a partir de qualquer diretório.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from nucleo.caminhos import *
from nucleo.documento import *
from nucleo.geracao import *

# Nomes anteriores mantidos para consumidores e testes de regressão.
FILTRO = FILTRO_APRESENTACAO
FILTRO_REFERENCIAS = FILTRO_SEMANTICO


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
        help="Valida metadados, recursos, citações e referências com Pandoc, sem gerar arquivos.",
    )
    parser.add_argument(
        "--pandoc",
        default="pandoc",
        help="Executável do Pandoc (padrão: pandoc).",
    )
    return parser



def main() -> int:
    args = criar_parser().parse_args()
    try:
        entradas = resolver_entradas(args.entradas)
        documentos = [carregar_documento(caminho) for caminho in entradas]
        pandoc = shutil.which(args.pandoc)
        if pandoc is None:
            raise ErroDocumento("Pandoc não encontrado; instale-o ou informe --pandoc /caminho/para/pandoc")
        if args.validar_apenas:
            validar_documentos(pandoc, documentos)
            for doc in documentos:
                print(f"[validar] {exibir_caminho(doc.caminho)}: OK")
            print("[validar] metadados, recursos, citações e referências são válidos")
            return 0
        formatos = interpretar_formatos(args.formato)
        saida = args.saida.resolve()
        renderizar(pandoc, documentos, formatos, saida)
    except (ErroDocumento, OSError) as erro:
        print(f"Erro: {erro}", file=sys.stderr)
        return 1
    print("[renderizar] concluído com sucesso")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
