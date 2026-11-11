from __future__ import annotations

import json
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

import yaml

from scripts import renderizar


@unittest.skipUnless(shutil.which("pandoc"), "Pandoc necessário para integração")
class ReferenciasTestes(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.metadados = dict(
            renderizar.carregar_documento(
                renderizar.RAIZ / "exemplos" / "nota-aula-metrologia.md"
            ).metadados,
            modelo="artigo",
            pre_textuais=False,
        )

    def setUp(self) -> None:
        self.temporario = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporario.cleanup)
        self.pasta = Path(self.temporario.name)
        self.escrever_png(self.pasta / "imagem.png")
        self.referencia = {
            "id": "silva2023",
            "type": "book",
            "author": [{"family": "Silva", "given": "Ana"}],
            "issued": {"date-parts": [[2023]]},
            "title": "Manual de inspeção mecânica",
            "publisher": "Editora Didática",
            "publisher-place": "Cuiabá",
        }

    @staticmethod
    def escrever_png(caminho: Path) -> None:
        def bloco(tipo: bytes, dados: bytes) -> bytes:
            return (
                struct.pack(">I", len(dados))
                + tipo
                + dados
                + struct.pack(">I", zlib.crc32(tipo + dados) & 0xFFFFFFFF)
            )

        largura, altura = 16, 8
        pixels = b"".join(b"\x00" + b"\x80\x80\x80" * largura for _ in range(altura))
        caminho.write_bytes(
            b"\x89PNG\r\n\x1a\n"
            + bloco(b"IHDR", struct.pack(">IIBBBBB", largura, altura, 8, 2, 0, 0, 0))
            + bloco(b"IDAT", zlib.compress(pixels))
            + bloco(b"IEND", b"")
        )

    def escrever_bibliografia(self, referencias: list[dict] | None = None) -> str:
        destino = self.pasta / "bibliografia" / "referencias.yaml"
        destino.parent.mkdir(exist_ok=True)
        destino.write_text(
            yaml.safe_dump(
                {"references": referencias if referencias is not None else [self.referencia]},
                allow_unicode=True,
                sort_keys=False,
            ),
            encoding="utf-8",
        )
        return "bibliografia/referencias.yaml"

    def executar(
        self,
        corpo: str,
        *,
        nome: str = "artigo",
        formato: str = "tex",
        validar_apenas: bool = False,
        **metadados: object,
    ) -> subprocess.CompletedProcess[str]:
        entrada = self.pasta / f"{nome}.md"
        entrada.write_text(
            "---\n"
            + yaml.safe_dump(
                {**self.metadados, **metadados}, allow_unicode=True, sort_keys=False
            )
            + "---\n"
            + corpo,
            encoding="utf-8",
        )
        comando = [
            sys.executable,
            "scripts/renderizar.py",
            str(entrada),
            "--formato",
            formato,
            "--saida",
            str(self.pasta / "saida"),
        ]
        if validar_apenas:
            comando.append("--validar-apenas")
        return subprocess.run(
            comando,
            cwd=renderizar.RAIZ,
            env=renderizar.ambiente_compilacao(),
            text=True,
            capture_output=True,
            timeout=90,
        )

    def ler_tex(self, resultado: subprocess.CompletedProcess[str], nome: str = "artigo") -> str:
        self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)
        return (self.pasta / "saida" / f"{nome}.tex").read_text(encoding="utf-8")

    @staticmethod
    def objeto(tipo: str, identificador: str, titulo: str, *, nota: bool = False) -> str:
        classes = {"fig": "figura", "gra": "grafico", "tab": "tabela", "eq": "equacao"}
        corpo = {
            "fig": "![Esquema](imagem.png){width=25%}",
            "gra": "![Dados simulados](imagem.png){width=25%}",
            "tab": "| Grandeza | Valor |\n|---|---|\n| Desvio | 0,18 mm |",
            "eq": "$$\nx = 2 + 3\n$$",
        }[tipo]
        adicional = ' nota="Exemplo didático & verificável."' if nota else ""
        return (
            f'\n::: {{.{classes[tipo]} #{tipo}:{identificador} titulo="{titulo}" '
            f'fonte="Equipe A & B (2026)."{adicional}}}\n'
            + corpo
            + "\n:::\n"
        )

    @staticmethod
    def normalizar(tex: str) -> str:
        return re.sub(r"\s+", " ", tex.replace("~", " ").replace("\u00a0", " "))

    def verificar_chamada(self, tex: str, tipo: str, identificador: str, numero: int) -> None:
        nomes = {"fig": "Figura", "gra": "Gráfico", "tab": "Tabela", "eq": "Equação"}
        rotulo = f"{nomes[tipo]} ({numero})" if tipo == "eq" else f"{nomes[tipo]} {numero}"
        alvo = re.escape(f"{tipo}:{identificador}")
        self.assertRegex(
            self.normalizar(tex),
            rf"\\(?:hyperlink\{{{alvo}\}}|hyperref\[{alvo}\])\{{{re.escape(rotulo)}\}}",
        )

    def test_referencias_antecipadas_e_renumeracao_independente_dos_quatro_tipos(self) -> None:
        tipos = ("fig", "gra", "tab", "eq")
        chamadas = "Comparação: " + "; ".join(
            f"@{tipo}:{identificador}"
            for tipo in tipos
            for identificador in ("alfa", "beta")
        ) + ".\n"
        for indice, ordem in enumerate((("alfa", "beta"), ("beta", "alfa"), ("novo", "beta", "alfa"))):
            with self.subTest(ordem=ordem):
                corpo = chamadas + "\n# Elementos\n" + "".join(
                    self.objeto(tipo, identificador, f"Elemento {tipo} {identificador}")
                    for identificador in ordem
                    for tipo in tipos
                )
                tex = self.ler_tex(self.executar(corpo, nome=f"ordem-{indice}"), f"ordem-{indice}")
                for tipo in tipos:
                    for identificador in ("alfa", "beta"):
                        numero = ordem.index(identificador) + 1
                        self.verificar_chamada(tex, tipo, identificador, numero)
                        self.assertRegex(tex, rf"\\(?:hypertarget|label)\{{{tipo}:{identificador}\}}")
                equacoes = re.findall(
                    r"\\begin\{equation\}(.*?)\\end\{equation\}", tex, re.DOTALL
                )
                self.assertEqual(len(equacoes), len(ordem))
                for numero, (identificador, trecho) in enumerate(zip(ordem, equacoes), 1):
                    alvos = re.findall(r"\\(?:hypertarget|label)\{(eq:[^}]+)\}", trecho)
                    self.assertEqual(set(alvos), {f"eq:{identificador}"})
                    self.assertEqual(re.findall(r"\\tag\{([^}]+)\}", trecho), [str(numero)])

    def test_titulos_fontes_e_notas_sao_informados_em_markdown_e_escapados(self) -> None:
        corpo = "# Elementos\n" + "".join(
            self.objeto(tipo, "exemplo", f"Medição {tipo} & análise", nota=True)
            for tipo in ("fig", "gra", "tab", "eq")
        )
        tex = self.ler_tex(self.executar(corpo))
        compacto = self.normalizar(tex)
        for tipo in ("fig", "gra", "tab", "eq"):
            self.assertIn(rf"Medição {tipo} \& análise", compacto)
        self.assertEqual(compacto.count(r"Equipe A \& B (2026)."), 4)
        self.assertEqual(compacto.count(r"Exemplo didático \& verificável."), 4)
        self.assertIn("Fonte:", compacto)
        self.assertIn("Nota:", compacto)

    def test_objetos_invalidos_e_chamadas_nao_resolvidas_interrompem_a_geracao(self) -> None:
        valido = self.objeto("fig", "alfa", "Motor-bomba")
        casos = [
            ("sem-id", valido.replace("#fig:alfa", ""), r"identificador|identifica|id"),
            ("duplicado", valido + valido, r"duplic"),
            ("chamada-ausente", "Ver @fig:ausente.\n" + valido, r"fig:ausente|ausente"),
            ("prefixo", valido.replace("#fig:alfa", "#tab:alfa"), r"prefixo|identificador"),
            ("sem-titulo", valido.replace('titulo="Motor-bomba"', ""), r"t.tulo"),
            ("sem-fonte", valido.replace('fonte="Equipe A & B (2026)."', ""), r"fonte"),
        ]
        for nome, corpo, erro in casos:
            with self.subTest(caso=nome):
                resultado = self.executar(corpo, nome=nome)
                self.assertNotEqual(resultado.returncode, 0, resultado.stdout)
                self.assertRegex(resultado.stderr.lower(), erro)

    def test_bibliografia_relativa_e_citacoes_autor_data_com_links(self) -> None:
        caminho = self.escrever_bibliografia()
        resultado = self.executar(
            "# Introdução\n\nSegundo @silva2023, o registro deve ser verificável. "
            "A revisão usa a mesma referência [@silva2023, p. 17].\n",
            bibliografia=caminho,
        )
        tex = self.ler_tex(resultado)
        self.assertIn("Manual de inspeção mecânica", self.normalizar(tex))
        self.assertIn("2023", tex)
        self.assertRegex(
            tex,
            r"\\(?:hypertarget\{ref-silva2023\}|bibitem(?:\[[^\]]*\])?\{ref-silva2023\})",
        )
        self.assertGreaterEqual(len(re.findall(r"\\(?:hyperlink|citeproc)\{ref-silva2023\}", tex)), 2)
        self.assertNotIn("@silva2023", tex)

    def test_bibliografia_ausente_ids_duplicados_e_citacao_desconhecida_falham(self) -> None:
        casos = [
            ("arquivo-ausente", "bibliografia/inexistente.yaml", [self.referencia], "@silva2023", r"inexistente.yaml|bibliografia"),
            ("id-duplicado", "bibliografia/referencias.yaml", [self.referencia, self.referencia], "@silva2023", r"duplic"),
            ("citacao-ausente", "bibliografia/referencias.yaml", [self.referencia], "@naocadastrado2026", r"naocadastrado2026|cita"),
        ]
        for nome, caminho, referencias, corpo, erro in casos:
            with self.subTest(caso=nome):
                self.escrever_bibliografia(referencias)
                resultado = self.executar(corpo, nome=nome, bibliografia=caminho)
                self.assertNotEqual(resultado.returncode, 0, resultado.stdout)
                self.assertRegex(resultado.stderr.lower(), erro)

    def test_fonte_bibliografica_e_chamada_mista_preservam_os_links(self) -> None:
        bibliografia = self.escrever_bibliografia()
        figura = self.objeto("fig", "alfa", "Esquema técnico").replace(
            'fonte="Equipe A & B (2026)."', 'fonte="Adaptado de @silva2023."'
        )
        tex = self.ler_tex(
            self.executar(
                "# Introdução\n\nReferência conjunta [@silva2023; @fig:alfa].\n" + figura,
                bibliografia=bibliografia,
            )
        )
        self.verificar_chamada(tex, "fig", "alfa", 1)
        self.assertIn("Fonte: Adaptado de Silva", self.normalizar(tex))
        self.assertGreaterEqual(len(re.findall(r"\\(?:hyperlink|citeproc)\{ref-silva2023\}", tex)), 2)

    def test_yaml_exige_objeto_references_em_vez_de_lista_raiz(self) -> None:
        caminho = self.escrever_bibliografia()
        (self.pasta / caminho).write_text(
            yaml.safe_dump([self.referencia], allow_unicode=True), encoding="utf-8"
        )
        resultado = self.executar(
            "Consultar @silva2023.\n", bibliografia=caminho, validar_apenas=True
        )
        self.assertNotEqual(resultado.returncode, 0, resultado.stdout)
        self.assertIn("references", resultado.stderr)
        self.assertFalse((self.pasta / "saida").exists())

    def test_csl_json_aceita_lista_raiz_e_resolve_as_citacoes(self) -> None:
        caminho = self.pasta / "referencias.json"
        caminho.write_text(json.dumps([self.referencia], ensure_ascii=False), encoding="utf-8")
        validacao = self.executar(
            "Consultar @silva2023.\n", bibliografia=caminho.name, validar_apenas=True
        )
        self.assertEqual(validacao.returncode, 0, validacao.stdout + validacao.stderr)
        self.assertFalse((self.pasta / "saida").exists())
        tex = self.ler_tex(
            self.executar("Consultar @silva2023.\n", bibliografia=caminho.name)
        )
        self.assertIn("Manual de inspeção mecânica", self.normalizar(tex))
        self.assertRegex(tex, r"\\(?:hyperlink|citeproc)\{ref-silva2023\}")
        self.assertNotIn("@silva2023", tex)

    def test_csl_json_rejeita_sintaxe_yaml_e_objeto_references(self) -> None:
        caminho = self.pasta / "referencias.json"
        casos = (
            ("sintaxe-yaml", yaml.safe_dump([self.referencia], allow_unicode=True), r"inválida"),
            ("objeto-references", json.dumps({"references": [self.referencia]}), r"lista"),
        )
        for nome, conteudo, erro in casos:
            with self.subTest(caso=nome):
                caminho.write_text(conteudo, encoding="utf-8")
                resultado = self.executar(
                    "Consultar @silva2023.\n",
                    bibliografia=caminho.name,
                    validar_apenas=True,
                )
                self.assertNotEqual(resultado.returncode, 0, resultado.stdout)
                self.assertRegex(resultado.stderr.lower(), erro)
                self.assertFalse((self.pasta / "saida").exists())

    def test_validar_apenas_resolve_citacao_e_objeto_sem_criar_saida(self) -> None:
        bibliografia = self.escrever_bibliografia()
        corpo = "Consultar @silva2023 e @fig:alfa.\n" + self.objeto("fig", "alfa", "Motor-bomba")
        resultado = self.executar(corpo, bibliografia=bibliografia, validar_apenas=True)
        self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)
        self.assertNotIn("[renderizar]", resultado.stdout)
        self.assertFalse((self.pasta / "saida").exists())

    def test_validar_apenas_rejeita_citacao_ou_objeto_ausente_sem_criar_saida(self) -> None:
        bibliografia = self.escrever_bibliografia()
        for identificador in ("naocadastrado2026", "fig:ausente"):
            with self.subTest(identificador=identificador):
                resultado = self.executar(
                    f"Consultar @{identificador}.\n",
                    bibliografia=bibliografia,
                    validar_apenas=True,
                )
                self.assertNotEqual(resultado.returncode, 0, resultado.stdout)
                self.assertIn(identificador, resultado.stderr)
                self.assertFalse((self.pasta / "saida").exists())

    def paginas_pdf(self, nome: str = "artigo") -> list[str]:
        texto = subprocess.check_output(
            ["pdftotext", "-layout", str(self.pasta / "saida" / f"{nome}.pdf"), "-"],
            text=True,
            timeout=30,
        )
        return [re.sub(r"\s+", " ", pagina) for pagina in texto.split("\f") if pagina.strip()]

    @unittest.skipUnless(
        all(shutil.which(ferramenta) for ferramenta in ("xelatex", "pdftotext", "pdfinfo")),
        "XeLaTeX e Poppler necessários para conferir destinos no PDF",
    )
    def test_destino_da_figura_acompanha_legenda_ao_mudar_de_pagina(self) -> None:
        figura = self.objeto("fig", "alfa", "Figura de destino", nota=True).replace(
            "width=25%", "width=80%"
        )
        # O espaço restante comporta a âncora, mas não a caixa da figura.
        # Assim, a caixa quebra naturalmente depois de uma chamada na página 1.
        corpo = (
            "Chamada de prova: @fig:alfa.\n\n"
            "```{=latex}\n\\par\\vspace*{0.62\\textheight}\n```\n"
            + figura
        )
        resultado = self.executar(corpo, formato="pdf")
        self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)
        paginas = self.paginas_pdf()
        self.assertIn("Chamada de prova: Figura 1", paginas[0])
        pagina_da_legenda = [
            indice for indice, pagina in enumerate(paginas, 1) if "Figura de destino" in pagina
        ]
        self.assertEqual(pagina_da_legenda, [2])
        destinos = subprocess.check_output(
            ["pdfinfo", "-dests", str(self.pasta / "saida" / "artigo.pdf")],
            text=True,
            timeout=30,
        )
        linhas = [linha for linha in destinos.splitlines() if '"fig:alfa"' in linha]
        self.assertEqual(len(linhas), 1, destinos)
        numero = re.match(r"\s*(\d+)\s", linhas[0])
        self.assertIsNotNone(numero, destinos)
        self.assertEqual(int(numero.group(1)), pagina_da_legenda[0])

    @unittest.skipUnless(
        all(shutil.which(ferramenta) for ferramenta in ("xelatex", "pdftotext")),
        "XeLaTeX e pdftotext necessários para conferir agrupamento da tabela",
    )
    def test_tabela_curta_mantem_legenda_dados_fonte_e_nota_na_mesma_pagina(self) -> None:
        tabela = self.objeto("tab", "alfa", "Dados concentrados", nota=True).replace(
            '.tabela #tab:alfa', '.tabela #tab:alfa manter_junto="true"'
        ).replace(
            "| Desvio | 0,18 mm |",
            "| Medição alfa | 0,18 mm |\n| Medição beta | 0,12 mm |\n| Medição gama | 0,07 mm |",
        )
        corpo = (
            "Chamada da tabela: @tab:alfa.\n\n"
            "```{=latex}\n\\par\\vspace*{0.72\\textheight}\n```\n"
            + tabela
        )
        resultado = self.executar(corpo, formato="pdf")
        self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)
        paginas = self.paginas_pdf()
        self.assertIn("Chamada da tabela: Tabela 1", paginas[0])
        partes = (
            "Tabela 1 — Dados concentrados",
            "Medição alfa",
            "Medição beta",
            "Medição gama",
            "Fonte: Equipe A & B (2026).",
            "Nota: Exemplo didático & verificável.",
        )
        posicoes = []
        for parte in partes:
            encontrados = [indice for indice, pagina in enumerate(paginas, 1) if parte in pagina]
            self.assertEqual(len(encontrados), 1, (parte, paginas))
            posicoes.append(encontrados[0])
        self.assertEqual(set(posicoes), {2})

    @unittest.skipUnless(
        all(shutil.which(ferramenta) for ferramenta in ("xelatex", "pdftotext")),
        "XeLaTeX e pdftotext necessários para integração PDF",
    )
    def test_pdf_resolve_citacoes_objetos_e_numeros_sem_interrogacoes(self) -> None:
        bibliografia = self.escrever_bibliografia()
        corpo = (
            "# Introdução\n\nSegundo @silva2023, o registro deve ser verificável. "
            "Confira também [@silva2023, p. 17].\n\n"
            "Elementos: @fig:alfa, @gra:alfa, @tab:alfa e @eq:alfa.\n"
            + "".join(
                self.objeto(tipo, "alfa", f"Elemento {tipo} didático", nota=True)
                for tipo in ("fig", "gra", "tab", "eq")
            )
        )
        resultado = self.executar(corpo, formato="tex,pdf", bibliografia=bibliografia)
        tex = self.ler_tex(resultado)
        for tipo in ("fig", "gra", "tab", "eq"):
            self.verificar_chamada(tex, tipo, "alfa", 1)
        texto = subprocess.check_output(
            ["pdftotext", "-layout", str(self.pasta / "saida" / "artigo.pdf"), "-"],
            text=True,
            timeout=30,
        )
        texto = re.sub(r"\s+", " ", texto)
        self.assertNotIn("?", texto)
        self.assertNotIn("@silva2023", texto)
        self.assertRegex(texto, r"Silva\s*\(2023\)")
        self.assertRegex(texto, r"\(Silva,\s*2023,\s*p\.\s*17\)")
        for chamada in ("Figura 1", "Gráfico 1", "Tabela 1", "Equação (1)"):
            self.assertIn(chamada, texto)
        self.assertIn("Manual de inspeção mecânica", texto)
        self.assertIn("Fonte: Equipe A & B (2026).", texto)


if __name__ == "__main__":
    unittest.main()
