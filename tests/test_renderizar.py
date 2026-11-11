from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from jsonschema import ValidationError

from scripts import renderizar


class RenderizadorTestes(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = renderizar.ler_schema()

    def test_exemplo_valido_atende_ao_schema(self) -> None:
        documento = renderizar.carregar_documento(
            renderizar.RAIZ / "exemplos" / "atividade-usinagem.md"
        )
        renderizar.validar_metadados(documento, self.schema)
        renderizar.validar_recursos(documento)

    def test_titulo_ausente_e_rejeitado(self) -> None:
        documento = renderizar.carregar_documento(
            renderizar.RAIZ / "exemplos" / "atividade-usinagem.md"
        )
        metadados = dict(documento.metadados)
        metadados.pop("titulo")
        invalido = renderizar.Documento(documento.caminho, metadados, documento.corpo)
        with self.assertRaisesRegex(renderizar.ErroDocumento, "titulo"):
            renderizar.validar_metadados(invalido, self.schema)

    def test_autor_aceita_texto_ou_lista_de_nomes(self) -> None:
        exemplo = renderizar.carregar_documento(
            renderizar.RAIZ / "exemplos" / "atividade-usinagem.md"
        )
        for autor in ("Richar Allan Macedo", ["Zélia & Silva", "Ana_Costa", "Érico Souza"]):
            with self.subTest(autor=autor):
                documento = renderizar.Documento(
                    exemplo.caminho, {**exemplo.metadados, "autor": autor}, exemplo.corpo
                )
                renderizar.validar_metadados(documento, self.schema)

    def test_autor_rejeita_lista_vazia_e_nomes_invalidos(self) -> None:
        exemplo = renderizar.carregar_documento(
            renderizar.RAIZ / "exemplos" / "atividade-usinagem.md"
        )
        for autor in ([], ["Ana", ""], ["Ana", "AB"], ["Ana", 12], 12, ""):
            with self.subTest(autor=autor):
                documento = renderizar.Documento(
                    exemplo.caminho, {**exemplo.metadados, "autor": autor}, exemplo.corpo
                )
                with self.assertRaisesRegex(renderizar.ErroDocumento, "autor"):
                    renderizar.validar_metadados(documento, self.schema)

    def test_metadados_author_preservam_texto_e_ordem_da_lista(self) -> None:
        exemplo = renderizar.carregar_documento(
            renderizar.RAIZ / "exemplos" / "atividade-usinagem.md"
        )
        autores = ["Zélia & Silva", "Ana_Costa", "Érico Souza"]
        for autor, nomes in (("Richar Allan Macedo", ["Richar Allan Macedo"]), (autores, autores)):
            for modelo in (None, "artigo"):
                with self.subTest(autor=autor, modelo=modelo):
                    metadados = {**exemplo.metadados, "autor": autor}
                    if modelo:
                        metadados["modelo"] = modelo
                    documento = renderizar.Documento(exemplo.caminho, metadados, exemplo.corpo)
                    argumentos = renderizar.metadados_pandoc(documento)
                    self.assertEqual(
                        [arg for arg in argumentos if arg.startswith("--metadata=author:")],
                        [f"--metadata=author:{nome}" for nome in nomes],
                    )

    def test_imagem_local_ausente_e_rejeitada(self) -> None:
        with tempfile.TemporaryDirectory() as temporario:
            caminho = Path(temporario) / "entrada.md"
            documento = renderizar.Documento(
                caminho=caminho,
                metadados={},
                corpo="![Evidência](imagens/ausente.png)",
            )
            with self.assertRaisesRegex(renderizar.ErroDocumento, "ausente.png"):
                renderizar.validar_recursos(documento)

    def test_lista_de_formatos_e_normalizada(self) -> None:
        self.assertEqual(
            renderizar.interpretar_formatos("pdf,docx,pdf"),
            ("pdf", "docx"),
        )
        with self.assertRaises(renderizar.ErroDocumento):
            renderizar.interpretar_formatos("odt")


if __name__ == "__main__":
    unittest.main()
