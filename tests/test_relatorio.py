"""Contrato e composição do relatório sobre o núcleo documental comum."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import unittest
import xml.etree.ElementTree as ET
from dataclasses import replace
from typing import Any
from unittest.mock import patch

from scripts import renderizar
from nucleo.perfis import carregar_perfil
import test_nucleo as apoio


PDF_DISPONIVEL = all(shutil.which(item) for item in ("pandoc", "xelatex", "pdftotext", "pdfinfo"))


@unittest.skipUnless(shutil.which("pandoc"), "Pandoc necessário para testar o relatório")
class ModeloRelatorioTestes(unittest.TestCase):
    # Composição de fixtures, sem herdar e repetir os testes do núcleo.
    setUp = apoio.NucleoDocumentalTestes.setUp
    documento = apoio.NucleoDocumentalTestes.documento
    escrever = apoio.NucleoDocumentalTestes.escrever
    executar = apoio.NucleoDocumentalTestes.executar
    interpretar = apoio.NucleoDocumentalTestes.interpretar
    figura = staticmethod(apoio.NucleoDocumentalTestes.figura)

    @classmethod
    def setUpClass(cls) -> None:
        apoio.NucleoDocumentalTestes.setUpClass.__func__(cls)
        cls.base = {**cls.base, "modelo": "relatorio"}

    def gerar(self, corpo: str, formato: str = "tex", **metadados: Any) -> str:
        entrada = self.escrever(corpo, **metadados)
        resultado = self.executar(entrada, formato)
        self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)
        tex = self.pasta / "saida" / "entrada.tex"
        return tex.read_text(encoding="utf-8") if tex.exists() else ""

    def paginas(self) -> list[str]:
        texto = subprocess.check_output(
            ["pdftotext", "-layout", str(self.pasta / "saida" / "entrada.pdf"), "-"],
            text=True, timeout=30,
        )
        paginas = texto.split("\f")
        if not paginas[-1].strip():
            paginas.pop()
        return paginas

    def palavras_da_capa(self) -> tuple[float, float, list[dict[str, Any]]]:
        xml = subprocess.check_output(
            ["pdftotext", "-f", "1", "-l", "1", "-bbox",
             str(self.pasta / "saida" / "entrada.pdf"), "-"],
            text=True, timeout=30,
        )
        ns = {"x": "http://www.w3.org/1999/xhtml"}
        pagina = ET.fromstring(xml).find(".//x:page", ns)
        self.assertIsNotNone(pagina)
        palavras = [{**no.attrib, "texto": no.text or ""}
                    for no in pagina.findall(".//x:word", ns)]
        return float(pagina.attrib["width"]), float(pagina.attrib["height"]), palavras

    def test_perfil_relatorio_preserva_obrigatorios_tipos_e_formatos(self) -> None:
        schema = renderizar.ler_schema()
        for tipo in ("nota_aula", "atividade_avaliativa"):
            documento = self.documento("Conteúdo.\n", tipo_documento=tipo)
            renderizar.validar_metadados(documento, schema)
            perfil = carregar_perfil(documento)
            self.assertEqual(perfil.id, "relatorio")
            self.assertEqual(perfil.opcoes_classe, ("relatorio",))
            self.assertEqual(set(perfil.formatos), {"tex", "pdf"})
            self.assertTrue(perfil.sumario)
            self.assertTrue(perfil.pre_textuais)
        for campo in schema["required"]:
            with self.subTest(campo=campo):
                metadados = dict(self.base)
                metadados.pop(campo)
                with self.assertRaisesRegex(renderizar.ErroDocumento, campo):
                    renderizar.validar_metadados(
                        renderizar.Documento(self.pasta / "entrada.md", metadados, "Conteúdo."), schema
                    )
        with self.assertRaisesRegex(renderizar.ErroDocumento, "relatorio"):
            renderizar.validar_formatos([self.documento("Conteúdo.")], ("docx",))

    def test_campos_do_relatorio_validam_tipos_e_omitem_vazios(self) -> None:
        for campo in ("natureza", "tipo_trabalho"):
            for valor in (12, [], {"texto": "Conteúdo"}):
                with self.subTest(campo=campo, valor=valor):
                    resultado = self.executar(self.escrever("Conteúdo.\n", **{campo: valor}), validar=True)
                    self.assertNotEqual(resultado.returncode, 0)
                    self.assertIn(campo, resultado.stderr)
            for valor in (None, "", " \t "):
                documento = renderizar.carregar_documento(self.escrever("Conteúdo.\n", **{campo: valor}))
                self.assertNotIn(campo, documento.metadados)
        entrada = self.escrever("Conteúdo.\n", natureza="Relatório didático com dados simulados.",
                                tipo_trabalho="RELATÓRIO DE ESTUDO")
        resultado = self.executar(entrada, validar=True)
        self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)

    def test_capacidades_do_perfil_controlam_as_paginas_pre_textuais(self) -> None:
        documento = self.documento("# Registro\n\nConteúdo.\n", pre_textuais=True,
                                   banca=["Equipe de avaliação"], coordenacao="Equipe de coordenação")
        perfil = replace(carregar_perfil(documento), paginas_pre_textuais=("capa",))
        with patch("nucleo.geracao.carregar_perfil", return_value=perfil):
            comando = renderizar.comando_pandoc("pandoc", documento, "tex", self.pasta / "saida.tex")
        self.assertIn("--variable=mostrar-capa:true", comando)
        self.assertNotIn("--variable=mostrar-folha-rosto:true", comando)
        self.assertNotIn("--variable=mostrar-aprovacao:true", comando)
        dados = json.loads((renderizar.RAIZ / "perfis" / "relatorio.json").read_text(encoding="utf-8"))
        dados["paginas_pre_textuais"] = []
        (self.pasta / "relatorio.json").write_text(json.dumps(dados), encoding="utf-8")
        with patch("nucleo.perfis.PERFIS", self.pasta):
            with self.assertRaisesRegex(renderizar.ErroDocumento, "paginas_pre_textuais"):
                carregar_perfil(documento)

    def test_pre_textuais_usam_apenas_os_campos_fornecidos(self) -> None:
        tex = self.gerar("# Registro\n\nConteúdo.\n", sumario=False,
                         natureza="Descrição de finalidade fornecida no Markdown.",
                         tipo_trabalho="RELATÓRIO DE ESTUDO", local=None, data=None)
        self.assertIn(r"\documentclass[relatorio]{senaiarticle}", tex)
        self.assertIn("RELATÓRIO DE ESTUDO", tex)
        self.assertIn("Descrição de finalidade fornecida no Markdown.", tex)
        self.assertEqual(len(re.findall(r"\\begin\{titlepage\}", tex)), 2)
        for ausente in ("Artigo científico apresentado", "TERMO DE APROVAÇÃO", "Orientador(a):",
                        "Coordenação pedagógica:", "BANCA EXAMINADORA", "Resultado final:"):
            self.assertNotIn(ausente, tex)
        tex = self.gerar("# Registro\n\nConteúdo.\n", sumario=False,
                         coordenacao="Equipe de coordenação", banca=["Equipe de avaliação"],
                         orientador="Equipe de orientação", data_aprovacao="13 de novembro de 2026")
        self.assertEqual(len(re.findall(r"\\begin\{titlepage\}", tex)), 3)
        for fornecido in ("Equipe de coordenação", "Equipe de avaliação", "Equipe de orientação",
                          "13 de novembro de 2026"):
            self.assertIn(fornecido, tex)

    @staticmethod
    def objeto(prefixo: str, identificador: str) -> str:
        classe = {"fig": "figura", "gra": "grafico", "tab": "tabela", "eq": "equacao"}[prefixo]
        conteudo = {
            "fig": "", "gra": "",
            "tab": "| Item | Valor |\n|---|---:|\n| Registro | 1 |\n",
            "eq": "$$\nx = 1 + 2\n$$\n",
        }[prefixo]
        imagem = ' arquivo="imagem.png"' if prefixo in {"fig", "gra"} else ""
        return (f'\n::: {{.{classe} identificador="{prefixo}:{identificador}" '
                f'titulo="Registro de estudo" fonte="Equipe de elaboração."{imagem}}}\n'
                + conteudo + ":::\n")

    def test_ir_e_renumeracao_dos_quatro_tipos_sao_compartilhadas(self) -> None:
        for ordem in (("a", "b"), ("b", "a"), ("novo", "b", "a")):
            corpo = "Consultar @fig:a, @gra:a, @tab:a e @eq:a.\n" + "".join(
                self.objeto(prefixo, identificador)
                for identificador in ordem for prefixo in ("fig", "gra", "tab", "eq")
            )
            relatorio = self.interpretar(corpo)
            artigo = self.interpretar(corpo, modelo="artigo")
            self.assertEqual(relatorio["blocks"], artigo["blocks"])
            objetos = apoio.objetos_ast(relatorio)
            for identificador in ordem:
                for prefixo in ("fig", "gra", "tab", "eq"):
                    self.assertEqual(objetos[f"{prefixo}:{identificador}"]["senai-numero"],
                                     str(ordem.index(identificador) + 1))

    def test_validacao_do_relatorio_rejeita_ids_destinos_e_arquivos_invalidos(self) -> None:
        casos = (
            (self.figura("igual") + self.figura("igual"), "fig:igual"),
            ("[Consultar](#sec:ausente).\n", "sec:ausente"),
            (self.figura("ausente").replace("imagem.png", "ausente.png"), "ausente.png"),
            ("Consultar @origem_ausente.\n", "origem_ausente"),
        )
        for corpo, diagnostico in casos:
            with self.subTest(diagnostico=diagnostico):
                resultado = self.executar(self.escrever(corpo), validar=True)
                self.assertNotEqual(resultado.returncode, 0)
                self.assertIn(diagnostico, resultado.stderr)
                self.assertFalse((self.pasta / "saida").exists())

    @unittest.skipUnless(PDF_DISPONIVEL, "XeLaTeX e Poppler necessários para validar a capa")
    def test_pdf_capa_preserva_hierarquia_posicoes_e_tres_autores(self) -> None:
        autores = ["Equipe de preparação", "Equipe de registro", "Equipe de revisão"]
        self.gerar("# Registro\n\nConteúdo.\n", "tex,pdf", sumario=False,
                   titulo="Relatório de estudo", autor=autores,
                   tipo_trabalho="TRABALHO DE CONCLUSÃO DE CURSO",
                   curso="Habilitação Técnica em Mecânica", local="Rondonópolis – MT", data="2026")
        largura, altura, palavras = self.palavras_da_capa()
        self.assertAlmostEqual(largura, 595.3, delta=1)
        self.assertAlmostEqual(altura, 841.9, delta=1)
        for texto, y in (("TRABALHO", 258.06), ("HABILITAÇÃO", 320.16),
                         ("RELATÓRIO", 402.96), ("RONDONÓPOLIS", 713.46), ("2026", 734.16)):
            palavra = next((p for p in palavras if p["texto"] == texto), None)
            self.assertIsNotNone(palavra, texto)
            self.assertAlmostEqual(float(palavra["yMin"]), y, delta=8, msg=texto)
        linhas = []
        for palavra in palavras:
            if palavra["texto"] == "Equipe":
                y = float(palavra["yMin"])
                linha = [p for p in palavras if abs(float(p["yMin"]) - y) < 2]
                linhas.append((y, " ".join(p["texto"] for p in linha),
                               max(float(p["xMax"]) for p in linha)))
        self.assertEqual([linha[1] for linha in linhas], autores)
        for indice, (y, _, direita) in enumerate(linhas):
            self.assertAlmostEqual(y, 506.46 + indice * 20.7, delta=8)
            self.assertAlmostEqual(direita, 538.73, delta=3)

        titulo_longo = ("Relatório de estudo da rastreabilidade das medições e da revisão dos registros "
                        "de manutenção em um conjunto motor-bomba com dados simulados")
        self.gerar("# Registro\n\nConteúdo.\n", "tex,pdf", sumario=False,
                   titulo=titulo_longo, autor=autores, local=None, data=None)
        paginas = self.paginas()
        capa = re.sub(r"\s+", " ", paginas[0])
        for autor in autores:
            self.assertIn(autor, capa)
        self.assertIn("DADOS SIMULADOS", capa)
        self.assertNotIn("RONDONÓPOLIS", capa)
        self.assertNotIn("2026", capa)
        _, _, palavras = self.palavras_da_capa()
        autores_y = min(float(p["yMin"]) for p in palavras if p["texto"] == "Equipe")
        titulo_fim = max(float(p["yMax"]) for p in palavras
                         if 390 < float(p["yMin"]) < autores_y - 5)
        self.assertLess(titulo_fim, autores_y - 8, "Título e autoria devem permanecer separados")

    @unittest.skipUnless(PDF_DISPONIVEL, "XeLaTeX e Poppler necessários para validar a paginação")
    def test_pdf_capitulos_abrem_nova_pagina_e_sumario_tem_destinos(self) -> None:
        corpo = ("# Preparação {#sec:preparacao}\n\nPasso de preparação.\n\n"
                 "## Detalhe\n\nRegistro da condição.\n\n"
                 "# Resultados {#sec:resultados}\n\nEvidência dos resultados.\n\n"
                 "[Voltar à preparação](#sec:preparacao).\n")
        tex = self.gerar(corpo, "tex,pdf", pre_textuais=False, sumario=False)
        paginas = self.paginas()
        self.assertEqual(len(paginas), 2)
        self.assertIn("Passo de preparação.", paginas[0])
        self.assertIn("Registro da condição.", paginas[0])
        self.assertIn("Evidência dos resultados.", paginas[1])
        self.assertNotIn("?", "".join(paginas))
        self.assertIn(r"\label{sec:preparacao}", tex)
        self.assertRegex(tex, r"\\(?:hyperref\[sec:preparacao\]|hyperlink\{sec:preparacao\})")

        self.gerar(corpo, "tex,pdf", pre_textuais=False, sumario=True)
        paginas = self.paginas()
        self.assertEqual(len(paginas), 3)
        self.assertIn("sumário", paginas[0].casefold())
        self.assertIn("Preparação", paginas[0])
        self.assertIn("Resultados", paginas[0])
        self.assertTrue(all(pagina.strip() for pagina in paginas))

    @unittest.skipUnless(PDF_DISPONIVEL, "XeLaTeX e Poppler necessários para validar os opcionais")
    def test_pdf_opcionais_ausentes_nao_criam_paginas_ou_rotulos_vazios(self) -> None:
        opcionais = dict(sumario=False, resumo="", palavras_chave=[], local=None, data="",
                         orientador="", coordenacao=None, banca=[], data_aprovacao="",
                         natureza="", tipo_trabalho="", aprovacao=True)
        self.gerar("# Registro\n\nConteúdo presente.\n", "tex,pdf", **opcionais)
        paginas = self.paginas()
        self.assertEqual(len(paginas), 3, "Capa, rosto e corpo; aprovação ausente")
        texto = "".join(paginas)
        for ausente in ("TERMO DE APROVAÇÃO", "Orientador(a):", "BANCA EXAMINADORA",
                        "Coordenação pedagógica:", "Resultado final:", "Palavras-chave:", "RESUMO"):
            self.assertNotIn(ausente, texto)
        self.assertTrue(all(pagina.strip() for pagina in paginas))
        self.gerar("# Registro\n\nConteúdo presente.\n", "tex,pdf",
                   **opcionais, capa=False, folha_rosto=False)
        paginas = self.paginas()
        self.assertEqual(len(paginas), 1)
        self.assertIn("Conteúdo presente.", paginas[0])


if __name__ == "__main__":
    unittest.main()
