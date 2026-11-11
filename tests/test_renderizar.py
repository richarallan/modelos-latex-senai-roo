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
