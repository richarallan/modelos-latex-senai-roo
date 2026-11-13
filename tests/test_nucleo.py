"""Contrato comum dos perfis, interpretação semântica e saídas reais.

Os documentos usam autoria coletiva e a referência real JCGM 200:2012.
As integrações são executadas também com o Pandoc 3.1.3 pelo CI.
"""

from __future__ import annotations

import hashlib
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any, Iterator

import yaml

from scripts import renderizar


def nos_ast(valor: Any) -> Iterator[dict[str, Any]]:
    if isinstance(valor, dict):
        if "t" in valor:
            yield valor
        for filho in valor.values():
            yield from nos_ast(filho)
    elif isinstance(valor, list):
        for filho in valor:
            yield from nos_ast(filho)


def objetos_ast(ir: dict[str, Any]) -> dict[str, dict[str, str]]:
    objetos = {}
    for no in nos_ast(ir["blocks"]):
        if no["t"] == "Div":
            identificador, _, pares = no["c"][0]
            atributos = dict(pares)
            if "senai-tipo" in atributos:
                objetos[identificador] = atributos
    return objetos


@unittest.skipUnless(shutil.which("pandoc"), "Pandoc necessário para testar o núcleo")
class NucleoDocumentalTestes(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.pandoc = shutil.which("pandoc")
        cls.base = dict(renderizar.carregar_documento(
            renderizar.RAIZ / "exemplos" / "nota-aula-metrologia.md"
        ).metadados)
        cls.base.update(autor="Equipe de elaboração", titulo="Demonstração do núcleo")

    def setUp(self) -> None:
        self.temporario = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporario.cleanup)
        self.pasta = Path(self.temporario.name)
        shutil.copyfile(
            renderizar.RAIZ / "templates" / "artigo" / "recursos" / "logo-senai.png",
            self.pasta / "imagem.png",
        )
        referencias = yaml.safe_load((
            renderizar.RAIZ / "exemplos" / "referencias" / "artigo.yaml"
        ).read_text(encoding="utf-8"))["references"]
        (self.pasta / "referencias.yaml").write_text(
            yaml.safe_dump({"references": referencias[:1]}, allow_unicode=True),
            encoding="utf-8",
        )

    def documento(self, corpo: str, **metadados: Any) -> renderizar.Documento:
        if metadados.get("modelo") == "atividade_avaliativa":
            metadados.setdefault("tipo_documento", "atividade_avaliativa")
        return renderizar.Documento(
            self.pasta / "entrada.md", {**self.base, **metadados}, corpo
        )

    def escrever(self, corpo: str, nome: str = "entrada", **metadados: Any) -> Path:
        if metadados.get("modelo") == "atividade_avaliativa":
            metadados.setdefault("tipo_documento", "atividade_avaliativa")
        caminho = self.pasta / f"{nome}.md"
        caminho.write_text(
            "---\n" + yaml.safe_dump(
                {**self.base, **metadados}, allow_unicode=True, sort_keys=False
            ) + "---\n" + corpo,
            encoding="utf-8",
        )
        return caminho

    def executar(self, entrada: Path, formato: str = "tex", *, validar: bool = False):
        comando = [sys.executable, "scripts/renderizar.py", str(entrada),
                   "--formato", formato, "--saida", str(self.pasta / "saida")]
        if validar:
            comando.append("--validar-apenas")
        return subprocess.run(
            comando, cwd=renderizar.RAIZ, env=renderizar.ambiente_compilacao(),
            text=True, capture_output=True, timeout=120,
        )

    def interpretar(self, corpo: str, **metadados: Any) -> dict[str, Any]:
        from nucleo.geracao import interpretar_documento
        return interpretar_documento(self.pandoc, self.documento(corpo, **metadados))

    @staticmethod
    def figura(identificador: str, classe: str = "figura") -> str:
        return (f'\n::: {{.{classe} identificador="fig:{identificador}" '
                'titulo="Esquema de demonstração" arquivo="imagem.png" '
                'fonte="Equipe de elaboração." idioma="pt-BR"}\n:::\n')

    def test_perfis_consumem_a_mesma_ir_sem_reinterpretar_conteudo(self) -> None:
        from nucleo.perfis import carregar_perfil
        corpo = ("# Procedimento {#sec:procedimento}\n\n"
                 "Leia a @fig:conjunto e [retorne à seção](#sec:procedimento).\n"
                 + self.figura("conjunto"))
        representacoes = []
        for modelo in ("artigo", "nota_aula", "atividade_avaliativa", "relatorio"):
            with self.subTest(modelo=modelo):
                documento = self.documento(corpo, modelo=modelo)
                perfil = carregar_perfil(documento)
                self.assertEqual(perfil.id, modelo)
                self.assertTrue({"tex", "pdf"}.issubset(set(perfil.formatos)))
                representacoes.append(self.interpretar(corpo, modelo=modelo)["blocks"])
        self.assertEqual(len(representacoes), 4)
        for representacao in representacoes[1:]:
            self.assertEqual(representacoes[0], representacao)

    def test_ir_preserva_markdown_nativo_e_cobre_catalogo_sem_latex_gerado(self) -> None:
        corpo = (
            "# Procedimento {#sec:inicio}\n\nParágrafo com **ênfase** e `código`.\n\n"
            "- Preparar.\n- Conferir.\n\n1. Registrar.\n2. Revisar.\n\n"
            "> Evidência em citação de bloco.\n\n"
            "```text\nregistro verificável\n```\n\n"
            "Expressão $x=1$; nota[^nota].\n\n[^nota]: Explicação técnica.\n\n"
            "Segundo @jcgm2012, há uma referência [@jcgm2012, p. 2].\n\n"
            "[Voltar](#sec:inicio). Objetos: @fig:conjunto, @gra:dados, "
            "@tab:dados e @eq:calculo.\n"
            + self.figura("conjunto")
            + self.figura("ilustracao", "ilustracao")
            + self.figura("desenho", "desenho")
            + '\n::: {.grafico identificador="gra:dados" titulo="Dados simulados" '
              'arquivo="imagem.png" fonte="Equipe de elaboração."}\n:::\n'
            + '\n::: {.tabela identificador="tab:dados" titulo="Valores simulados" '
              'fonte="Equipe de elaboração." nota="Sem medição de campo."}\n'
              '| Item | Valor |\n|---|---:|\n| A | 1 |\n:::\n'
            + '\n::: {.equacao identificador="eq:calculo"}\n$$\nx = 1 + 2\n$$\n:::\n'
            + "\n:::: {.painel-imagens colunas=2}\n"
            + self.figura("painel-a") + self.figura("painel-b") + "\n::::\n"
        )
        for classe in ("objetivo", "situacao_problema", "questao", "seguranca",
                       "pratica", "rubrica", "atencao"):
            corpo += f"\n::: {{.{classe}}}\nEvidência de {classe}.\n:::\n"
        ir = self.interpretar(corpo, bibliografia="referencias.yaml")
        tipos = {no["t"] for no in nos_ast(ir["blocks"])}
        self.assertTrue({"Header", "Para", "BulletList", "OrderedList", "Strong",
                         "BlockQuote", "Code", "CodeBlock", "Math", "Note", "Cite",
                         "Link", "Image", "Table"}.issubset(tipos), tipos)
        self.assertFalse(any(no["t"] in {"RawBlock", "RawInline"}
                             and no["c"][0] in {"latex", "tex"}
                             for no in nos_ast(ir["blocks"])))
        objetos = objetos_ast(ir)
        self.assertEqual(set(objetos), {"fig:conjunto", "fig:ilustracao", "fig:desenho",
                                       "fig:painel-a", "fig:painel-b", "gra:dados",
                                       "tab:dados", "eq:calculo"})
        self.assertEqual(objetos["fig:desenho"]["senai-numero"], "3")
        self.assertEqual(objetos["gra:dados"]["senai-numero"], "1")
        pedagogicos = {
            dict(no["c"][0][2])["senai-pedagogico"]
            for no in nos_ast(ir["blocks"])
            if no["t"] == "Div" and "senai-pedagogico" in dict(no["c"][0][2])
        }
        self.assertEqual(pedagogicos, {"objetivo", "situacao_problema", "questao",
                                      "seguranca", "pratica", "rubrica", "atencao"})

    def test_identificador_chave_valor_renumera_apos_reordenar(self) -> None:
        for ordem in (("a", "b"), ("b", "a"), ("novo", "b", "a")):
            with self.subTest(ordem=ordem):
                ir = self.interpretar("Consultar @fig:a e @fig:b.\n" + "".join(
                    self.figura(identificador) for identificador in ordem
                ))
                objetos = objetos_ast(ir)
                for identificador in ordem:
                    self.assertEqual(objetos[f"fig:{identificador}"]["senai-numero"],
                                     str(ordem.index(identificador) + 1))

    def test_identificadores_duplicados_e_conflitantes_tem_diagnostico(self) -> None:
        casos = (
            ("# Primeiro {#sec:igual}\n\n# Segundo {#sec:igual}\n", "sec:igual"),
            (self.figura("igual") + self.figura("igual"), "fig:igual"),
            (self.figura("a").replace('.figura ', '.figura #fig:outro '), "identifica"),
        )
        for corpo, diagnostico in casos:
            with self.subTest(diagnostico=diagnostico):
                resultado = self.executar(self.escrever(corpo), validar=True)
                self.assertNotEqual(resultado.returncode, 0)
                self.assertIn(diagnostico, resultado.stderr)
                self.assertFalse((self.pasta / "saida").exists())

    def test_destinos_inexistentes_e_chamadas_ausentes_sao_rejeitados(self) -> None:
        for corpo, destino in (("[Seção](#sec:ausente).", "sec:ausente"),
                                ("Consultar @fig:ausente.", "fig:ausente"),
                                ("Consultar @referencia_ausente.", "referencia_ausente")):
            with self.subTest(destino=destino):
                resultado = self.executar(self.escrever(corpo), validar=True)
                self.assertNotEqual(resultado.returncode, 0)
                self.assertIn(destino, resultado.stderr)

    def test_arquivos_ausentes_cobrem_atributos_e_markdown_por_referencia(self) -> None:
        corpos = (
            self.figura("ausente").replace("imagem.png", "arquivo-ausente.png"),
            "![Evidência][recurso]\n\n[recurso]: arquivo-ausente.png\n",
            "![Evidência](<pasta com espaço/arquivo-ausente.png>)\n",
        )
        for corpo in corpos:
            with self.subTest(corpo=corpo):
                resultado = self.executar(self.escrever(corpo), validar=True)
                self.assertNotEqual(resultado.returncode, 0)
                self.assertIn("arquivo-ausente.png", resultado.stderr)

    def test_metadados_invalidos_identificam_campo_e_nao_criam_saidas(self) -> None:
        casos = (("titulo", "   "), ("autor", []), ("idioma", "idioma-invalido"),
                 ("resumo", ["Tipo incorreto"]), ("carga_horaria", "cinco horas"),
                 ("titulo_digitado_errado", "Conteúdo"))
        for campo, valor in casos:
            with self.subTest(campo=campo):
                resultado = self.executar(self.escrever("Conteúdo.\n", **{campo: valor}),
                                         validar=True)
                self.assertNotEqual(resultado.returncode, 0)
                self.assertIn(campo, resultado.stderr)
                self.assertFalse((self.pasta / "saida").exists())

    def test_todos_os_campos_obrigatorios_tem_mensagem_identificavel(self) -> None:
        obrigatorios = ("versao_schema", "tipo_documento", "titulo", "autor", "instituicao",
                        "unidade_operacional", "unidade_curricular", "publico", "carga_horaria")
        schema = renderizar.ler_schema()
        for campo in obrigatorios:
            with self.subTest(campo=campo):
                metadados = dict(self.base)
                metadados.pop(campo)
                documento = renderizar.Documento(self.pasta / "entrada.md", metadados, "Conteúdo.")
                with self.assertRaisesRegex(renderizar.ErroDocumento, campo):
                    renderizar.validar_metadados(documento, schema)

    def test_idioma_dos_metadados_governa_apresentacao(self) -> None:
        for idioma, babel in (("pt-BR", "brazilian"), ("en", "english"), ("es", "spanish")):
            with self.subTest(idioma=idioma):
                entrada = self.escrever("# Registro\n\nConteúdo.\n", modelo="artigo",
                                        pre_textuais=False, idioma=idioma)
                resultado = self.executar(entrada)
                self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)
                tex = (self.pasta / "saida" / "entrada.tex").read_text(encoding="utf-8")
                self.assertIn(r"\babelprovide[main,import]{" + babel + "}", tex)
                self.assertIn("pdflang={" + idioma + "}", tex)

    def test_idioma_do_elemento_nao_reimporta_o_idioma_principal(self) -> None:
        for idioma, babel in (("pt-BR", "brazilian"), ("en", "english"), ("es", "spanish")):
            for modelo in ("artigo", "nota_aula", "atividade_avaliativa", "relatorio"):
                with self.subTest(idioma=idioma, modelo=modelo):
                    corpo = self.figura("idioma").replace('idioma="pt-BR"', f'idioma="{idioma}"')
                    entrada = self.escrever(corpo, modelo=modelo, idioma=idioma, pre_textuais=False)
                    resultado = self.executar(entrada)
                    self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)
                    tex = (self.pasta / "saida" / "entrada.tex").read_text(encoding="utf-8")
                    importados = re.findall(r"\\babelprovide(?:\[[^\]]*\])?\{([^}]+)\}", tex)
                    self.assertEqual(importados.count(babel), 1, tex)
                    ir = self.interpretar(corpo, modelo=modelo, idioma=idioma)
                    self.assertIn(["idioma", idioma], next(
                        no["c"][0][2] for no in nos_ast(ir["blocks"])
                        if no["t"] == "Div" and no["c"][0][0] == "fig:idioma"
                    ))

    def test_opcionais_vazios_sao_omitidos_ao_carregar_sem_ocultar_obrigatorios(self) -> None:
        entrada = self.escrever("Conteúdo.\n", resumo="  ", subtitulo="", local=None,
                                palavras_chave=[], orientador="\t", banca=[])
        documento = renderizar.carregar_documento(entrada)
        for campo in ("resumo", "subtitulo", "local", "palavras_chave", "orientador", "banca"):
            self.assertNotIn(campo, documento.metadados)
        entrada = self.escrever("Conteúdo.\n", titulo=" ")
        resultado = self.executar(entrada, validar=True)
        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn("titulo", resultado.stderr)

    def test_listas_vazias_nao_ocultam_tipos_invalidos_de_metadados(self) -> None:
        for campo in ("idioma", "modelo", "pre_textuais", "resumo", "email"):
            with self.subTest(campo=campo):
                entrada = self.escrever("Conteúdo.\n", **{campo: []})
                resultado = self.executar(entrada, validar=True)
                self.assertNotEqual(resultado.returncode, 0)
                self.assertIn(campo, resultado.stderr)
                self.assertFalse((self.pasta / "saida").exists())

    def test_citacao_invalida_no_lote_impede_saida_parcial_do_primeiro_documento(self) -> None:
        valido = self.escrever("Registro válido.\n", nome="valido")
        invalido = self.escrever("Consultar @referencia_ausente.\n", nome="invalido")
        resultado = subprocess.run(
            [sys.executable, "scripts/renderizar.py", str(valido), str(invalido),
             "--formato", "tex", "--saida", str(self.pasta / "saida")],
            cwd=renderizar.RAIZ, env=renderizar.ambiente_compilacao(),
            text=True, capture_output=True, timeout=60,
        )
        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn("referencia_ausente", resultado.stderr)
        self.assertFalse((self.pasta / "saida").exists(),
                         "Todo o lote deve ser validado antes da primeira gravação")

    def test_link_para_referencia_exige_destino_efetivamente_emitido(self) -> None:
        entrada = self.escrever("[Obra não citada](#ref-jcgm2012).\n",
                                bibliografia="referencias.yaml")
        resultado = self.executar(entrada, validar=True)
        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn("ref-jcgm2012", resultado.stderr)
        entrada = self.escrever("Consultar @jcgm2012 e [obra citada](#ref-jcgm2012).\n",
                                bibliografia="referencias.yaml")
        resultado = self.executar(entrada, validar=True)
        self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)
        self.assertFalse((self.pasta / "saida").exists())

    def test_arquivo_que_aponta_para_diretorio_e_rejeitado(self) -> None:
        (self.pasta / "diretorio.png").mkdir()
        entrada = self.escrever(self.figura("diretorio").replace("imagem.png", "diretorio.png"))
        resultado = self.executar(entrada, validar=True)
        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn("diretorio.png", resultado.stderr)

    def test_atributos_invalidos_indicam_o_elemento(self) -> None:
        casos = (
            (self.figura("idioma").replace('idioma="pt-BR"', 'idioma="idioma inválido!"'), "idioma"),
            ('::: {.painel-imagens colunas=5}\n' + self.figura("a")
             + self.figura("b") + ":::\n", "colunas"),
            ('::: {.tabela identificador="tab:valor" titulo="Valor" fonte="Equipe." '
             'manter_junto="talvez"}\n| Item | Valor |\n|---|---|\n| A | 1 |\n:::\n',
             "manter_junto"),
        )
        for corpo, campo in casos:
            with self.subTest(campo=campo):
                resultado = self.executar(self.escrever(corpo), validar=True)
                self.assertNotEqual(resultado.returncode, 0)
                self.assertIn(campo, resultado.stderr)

    def test_blocos_pedagogicos_vazios_nao_geram_rotulos(self) -> None:
        corpo = "# Registro\n\nTexto presente.\n\n" + "\n".join(
            f"::: {{.{classe}}}\n:::\n" for classe in (
                "objetivo", "situacao_problema", "questao", "seguranca",
                "pratica", "rubrica", "atencao")
        )
        ir = self.interpretar(corpo)
        self.assertFalse(any(
            no["t"] == "Div" and "senai-pedagogico" in dict(no["c"][0][2])
            for no in nos_ast(ir["blocks"])
        ))

    def test_questao_aceita_pontos_inteiros_decimais_e_rejeita_valores_invalidos(self) -> None:
        for pontos in ("2", "2,5"):
            with self.subTest(pontos=pontos):
                corpo = ('[Consulte a questão](#q:registro).\n\n'
                         f'::: {{.questao identificador="q:registro" pontos="{pontos}" tipo="registro"}}\n'
                         'Registre a leitura e explique o resultado.\n:::\n')
                ir = self.interpretar(corpo)
                questoes = [no for no in nos_ast(ir["blocks"])
                            if no["t"] == "Div" and no["c"][0][0] == "q:registro"]
                self.assertEqual(len(questoes), 1)
                atributos = dict(questoes[0]["c"][0][2])
                self.assertEqual(atributos["senai-pedagogico"], "questao")
                self.assertEqual(atributos["pontos"], pontos)
        for pontos in ("abc", "-1"):
            with self.subTest(pontos=pontos):
                entrada = self.escrever(
                    f'::: {{.questao identificador="q:registro" pontos="{pontos}"}}\n'
                    'Registre a leitura.\n:::\n'
                )
                resultado = self.executar(entrada, validar=True)
                self.assertNotEqual(resultado.returncode, 0)
                self.assertIn("pontos", resultado.stderr)
                self.assertIn("q:registro", resultado.stderr)

    @unittest.skipUnless(
        all(shutil.which(item) for item in ("xelatex", "pdftotext", "pdfinfo")),
        "XeLaTeX e Poppler necessários para integração PDF",
    )
    def test_pdf_dos_perfis_resolve_objetos_tabelas_e_citacoes(self) -> None:
        corpo = (
            "# Registro {#sec:registro}\n\n"
            "Segundo @jcgm2012, conferir [@jcgm2012, p. 2].\n\n"
            "Consultar @fig:conjunto, @gra:dados, @tab:valores e @eq:calculo. "
            "[Retornar ao registro](#sec:registro).\n"
            + self.figura("conjunto")
            + '\n::: {.grafico identificador="gra:dados" titulo="Leituras simuladas" '
              'arquivo="imagem.png" fonte="Equipe de elaboração."}\n:::\n'
            + '\n::: {.tabela identificador="tab:valores" titulo="Dados simulados" '
              'fonte="Equipe de elaboração." nota="Sem coleta de campo."}\n'
              '| Item | Valor |\n|---|---:|\n| Medição | 2 |\n:::\n'
            + '\n::: {.equacao identificador="eq:calculo"}\n$$\nx = 1 + 1\n$$\n:::\n'
            + '\n[Consulte a questão](#q:registro).\n\n'
              '::: {.questao identificador="q:registro" pontos="2" tipo="registro"}\n'
              'Registre a leitura.\n:::\n'
        )
        for modelo in ("artigo", "nota_aula", "atividade_avaliativa", "relatorio"):
            with self.subTest(modelo=modelo):
                entrada = self.escrever(corpo, nome=modelo, modelo=modelo,
                                        pre_textuais=False, bibliografia="referencias.yaml")
                resultado = self.executar(entrada, "tex,pdf")
                self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)
                pdf = self.pasta / "saida" / f"{modelo}.pdf"
                texto = re.sub(r"\s+", " ", subprocess.check_output(
                    ["pdftotext", "-layout", str(pdf), "-"], text=True, timeout=30,
                ))
                for trecho in ("Figura 1", "Gráfico 1", "Tabela 1", "Equação (1)", "Dados simulados",
                               "Fonte: Equipe de elaboração.", "Nota: Sem coleta de campo.",
                               "International vocabulary of metrology"):
                    self.assertIn(trecho, texto)
                self.assertRegex(texto, r"JCGM\s*\(2012\)")
                self.assertRegex(texto, r"\(JCGM,\s*2012,\s*p\.\s*2\)")
                self.assertNotIn("?", texto)
                self.assertNotIn("@jcgm", texto)
                destinos = subprocess.check_output(
                    ["pdfinfo", "-dests", str(pdf)], text=True, timeout=30,
                )
                for destino in ("fig:conjunto", "gra:dados", "tab:valores", "eq:calculo", "q:registro"):
                    self.assertIn(destino, destinos)
                tex = pdf.with_suffix(".tex").read_text(encoding="utf-8")
                self.assertIn(r"\label{sec:registro}", tex)
                self.assertRegex(tex, r"\\(?:hyperref\[sec:registro\]|hyperlink\{sec:registro\})")

    @unittest.skipUnless(
        all(shutil.which(item) for item in ("xelatex", "pdftotext")),
        "XeLaTeX e Poppler necessários para conferir opcionais no PDF",
    )
    def test_pdf_artigo_sem_opcionais_nao_cria_aprovacao_nem_rotulos_vazios(self) -> None:
        entrada = self.escrever("# Registro\n\nConteúdo presente.\n", modelo="artigo",
                                resumo="", palavras_chave=[], orientador="", coordenacao="",
                                banca=[], data_aprovacao="", local="", data="", aprovacao=True)
        resultado = self.executar(entrada, "pdf")
        self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)
        texto = subprocess.check_output(
            ["pdftotext", "-layout", str(self.pasta / "saida" / "entrada.pdf"), "-"],
            text=True, timeout=30,
        )
        self.assertEqual(texto.count("\f"), 3, "Capa, rosto e corpo; aprovação ausente")
        for ausente in ("TERMO DE APROVAÇÃO", "Orientador(a):", "Coordenação pedagógica:",
                        "BANCA EXAMINADORA", "Membro da banca", "Resultado final:",
                        "Palavras-chave:", "RESUMO"):
            self.assertNotIn(ausente, texto)
        self.assertIn("Conteúdo presente.", texto)

    def test_pdf_artigo_aprovado_permanece_como_referencia_de_regressao(self) -> None:
        referencia = renderizar.RAIZ / "exemplos" / "artigo-exemplo.pdf"
        self.assertEqual(hashlib.sha256(referencia.read_bytes()).hexdigest(),
                         "1ff1e928324819361c3c00c45f1b8471d9e1150b5609a7505b9a74d37255bafd")


if __name__ == "__main__":
    unittest.main()
