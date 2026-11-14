"""Regressões visuais e de navegação do sumário gerado a partir de Markdown."""
from __future__ import annotations

import re
import shutil
import subprocess
import unicodedata
import unittest
import xml.etree.ElementTree as ET
from typing import Any

import test_nucleo as apoio


PDF_DISPONIVEL = all(shutil.which(item) for item in (
    "pandoc", "xelatex", "pdftotext", "pdfinfo", "pdftohtml",
))
NAMESPACE = {"x": "http://www.w3.org/1999/xhtml"}


@unittest.skipUnless(PDF_DISPONIVEL, "Pandoc, XeLaTeX e Poppler necessários para o sumário")
class SumarioTestes(unittest.TestCase):
    setUp = apoio.NucleoDocumentalTestes.setUp
    escrever = apoio.NucleoDocumentalTestes.escrever
    executar = apoio.NucleoDocumentalTestes.executar

    @classmethod
    def setUpClass(cls) -> None:
        apoio.NucleoDocumentalTestes.setUpClass.__func__(cls)

    def gerar(self, corpo: str, modelo: str = "relatorio") -> None:
        entrada = self.escrever(
            corpo, nome="sumario", modelo=modelo, pre_textuais=False, sumario=True,
            resumo=None, palavras_chave=[], local=None, data=None,
        )
        resultado = self.executar(entrada, "tex,pdf")
        self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)
        self.pdf = self.pasta / "saida" / "sumario.pdf"

    def destinos(self) -> dict[str, tuple[int, float]]:
        texto = subprocess.check_output(
            ["pdfinfo", "-dests", str(self.pdf)], text=True, timeout=30,
        )
        resultado = {}
        for linha in texto.splitlines():
            item = re.match(
                r'\s*(\d+)\s+\[\s*XYZ\s+[-\d.]+\s+([-\d.]+)\s+[^\]]*\]\s+"([^"]+)"',
                linha,
            )
            if item:
                resultado[item[3]] = (int(item[1]), float(item[2]))
        return resultado

    def linhas_pdf(self) -> list[dict[str, Any]]:
        xml = subprocess.check_output(
            ["pdftotext", "-bbox", str(self.pdf), "-"], text=True, timeout=30,
        )
        linhas = []
        for numero, pagina in enumerate(ET.fromstring(xml).findall(".//x:page", NAMESPACE), 1):
            grupos = []
            palavras = [{
                **{chave: float(valor) for chave, valor in no.attrib.items()},
                "texto": unicodedata.normalize("NFKC", no.text or ""),
            } for no in pagina.findall(".//x:word", NAMESPACE)]
            for palavra in sorted(palavras, key=lambda p: (p["yMin"], p["xMin"])):
                grupo = next((g for g in grupos[-3:]
                              if abs(g["yMin"] - palavra["yMin"]) < 2.5), None)
                if grupo is None:
                    grupo = {"yMin": palavra["yMin"], "palavras": []}
                    grupos.append(grupo)
                grupo["palavras"].append(palavra)
            for grupo in grupos:
                grupo["palavras"].sort(key=lambda p: p["xMin"])
                grupo.update(pagina=numero, largura=float(pagina.attrib["width"]),
                             altura=float(pagina.attrib["height"]))
                linhas.append(grupo)
        return linhas

    @staticmethod
    def texto_linha(linha: dict[str, Any]) -> str:
        return " ".join(p["texto"] for p in linha["palavras"])

    def linhas_sumario(self) -> list[dict[str, Any]]:
        linhas = self.linhas_pdf()
        inicio = next((i for i, linha in enumerate(linhas)
                       if self.texto_linha(linha).casefold() == "sumário"), None)
        self.assertIsNotNone(inicio, "O PDF deve conter o título do sumário")
        primeira_pagina, topo_destino = self.destinos()["section.1"]
        return [linha for linha in linhas[inicio + 1:]
                if linha["pagina"] < primeira_pagina
                or linha["pagina"] == primeira_pagina
                and linha["yMin"] < linha["altura"] - topo_destino - 1]

    @staticmethod
    def pontilhado(palavra: dict[str, Any]) -> bool:
        return bool(re.fullmatch(r"[.·…]+", palavra["texto"]))

    def entrada(self, linhas: list[dict[str, Any]], indicador: str | None,
                inicio_titulo: str) -> dict[str, Any]:
        for indice, linha in enumerate(linhas):
            palavras = linha["palavras"]
            if indicador is not None and palavras[0]["texto"] != indicador:
                continue
            inicio = 1 if indicador is not None else 0
            if not " ".join(p["texto"] for p in palavras[inicio:]).casefold().startswith(
                inicio_titulo.casefold()
            ):
                continue
            linhas_entrada = []
            for atual in linhas[indice:indice + 12]:
                if linhas_entrada and atual["pagina"] != linha["pagina"]:
                    break
                if linhas_entrada and re.fullmatch(r"\d+(?:\.\d+)*", atual["palavras"][0]["texto"]):
                    break
                linhas_entrada.append(atual)
                ultima = atual["palavras"][-1]
                if ultima["texto"].isdigit() and ultima["xMin"] > atual["largura"] * 0.8:
                    palavras_titulo = []
                    for posicao, parte in enumerate(linhas_entrada):
                        itens = parte["palavras"][inicio if posicao == 0 else 0:]
                        if parte is atual:
                            itens = itens[:-1]
                        palavras_titulo.extend(p for p in itens if not self.pontilhado(p))
                    return {
                        "indicador": palavras[0] if indicador is not None else None,
                        "titulo": palavras_titulo,
                        "linhas": linhas_entrada,
                        "pagina": ultima,
                    }
        self.fail(f"Entrada não encontrada no sumário: {indicador or ''} {inicio_titulo}")

    def verificar_pontilhado(self, entrada: dict[str, Any]) -> None:
        pontos = [p for linha in entrada["linhas"] for p in linha["palavras"]
                  if self.pontilhado(p)]
        self.assertGreaterEqual(sum(len(p["texto"]) for p in pontos), 3,
                                "Cada entrada deve ter pontilhado até a paginação")
        self.assertLess(pontos[-1]["xMax"], entrada["pagina"]["xMin"])

    def test_pdf_sumario_alinha_niveis_pontilha_e_preserva_capitalizacao(self) -> None:
        corpo = (
            "# Primeira seção {#sec:primeira}\n\nRegistro de preparação.\n\n"
            "## Contexto SENAI\n\nCondição observada.\n\n"
            "### Detalhe ABNT\n\nEvidência registrada.\n\n"
            "# Etapa final {#sec:final}\n\nSíntese da revisão.\n\n"
            "# Referências {.unnumbered}\n\nPublicações de consulta.\n\n"
            "# Apêndice A — Roteiro {.unnumbered}\n\nRoteiro de registro.\n"
        )
        casos = (("1", "PRIMEIRA SEÇÃO"), ("1.1", "Contexto SENAI"),
                 ("1.1.1", "Detalhe ABNT"), ("2", "ETAPA FINAL"),
                 (None, "REFERÊNCIAS"), (None, "APÊNDICE A — ROTEIRO"))
        for modelo in ("artigo", "nota_aula", "atividade_avaliativa", "relatorio"):
            with self.subTest(modelo=modelo):
                self.gerar(corpo, modelo)
                linhas = self.linhas_sumario()
                entradas = [self.entrada(linhas, indicador, titulo) for indicador, titulo in casos]
                for entrada, (_, titulo) in zip(entradas, casos):
                    self.assertEqual(" ".join(p["texto"] for p in entrada["titulo"]), titulo)
                    self.verificar_pontilhado(entrada)
                numeros = [e["indicador"]["xMin"] for e in entradas if e["indicador"]]
                titulos = [e["titulo"][0]["xMin"] for e in entradas]
                paginas = [e["pagina"]["xMax"] for e in entradas]
                margem = (30 if modelo in {"artigo", "relatorio"} else 25) * 72 / 25.4
                for numero in numeros:
                    self.assertAlmostEqual(numero, margem, delta=2,
                                           msg="O indicativo deve começar na margem real do perfil")
                self.assertLessEqual(max(numeros) - min(numeros), 1.5,
                                     "Indicativos de níveis diferentes devem compartilhar a margem esquerda")
                self.assertLessEqual(max(titulos) - min(titulos), 2,
                                     "Títulos e elementos sem número devem usar uma coluna comum")
                self.assertLessEqual(max(paginas) - min(paginas), 2,
                                     "A paginação deve ficar alinhada à direita")

    def test_pdf_sumario_indicativo_extenso_e_titulo_longo_nao_sobrepoem_colunas(self) -> None:
        partes = []
        for capitulo in range(1, 11):
            partes.append(f"# Capítulo de estudo {capitulo}\n\nRegistro do capítulo.\n")
        for secao in range(1, 11):
            partes.append(f"## Etapa de revisão {secao}\n\nRegistro da etapa.\n")
        for detalhe in range(1, 10):
            partes.append(f"### Conferência da condição {detalhe}\n\nRegistro da condição.\n")
        titulo = ("Rastreabilidade das medições e revisão das evidências do registro técnico "
                  "para organizar as condições de preparação e a análise dos dados em equipe "
                  "com observações e procedimentos documentados")
        partes.append(f"### {titulo}\n\nRegistro do detalhe final.\n")
        self.gerar("\n".join(partes))
        linhas = self.linhas_sumario()
        primeira = self.entrada(linhas, "1", "CAPÍTULO DE ESTUDO")
        longa = self.entrada(linhas, "10.10.10", "Rastreabilidade das medições")
        self.assertAlmostEqual(primeira["indicador"]["xMin"], longa["indicador"]["xMin"], delta=1.5)
        self.assertAlmostEqual(primeira["titulo"][0]["xMin"], longa["titulo"][0]["xMin"], delta=2)
        self.assertGreater(longa["titulo"][0]["xMin"] - longa["indicador"]["xMax"], 2.5,
                           "O indicativo extenso precisa de espaço antes do título")
        self.assertGreaterEqual(len(longa["linhas"]), 2, "O exemplo deve exercitar continuação de título")
        for linha in longa["linhas"][1:]:
            texto = [p for p in linha["palavras"]
                     if not self.pontilhado(p) and p is not longa["pagina"]]
            if texto:
                self.assertAlmostEqual(texto[0]["xMin"], longa["titulo"][0]["xMin"], delta=2,
                                       msg="A continuação deve alinhar pela coluna do título")
        self.verificar_pontilhado(longa)
        self.assertAlmostEqual(primeira["pagina"]["xMax"], longa["pagina"]["xMax"], delta=2)

    def test_pdf_links_do_sumario_chegam_a_pagina_do_titulo_apos_reordenar(self) -> None:
        titulos = {"preparacao": "Preparação do registro", "revisao": "Revisão das evidências"}
        for ordem in (("preparacao", "revisao"), ("revisao", "preparacao")):
            with self.subTest(ordem=ordem):
                corpo = "\n".join(
                    f"# {titulos[item]} {{#sec:{item}}}\n\nEvidência de {item}.\n"
                    for item in ordem
                )
                corpo += "\n[Voltar à preparação](#sec:preparacao).\n"
                self.gerar(corpo)
                paginas = subprocess.check_output(
                    ["pdftotext", "-layout", str(self.pdf), "-"], text=True, timeout=30,
                ).split("\f")
                html = ET.fromstring(subprocess.check_output(
                    ["pdftohtml", "-q", "-xml", "-stdout", str(self.pdf)],
                    text=True, stderr=subprocess.DEVNULL, timeout=30,
                ))
                links = [(" ".join("".join(a.itertext()).split()), a.attrib["href"])
                         for a in html.findall(".//a")]
                destinos = self.destinos()
                entradas = self.linhas_sumario()
                for numero, item in enumerate(ordem, 1):
                    titulo = titulos[item].upper()
                    pagina_real = next((i for i, pagina in enumerate(paginas, 1)
                                        if re.search(rf"(?m)^\s*{numero}\s+{re.escape(titulo)}\s*$", pagina)), None)
                    self.assertIsNotNone(pagina_real, titulo)
                    self.assertEqual(destinos[f"section.{numero}"][0], pagina_real,
                                     "O destino do sumário deve acompanhar a quebra de seção")
                    paginas_dos_links = {
                        int(re.search(r"#(\d+)$", destino)[1])
                        for texto, destino in links
                        if re.sub(r"^\d+(?:\.\d+)*\s*", "", texto).casefold() == titulo.casefold()
                        and re.search(r"#(\d+)$", destino)
                    }
                    self.assertEqual(paginas_dos_links, {pagina_real}, titulo)
                    entrada = self.entrada(entradas, str(numero), titulo)
                    self.assertEqual(int(entrada["pagina"]["texto"]), numero,
                                     "Os números exibidos devem ser atualizados após reorganizar seções")


if __name__ == "__main__":
    unittest.main()
