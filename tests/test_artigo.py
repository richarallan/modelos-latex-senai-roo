from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

from scripts import renderizar


class ModeloArtigoTestes(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = renderizar.ler_schema()
        cls.exemplo = renderizar.carregar_documento(
            renderizar.RAIZ / "exemplos" / "nota-aula-metrologia.md"
        )

    def documento(self, **alteracoes: object) -> renderizar.Documento:
        metadados = {**self.exemplo.metadados, "modelo": "artigo", **alteracoes}
        return renderizar.Documento(
            caminho=self.exemplo.caminho,
            metadados=metadados,
            corpo="# Introdução\n\nConteúdo de exemplo.\n",
        )

    def test_artigo_e_apresentacao_dos_dois_tipos_existentes(self) -> None:
        for tipo in ("nota_aula", "atividade_avaliativa"):
            with self.subTest(tipo=tipo):
                renderizar.validar_metadados(
                    self.documento(tipo_documento=tipo), self.schema
                )
        with self.assertRaisesRegex(renderizar.ErroDocumento, "tipo_documento"):
            renderizar.validar_metadados(
                self.documento(tipo_documento="artigo"), self.schema
            )

    def test_modelo_e_metadados_de_artigo_invalidos_sao_rejeitados(self) -> None:
        for campo, valor in (
            ("modelo", "inexistente"),
            ("resumo", ["Não é um texto"]),
            ("email", 123),
            ("palavras_chave", "metrologia"),
            ("pre_textuais", "false"),
            ("banca", "Uma pessoa"),
        ):
            with self.subTest(campo=campo):
                with self.assertRaisesRegex(renderizar.ErroDocumento, campo):
                    renderizar.validar_metadados(
                        self.documento(**{campo: valor}), self.schema
                    )

    def test_formato_padrao_gera_tex_e_pdf_sem_antecipar_word(self) -> None:
        argumentos = renderizar.criar_parser().parse_args([])
        self.assertEqual(
            renderizar.interpretar_formatos(argumentos.formato), ("tex", "pdf")
        )
        self.assertEqual(
            renderizar.interpretar_formatos("todos"), ("tex", "pdf", "docx")
        )

    def test_comando_do_artigo_seleciona_template_e_xelatex(self) -> None:
        documento = self.documento()
        template = renderizar.RAIZ / "templates" / "artigo" / "artigo.latex"
        for formato in ("tex", "pdf"):
            with self.subTest(formato=formato):
                comando = renderizar.comando_pandoc(
                    "pandoc", documento, formato, Path(f"artigo.{formato}")
                )
                self.assertIn(f"--template={template}", comando)
                self.assertNotIn("--toc", comando)
                if formato == "pdf":
                    self.assertIn("--pdf-engine=xelatex", comando)

    def test_tipos_existentes_preservam_template_padrao_e_word(self) -> None:
        for nome in ("atividade-usinagem.md", "nota-aula-metrologia.md"):
            documento = renderizar.carregar_documento(
                renderizar.RAIZ / "exemplos" / nome
            )
            with self.subTest(documento=nome):
                comando_pdf = renderizar.comando_pandoc(
                    "pandoc", documento, "pdf", Path("saida.pdf")
                )
                self.assertIn("--variable=documentclass:senaiarticle", comando_pdf)
                self.assertIn("--pdf-engine=xelatex", comando_pdf)
                self.assertIn("--toc", comando_pdf)
                self.assertFalse(any(c.startswith("--template=") for c in comando_pdf))
                comando_docx = renderizar.comando_pandoc(
                    "pandoc", documento, "docx", Path("saida.docx")
                )
                self.assertIn("--to=docx", comando_docx)
                self.assertIn(
                    f"--reference-doc={renderizar.REFERENCE_DOCX}", comando_docx
                )

    def escrever(self, diretorio: Path, nome: str, documento: renderizar.Documento) -> Path:
        caminho = diretorio / nome
        caminho.write_text(
            "---\n"
            + yaml.safe_dump(documento.metadados, allow_unicode=True, sort_keys=False)
            + "---\n"
            + documento.corpo,
            encoding="utf-8",
        )
        return caminho

    def executar(self, *argumentos: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "scripts/renderizar.py", *argumentos],
            cwd=renderizar.RAIZ,
            env=renderizar.ambiente_compilacao(),
            text=True,
            capture_output=True,
            timeout=60,
        )

    def test_word_do_artigo_e_rejeitado_antes_de_saidas_parciais_no_lote(self) -> None:
        # O documento legado vem primeiro para detectar validação tardia por arquivo.
        with tempfile.TemporaryDirectory() as temporario:
            pasta = Path(temporario)
            artigo = self.escrever(pasta, "artigo.md", self.documento())
            for formatos in ("tex,docx", "todos"):
                with self.subTest(formatos=formatos):
                    resultado = self.executar(
                        str(self.exemplo.caminho),
                        str(artigo),
                        "--formato",
                        formatos,
                        "--saida",
                        str(pasta / "saida"),
                    )
                    self.assertNotEqual(resultado.returncode, 0, resultado.stdout)
                    self.assertRegex(resultado.stderr.lower(), r"artigo.*docx|docx.*artigo")
                    self.assertEqual(list((pasta / "saida").rglob("*")), [])

    @unittest.skipUnless(shutil.which("pandoc"), "Pandoc necessário para integração")
    def test_tex_real_usa_classe_existente_e_escapa_metadados(self) -> None:
        documento = self.documento(
            titulo="Torque & rotação: medição a 50% no eixo_A",
            autor="João & Maria",
            resumo="Análise de medição & inspeção com erro de 5%.",
            palavras_chave=["metrologia", "eixo_A"],
            email="autor@example.com",
        )
        documento = renderizar.Documento(
            documento.caminho,
            documento.metadados,
            documento.corpo
            + "\n::: objetivo\nRegistrar a medição com segurança.\n:::\n"
            + "\n| Grandeza | Valor |\n|---|---|\n| Torque | 5 N m |\n",
        )
        with tempfile.TemporaryDirectory() as temporario:
            pasta = Path(temporario)
            entrada = self.escrever(pasta, "artigo.md", documento)
            resultado = self.executar(
                str(entrada), "--formato", "tex", "--saida", str(pasta / "saida")
            )
            self.assertEqual(
                resultado.returncode, 0, resultado.stdout + resultado.stderr
            )
            tex = (pasta / "saida" / "artigo.tex").read_text(encoding="utf-8")
            self.assertRegex(
                tex, r"(?s)\\documentclass\s*\[[^\]]*\bartigo\b[^\]]*\]\s*\{senaiarticle\}"
            )
            compacto = re.sub(r"\s+", " ", tex)
            self.assertIn(r"Torque \& rotação", compacto)
            self.assertIn(r"50\%", compacto)
            self.assertIn(r"eixo\_A", compacto)
            self.assertIn(r"João \& Maria", compacto)
            self.assertIn(r"medição \& inspeção", compacto)
            self.assertIn(r"\begin{senaiobjetivo}", tex)
            self.assertIn(r"\begin{longtable}", tex)
            self.assertNotIn(r"\tableofcontents", tex)

    @unittest.skipUnless(
        all(shutil.which(ferramenta) for ferramenta in ("pandoc", "xelatex", "pdftotext")),
        "Pandoc, XeLaTeX e pdftotext necessários para integração PDF",
    )
    def test_pdf_real_preserva_texto_e_tres_paginas_pre_textuais_opcionais(self) -> None:
        documento = self.documento(
            titulo="Torque & rotação: medição a 50% no eixo_A",
            autor="João & Maria",
            resumo="Análise de medição & inspeção com erro de 5%.",
            palavras_chave=["metrologia", "eixo_A"],
            email="joao_silva+artigo@example.com",
        )
        textos: dict[bool, str] = {}
        paginas: dict[bool, int] = {}
        with tempfile.TemporaryDirectory() as temporario:
            pasta = Path(temporario)
            for pre_textuais in (True, False):
                with self.subTest(pre_textuais=pre_textuais):
                    nome = "com-pre-textuais" if pre_textuais else "sem-pre-textuais"
                    entrada = self.escrever(
                        pasta,
                        f"{nome}.md",
                        renderizar.Documento(
                            documento.caminho,
                            {**documento.metadados, "pre_textuais": pre_textuais},
                            documento.corpo + "\nTexto com ~~registro antigo~~ revisado.\n",
                        ),
                    )
                    resultado = self.executar(
                        str(entrada),
                        "--formato",
                        "pdf",
                        "--saida",
                        str(pasta / "saida"),
                    )
                    self.assertEqual(
                        resultado.returncode, 0, resultado.stdout + resultado.stderr
                    )
                    pdf = pasta / "saida" / f"{nome}.pdf"
                    texto = subprocess.check_output(
                        ["pdftotext", "-layout", str(pdf), "-"],
                        text=True,
                        timeout=30,
                    )
                    paginas[pre_textuais] = texto.count("\f")
                    textos[pre_textuais] = re.sub(r"\s+", " ", texto.casefold())
            self.assertEqual(set(paginas), {True, False})
            self.assertEqual(paginas[True], paginas[False] + 3)
            for texto in textos.values():
                self.assertIn("resumo", texto)
                self.assertIn("conteúdo de exemplo", texto)
                self.assertIn("registro antigo", texto)
                self.assertIn("torque & rotação", texto)
                self.assertIn("50% no eixo_a", texto)
                self.assertIn("joão & maria", texto)
                self.assertIn("medição & inspeção com erro de 5%", texto)
                self.assertIn("joao_silva+artigo@example.com", texto)
                self.assertNotIn("sumário", texto)
            self.assertIn("termo de aprovação", textos[True])
            self.assertNotIn("termo de aprovação", textos[False])


if __name__ == "__main__":
    unittest.main()
