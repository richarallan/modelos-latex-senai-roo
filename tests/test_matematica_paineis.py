from __future__ import annotations

import re
import shutil
import subprocess
import unittest
import xml.etree.ElementTree as ET

import test_referencias as apoio


PANDOC_DISPONIVEL = shutil.which("pandoc") is not None
PDF_DISPONIVEL = all(
    shutil.which(ferramenta) for ferramenta in ("pandoc", "xelatex", "pdftotext", "pdfinfo")
)


@unittest.skipUnless(PANDOC_DISPONIVEL, "Pandoc necessário para integração")
class MatematicaPaineisTestes(unittest.TestCase):
    # Reutiliza as fixtures e o executor CLI, sem herdar/repetir os testes de referências.
    setUp = apoio.ReferenciasTestes.setUp
    escrever_png = staticmethod(apoio.ReferenciasTestes.escrever_png)
    escrever_bibliografia = apoio.ReferenciasTestes.escrever_bibliografia
    executar = apoio.ReferenciasTestes.executar
    ler_tex = apoio.ReferenciasTestes.ler_tex
    normalizar = staticmethod(apoio.ReferenciasTestes.normalizar)
    verificar_chamada = apoio.ReferenciasTestes.verificar_chamada
    paginas_pdf = apoio.ReferenciasTestes.paginas_pdf

    @classmethod
    def setUpClass(cls) -> None:
        apoio.ReferenciasTestes.setUpClass.__func__(cls)

    @staticmethod
    def imagem(
        identificador: str,
        titulo: str,
        *,
        fonte: str = "Elaboração própria.",
        nota: str | None = None,
        classe: str = "figura",
        prefixo: str = "fig",
    ) -> str:
        adicional = f' nota="{nota}"' if nota else ""
        return (
            f'\n::: {{.{classe} #{prefixo}:{identificador} titulo="{titulo}" '
            f'fonte="{fonte}"{adicional}}}\n'
            "![Esquema didático](imagem.png){width=100%}\n"
            ":::\n"
        )

    @staticmethod
    def painel(imagens: list[str], colunas: int | str | None = 2) -> str:
        atributo = f" colunas={colunas}" if colunas is not None else ""
        return "\n:::: {.painel-imagens" + atributo + "}\n" + "\n".join(imagens) + "\n::::\n"

    @staticmethod
    def equacao(identificador: str, expressao: str, *, titulo: str | None = None) -> str:
        atributo = f' titulo="{titulo}"' if titulo else ""
        return (
            f'\n::: {{.equacao #eq:{identificador}{atributo} fonte="Elaboração própria."}}\n'
            "$$\n" + expressao + "\n$$\n:::\n"
        )

    def test_formula_multilinha_recebe_alinhamento_e_numero_sem_legenda_grafica(self) -> None:
        corpo = (
            "A fórmula em linha $a^2$ antecede a @eq:balanco.\n"
            + self.equacao(
                "balanco",
                "a &= b^2 + c_1 \\\\\n"
                "d &= e_2 + f^3",
                titulo="Relação & deslocamento",
            )
        )
        tex = self.ler_tex(self.executar(corpo))
        self.verificar_chamada(tex, "eq", "balanco", 1)
        equacoes = re.findall(r"\\begin\{equation\}(.*?)\\end\{equation\}", tex, re.DOTALL)
        self.assertEqual(len(equacoes), 1)
        self.assertEqual(equacoes[0].count(r"\begin{aligned}"), 1)
        self.assertEqual(equacoes[0].count(r"\end{aligned}"), 1)
        self.assertEqual(re.findall(r"\\tag\{([^}]+)\}", equacoes[0]), ["1"])
        self.assertIn(r"Relação \& deslocamento", self.normalizar(tex))
        self.assertNotRegex(self.normalizar(tex), r"Equação\s+1\s+(?:---|—)")
        self.assertNotIn(r"\textbf{Relação \& deslocamento}", self.normalizar(tex))
        self.assertIn(r"\(a^2\)", tex)

    def test_ambiente_matematico_explicito_nao_e_aninhado_e_ids_renumeram(self) -> None:
        expressao = "\\begin{aligned}\na &= b + c \\\\\nd &= e - f\n\\end{aligned}"
        for ordem in (("saldo", "volume"), ("volume", "saldo"), ("novo", "volume", "saldo")):
            with self.subTest(ordem=ordem):
                corpo = "Comparar @eq:saldo e @eq:volume.\n" + "".join(
                    self.equacao(identificador, expressao) for identificador in ordem
                )
                tex = self.ler_tex(self.executar(corpo))
                equacoes = re.findall(
                    r"\\begin\{equation\}(.*?)\\end\{equation\}", tex, re.DOTALL
                )
                self.assertEqual(len(equacoes), len(ordem))
                for numero, (identificador, trecho) in enumerate(zip(ordem, equacoes), 1):
                    self.assertEqual(trecho.count(r"\begin{aligned}"), 1)
                    self.assertEqual(trecho.count(r"\end{aligned}"), 1)
                    self.assertEqual(re.findall(r"\\tag\{([^}]+)\}", trecho), [str(numero)])
                    alvos = re.findall(r"\\(?:hypertarget|label)\{(eq:[^}]+)\}", trecho)
                    self.assertEqual(set(alvos), {f"eq:{identificador}"})
                for identificador in ("saldo", "volume"):
                    self.verificar_chamada(tex, "eq", identificador, ordem.index(identificador) + 1)

    def test_marcadores_escapados_comentados_ou_internos_nao_criam_alinhamento_externo(self) -> None:
        casos = {
            "ampersand-escapado": r"x = \text{A \& B}",
            "comentario": "x = a + b % comentário com & e \\\\\n + c",
            "matriz-interna": r"A = \begin{pmatrix}a & b \\ c & d\end{pmatrix}",
        }
        for nome, expressao in casos.items():
            with self.subTest(caso=nome):
                tex = self.ler_tex(self.executar(self.equacao("simples", expressao)))
                equacoes = re.findall(
                    r"\\begin\{equation\}(.*?)\\end\{equation\}", tex, re.DOTALL
                )
                self.assertEqual(len(equacoes), 1)
                self.assertNotIn(r"\begin{aligned}", equacoes[0])
                self.assertEqual(re.findall(r"\\tag\{([^}]+)\}", equacoes[0]), ["1"])

    def test_ilustracao_e_desenho_usam_a_mesma_sequencia_de_figuras(self) -> None:
        corpo = "Ver @fig:base, @fig:ilustracao e @fig:desenho.\n" + "".join(
            self.imagem(identificador, titulo, classe=classe)
            for identificador, titulo, classe in (
                ("base", "Vista geral", "figura"),
                ("ilustracao", "Vista ilustrativa", "ilustracao"),
                ("desenho", "Vista desenhada", "desenho"),
            )
        )
        tex = self.ler_tex(self.executar(corpo))
        for numero, identificador in enumerate(("base", "ilustracao", "desenho"), 1):
            self.verificar_chamada(tex, "fig", identificador, numero)

    def test_painel_preserva_ordem_ids_fontes_notas_e_citacoes(self) -> None:
        bibliografia = self.escrever_bibliografia()
        corpo = "Ver @fig:alfa, @fig:beta e @gra:gama.\n" + self.painel(
            [
                self.imagem("alfa", "Vista Alfa", fonte="Adaptado de @silva2023.", nota="NotaAlfa."),
                self.imagem("beta", "Vista Beta", fonte="OrigemBeta."),
                self.imagem("gama", "Dados Gama", classe="grafico", prefixo="gra"),
            ],
            colunas=None,
        )
        tex = self.ler_tex(self.executar(corpo, bibliografia=bibliografia))
        for tipo, identificador, numero in (("fig", "alfa", 1), ("fig", "beta", 2), ("gra", "gama", 1)):
            self.verificar_chamada(tex, tipo, identificador, numero)
            self.assertRegex(tex, rf"\\(?:hypertarget|label)\{{{tipo}:{identificador}\}}")
        compacto = self.normalizar(tex)
        self.assertIn("Fonte: Adaptado de Silva", compacto)
        self.assertIn("Nota: NotaAlfa.", compacto)
        self.assertIn("Fonte: OrigemBeta.", compacto)
        self.assertRegex(tex, r"\\(?:hyperlink|citeproc)\{ref-silva2023\}")

    def test_paineis_invalidos_sao_rejeitados(self) -> None:
        imagens = [self.imagem("alfa", "Vista Alfa"), self.imagem("beta", "Vista Beta")]
        casos = [(f"colunas-{colunas}", self.painel(imagens, colunas)) for colunas in (0, 1, 5, "texto")]
        casos.extend(
            [
                ("apenas-uma-imagem", self.painel(imagens[:1])),
                ("texto-solto", self.painel([imagens[0], "Texto sem imagem."])),
                (
                    "tabela-no-painel",
                    self.painel([imagens[0], apoio.ReferenciasTestes.objeto("tab", "dados", "Dados")]),
                ),
                ("painel-aninhado", self.painel([self.painel(imagens), self.imagem("gama", "Gama")])),
            ]
        )
        for nome, corpo in casos:
            with self.subTest(caso=nome):
                resultado = self.executar(corpo, nome=nome)
                self.assertNotEqual(resultado.returncode, 0, resultado.stdout)
                self.assertRegex(resultado.stderr.lower(), r"painel|coluna|imagem")

    def palavras_pdf(self, nome: str = "artigo") -> list[tuple[float, list[dict[str, float | str]]]]:
        xml = subprocess.check_output(
            ["pdftotext", "-bbox", str(self.pasta / "saida" / f"{nome}.pdf"), "-"],
            text=True,
            timeout=30,
        )
        root = ET.fromstring(xml)
        paginas = []
        for pagina in root.iter():
            if pagina.tag.rsplit("}", 1)[-1] != "page":
                continue
            palavras = []
            for palavra in pagina.iter():
                if palavra.tag.rsplit("}", 1)[-1] == "word":
                    palavras.append(
                        {"texto": "".join(palavra.itertext()), **{k: float(v) for k, v in palavra.attrib.items()}}
                    )
            paginas.append((float(pagina.attrib["width"]), palavras))
        return paginas

    def caixa_frase(self, palavras: list[dict[str, float | str]], frase: str) -> tuple[float, float, float, float]:
        tokens = frase.split()
        for inicio in range(len(palavras) - len(tokens) + 1):
            grupo = palavras[inicio:inicio + len(tokens)]
            if [p["texto"] for p in grupo] == tokens:
                return (
                    min(float(p["xMin"]) for p in grupo),
                    min(float(p["yMin"]) for p in grupo),
                    max(float(p["xMax"]) for p in grupo),
                    max(float(p["yMax"]) for p in grupo),
                )
        self.fail(f"Frase não encontrada no PDF: {frase}")

    def destinos_pdf(self) -> dict[str, int]:
        texto = subprocess.check_output(
            ["pdfinfo", "-dests", str(self.pasta / "saida" / "artigo.pdf")],
            text=True,
            timeout=30,
        )
        destinos = {}
        for linha in texto.splitlines():
            encontrado = re.match(r'\s*(\d+)\s+.*"([^"]+)"\s*$', linha)
            if encontrado:
                destinos[encontrado.group(2)] = int(encontrado.group(1))
        return destinos

    @unittest.skipUnless(PDF_DISPONIVEL, "XeLaTeX e Poppler necessários para integração PDF")
    def test_pdf_centraliza_legenda_larga_e_alinha_paineis_de_duas_e_tres_imagens(self) -> None:
        separador = "\n```{=latex}\n\\newpage\n```\n"
        corpo = (
            "Ver @fig:largo, @fig:alfa e @fig:beta.\n"
            + self.imagem("largo", "Titulo Largo", fonte="OrigemLarga.")
            + separador
            + self.painel(
                [
                    self.imagem("alfa", "Titulo Alfa", fonte="OrigemAlfa.", nota="NotaAlfa longa para ocupar mais de uma linha na célula e testar o alinhamento pelo topo."),
                    self.imagem("beta", "Titulo Beta", fonte="OrigemBeta."),
                ]
            )
            + separador
            + self.painel(
                [
                    self.imagem("gama", "Titulo Gama", fonte="OrigemGama."),
                    self.imagem("delta", "Titulo Delta", fonte="OrigemDelta.", nota="NotaDelta."),
                    self.imagem("epsilon", "Titulo Epsilon", fonte="OrigemEpsilon."),
                ],
                colunas=3,
            )
        )
        resultado = self.executar(corpo, formato="tex,pdf")
        self.ler_tex(resultado)
        paginas = self.paginas_pdf()
        self.assertEqual(len(paginas), 3)
        self.assertNotIn("?", " ".join(paginas))
        caixas = self.palavras_pdf()
        largura, palavras = caixas[0]
        legenda = self.caixa_frase(palavras, "Figura 1 — Titulo Largo")
        margem_esquerda, margem_direita = 30 * 72 / 25.4, 20 * 72 / 25.4
        centro_util = (margem_esquerda + largura - margem_direita) / 2
        self.assertAlmostEqual((legenda[0] + legenda[2]) / 2, centro_util, delta=2)
        destinos = self.destinos_pdf()
        self.assertEqual(destinos["fig:largo"], 1)
        for indice_pagina, nomes in (
            (1, [(2, "alfa", "Alfa"), (3, "beta", "Beta")]),
            (2, [(4, "gama", "Gama"), (5, "delta", "Delta"), (6, "epsilon", "Epsilon")]),
        ):
            largura, palavras = caixas[indice_pagina]
            legendas = []
            for numero, identificador, titulo in nomes:
                legenda = self.caixa_frase(palavras, f"Figura {numero} — Titulo {titulo}")
                fonte = self.caixa_frase(palavras, f"Fonte: Origem{titulo}.")
                self.assertAlmostEqual(legenda[0], fonte[0], delta=1)
                self.assertGreaterEqual(legenda[0], margem_esquerda - 1)
                self.assertLessEqual(legenda[2], largura - margem_direita + 1)
                self.assertEqual(destinos[f"fig:{identificador}"], indice_pagina + 1)
                legendas.append(legenda)
            for anterior, atual in zip(legendas, legendas[1:]):
                self.assertAlmostEqual(anterior[1], atual[1], delta=1)
                self.assertLess(anterior[2], atual[0])

    @unittest.skipUnless(PDF_DISPONIVEL, "XeLaTeX e Poppler necessários para integração PDF")
    def test_pdf_painel_distribui_tres_imagens_em_duas_linhas_sem_exceder_margens(self) -> None:
        corpo = "Ver @fig:alfa, @fig:beta e @fig:gama.\n" + self.painel(
            [
                self.imagem("alfa", "Vista Alfa", fonte="OrigemAlfa."),
                self.imagem("beta", "Vista Beta", fonte="OrigemBeta."),
                self.imagem("gama", "Vista Gama", fonte="OrigemGama."),
            ]
        )
        resultado = self.executar(corpo, formato="tex,pdf")
        self.ler_tex(resultado)
        paginas = self.paginas_pdf()
        self.assertEqual(len(paginas), 1)
        self.assertNotIn("?", paginas[0])
        largura, palavras = self.palavras_pdf()[0]
        caixas = [
            self.caixa_frase(palavras, f"Figura {numero} — Vista {titulo}")
            for numero, titulo in enumerate(("Alfa", "Beta", "Gama"), 1)
        ]
        self.assertAlmostEqual(caixas[0][1], caixas[1][1], delta=1)
        self.assertLess(caixas[0][2], caixas[1][0])
        self.assertGreater(caixas[2][1], caixas[0][3] + 50)
        self.assertAlmostEqual(caixas[0][0], caixas[2][0], delta=1)
        margem_esquerda, margem_direita = 30 * 72 / 25.4, 20 * 72 / 25.4
        for caixa in caixas:
            self.assertGreaterEqual(caixa[0], margem_esquerda - 1)
            self.assertLessEqual(caixa[2], largura - margem_direita + 1)
        destinos = self.destinos_pdf()
        self.assertEqual({destinos[f"fig:{id}"] for id in ("alfa", "beta", "gama")}, {1})

    @unittest.skipUnless(PDF_DISPONIVEL, "XeLaTeX e Poppler necessários para integração PDF")
    def test_pdf_formula_composta_preserva_ambientes_internos_e_alinhamento_externo(self) -> None:
        casos = {
            "Cases": (
                "cases",
                r"a &= \begin{cases}b, & b > 0 \\ -b, & b \le 0\end{cases} \\"
                + "\n" + r"c &= d + e",
            ),
            "Matriz": (
                "pmatrix",
                r"A &= \begin{pmatrix}a & b \\ c & d\end{pmatrix} \\"
                + "\n" + r"B &= A^2",
            ),
        }
        for nome, (ambiente, expressao) in casos.items():
            with self.subTest(caso=nome):
                corpo = "Confira a @eq:composta.\n" + self.equacao(
                    "composta", expressao, titulo=f"Relação{nome}"
                )
                resultado = self.executar(corpo, formato="tex,pdf")
                tex = self.ler_tex(resultado)
                self.verificar_chamada(tex, "eq", "composta", 1)
                equacoes = re.findall(
                    r"\\begin\{equation\}(.*?)\\end\{equation\}", tex, re.DOTALL
                )
                self.assertEqual(len(equacoes), 1)
                formula = equacoes[0]
                self.assertEqual(formula.count(r"\begin{aligned}"), 1)
                self.assertEqual(formula.count(r"\end{aligned}"), 1)
                self.assertEqual(formula.count(r"\begin{" + ambiente + "}"), 1)
                self.assertEqual(formula.count(r"\end{" + ambiente + "}"), 1)
                self.assertLess(formula.index(r"\begin{aligned}"), formula.index(r"\begin{" + ambiente + "}"))
                self.assertGreater(formula.index(r"\end{aligned}"), formula.index(r"\end{" + ambiente + "}"))
                self.assertEqual(re.findall(r"\\tag\{([^}]+)\}", formula), ["1"])
                paginas = self.paginas_pdf()
                self.assertEqual(len(paginas), 1)
                self.assertIn(f"Relação{nome}", paginas[0])
                self.assertNotIn("?", paginas[0])
                self.assertEqual(self.destinos_pdf()["eq:composta"], 1)

    @unittest.skipUnless(PDF_DISPONIVEL, "XeLaTeX e Poppler necessários para integração PDF")
    def test_pdf_formula_multilinha_mantem_numero_direita_e_destino_resolvido(self) -> None:
        corpo = "A expressão está em @eq:balanco.\n" + self.equacao(
            "balanco", "a &= b^2 + c_1 \\\\\nd &= e_2 + f^3", titulo="Relação de deslocamentos"
        )
        resultado = self.executar(corpo, formato="tex,pdf")
        tex = self.ler_tex(resultado)
        self.verificar_chamada(tex, "eq", "balanco", 1)
        paginas = self.paginas_pdf()
        self.assertEqual(len(paginas), 1)
        self.assertNotIn("?", paginas[0])
        self.assertIn("Relação de deslocamentos", paginas[0])
        self.assertNotIn("Equação 1 —", paginas[0])
        largura, palavras = self.palavras_pdf()[0]
        numeros_direita = [p for p in palavras if p["texto"] == "(1)" and float(p["xMin"]) > largura * 0.8]
        self.assertEqual(len(numeros_direita), 1)
        self.assertLessEqual(float(numeros_direita[0]["xMax"]), largura - 20 * 72 / 25.4 + 1)
        self.assertEqual(self.destinos_pdf()["eq:balanco"], 1)


if __name__ == "__main__":
    unittest.main()
