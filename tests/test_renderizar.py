from __future__ import annotations

import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock


RAIZ = Path(__file__).resolve().parents[1]
ESPECIFICACAO = importlib.util.spec_from_file_location(
    "renderizar",
    RAIZ / "scripts" / "renderizar.py",
)
assert ESPECIFICACAO is not None
assert ESPECIFICACAO.loader is not None
renderizar = importlib.util.module_from_spec(ESPECIFICACAO)
ESPECIFICACAO.loader.exec_module(renderizar)


class ResolverEntradasTest(unittest.TestCase):
    def test_descobre_apenas_markdown_em_ordem(self) -> None:
        with tempfile.TemporaryDirectory() as temporario:
            documentos = Path(temporario)
            (documentos / "b.md").write_text("# B\n", encoding="utf-8")
            (documentos / "a.md").write_text("# A\n", encoding="utf-8")
            (documentos / "ignorar.txt").write_text("texto\n", encoding="utf-8")

            with mock.patch.object(renderizar, "DOCUMENTOS", documentos):
                resultado = renderizar.resolver_entradas([])

        self.assertEqual([caminho.name for caminho in resultado], ["a.md", "b.md"])

    def test_rejeita_entrada_inexistente(self) -> None:
        with self.assertRaisesRegex(ValueError, "inexistentes ou não Markdown"):
            renderizar.resolver_entradas([Path("arquivo-inexistente.md")])

    def test_rejeita_diretorio_sem_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temporario:
            with mock.patch.object(renderizar, "DOCUMENTOS", Path(temporario)):
                with self.assertRaisesRegex(ValueError, "nenhum arquivo Markdown"):
                    renderizar.resolver_entradas([])


class ComandosPandocTest(unittest.TestCase):
    def setUp(self) -> None:
        self.entrada = renderizar.DOCUMENTOS / "apostila-exemplo.md"
        self.destino = renderizar.SAIDA_PADRAO / "apostila-exemplo"

    def test_comando_tex_inclui_cabecalho(self) -> None:
        comando = renderizar.comando_para_formato(
            "pandoc",
            self.entrada,
            "tex",
            self.destino.with_suffix(".tex"),
        )

        self.assertIn("--to=latex", comando)
        self.assertIn(f"--include-in-header={renderizar.CABECALHO_LATEX}", comando)

    def test_comando_pdf_usa_xelatex(self) -> None:
        comando = renderizar.comando_para_formato(
            "pandoc",
            self.entrada,
            "pdf",
            self.destino.with_suffix(".pdf"),
        )

        self.assertIn("--to=pdf", comando)
        self.assertIn("--pdf-engine=xelatex", comando)

    def test_comando_docx_nao_injeta_cabecalho_latex(self) -> None:
        comando = renderizar.comando_para_formato(
            "pandoc",
            self.entrada,
            "docx",
            self.destino.with_suffix(".docx"),
        )

        self.assertIn("--to=docx", comando)
        self.assertFalse(
            any(argumento.startswith("--include-in-header=") for argumento in comando)
        )

    def test_rejeita_formato_desconhecido(self) -> None:
        with self.assertRaisesRegex(ValueError, "formato não suportado"):
            renderizar.comando_para_formato(
                "pandoc",
                self.entrada,
                "html",
                self.destino.with_suffix(".html"),
            )

    def test_comando_base_ativa_filtro_e_divs(self) -> None:
        comando = renderizar.comando_base("pandoc", self.entrada)

        self.assertIn("--from=markdown+fenced_divs", comando)
        self.assertIn(f"--lua-filter={renderizar.FILTRO}", comando)
        self.assertIn("--metadata=lang:pt-BR", comando)


class RenderizacaoTest(unittest.TestCase):
    def test_preserva_subdiretorio_de_documentos(self) -> None:
        entrada = renderizar.DOCUMENTOS / "unidade" / "atividade.md"
        self.assertEqual(
            renderizar.caminho_relativo_da_saida(entrada),
            Path("unidade/atividade.md"),
        )

    def test_executa_um_comando_por_formato(self) -> None:
        entrada = renderizar.DOCUMENTOS / "apostila-exemplo.md"
        with tempfile.TemporaryDirectory(dir=renderizar.RAIZ) as temporario:
            saida = Path(temporario)
            with mock.patch.object(subprocess, "run") as executar:
                renderizar.renderizar("pandoc", [entrada], ("tex", "docx"), saida)

            self.assertEqual(executar.call_count, 2)
            for chamada in executar.call_args_list:
                self.assertEqual(chamada.kwargs["cwd"], renderizar.RAIZ)
                self.assertTrue(chamada.kwargs["check"])


if __name__ == "__main__":
    unittest.main()
