from __future__ import annotations

import unittest
from pathlib import Path


RAIZ = Path(__file__).resolve().parents[1]


class EstruturaRepositorioTest(unittest.TestCase):
    def test_arquivos_essenciais_existem(self) -> None:
        essenciais = (
            "README.md",
            "CREDITS.md",
            "filtros/bloco-senai.lua",
            "scripts/renderizar.py",
            "templates/blocos-senai.tex",
            ".github/workflows/compilar-documentos.yml",
            ".github/workflows/verificar-ci.yml",
        )

        ausentes = [caminho for caminho in essenciais if not (RAIZ / caminho).is_file()]
        self.assertEqual(ausentes, [], f"arquivos essenciais ausentes: {ausentes}")

    def test_documentos_possuem_metadados_minimos(self) -> None:
        documentos = sorted((RAIZ / "documentos").rglob("*.md"))
        self.assertTrue(documentos, "nenhum documento Markdown encontrado")

        for documento in documentos:
            with self.subTest(documento=documento.relative_to(RAIZ)):
                conteudo = documento.read_text(encoding="utf-8")
                self.assertTrue(conteudo.startswith("---\n"))
                cabecalho = conteudo.split("---\n", 2)[1]
                for campo in ("title:", "author:", "lang:"):
                    self.assertIn(campo, cabecalho)


if __name__ == "__main__":
    unittest.main()
