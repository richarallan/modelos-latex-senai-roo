# Modelos LaTeX SENAI Rondonópolis

[![Licença: CC0 1.0](https://img.shields.io/badge/licen%C3%A7a-CC0%201.0-blue.svg)](LICENSE)
[![Compilar documentos](https://github.com/richarallan/modelos-latex-senai-roo/actions/workflows/compilar-documentos.yml/badge.svg)](https://github.com/richarallan/modelos-latex-senai-roo/actions/workflows/compilar-documentos.yml)

Modelos abertos para criar materiais educacionais com uma fonte única de
conteúdo. O professor ou uma IA escreve Markdown com metadados YAML; o projeto
valida essa estrutura e gera TEX, PDF e DOCX de maneira reproduzível.

> [!IMPORTANT]
> Este é um projeto independente e não constitui publicação oficial do SENAI.
> Marcas, logotipos e manuais de identidade visual não são licenciados por este
> repositório e somente devem ser usados por pessoas autorizadas.

## Princípio do projeto

**A IA redige e classifica; o esquema valida; o renderizador formata.**

O primeiro MVP mantém três camadas separadas:

1. conteúdo e metadados em Markdown/YAML;
2. significado dos blocos pedagógicos em JSON Schema e Lua;
3. apresentação em classe LaTeX e arquivo de referência DOCX.

Assim, a identidade visual poderá evoluir sem reescrever atividades, notas de
aula ou a lógica de validação.

## Escopo do primeiro MVP

- tipos documentais `atividade_avaliativa` e `nota_aula`;
- validação por JSON Schema;
- blocos para objetivo, situação-problema, questão, segurança, prática e
  rubrica;
- classe LaTeX visualmente neutra;
- referência DOCX com estilos semânticos;
- geração de TEX, PDF e DOCX por um único comando;
- quatro testes automatizados;
- validação e compilação no GitHub Actions.

## Estrutura

```text
.
├── documentos/                         # conteúdos mantidos pelo projeto
├── exemplos/                           # exemplos dos dois tipos do MVP
├── schemas/
│   └── documento.schema.json           # contrato documental
├── filtros/
│   └── blocos-senai.lua                # tradução dos blocos semânticos
├── scripts/
│   ├── renderizar.py                   # valida e coordena a conversão
│   └── criar_reference_docx.py         # recria a referência do Word
├── templates/
│   ├── latex/classes/senaiarticle.cls  # estrutura e apresentação LaTeX
│   └── docx/reference.docx             # estilos do Word
├── tests/
│   └── test_renderizar.py
└── .github/workflows/
    └── compilar-documentos.yml
```

## Uso rápido

### 1. Instale as dependências

- Python 3.10 ou superior;
- Pandoc 2.17 ou superior;
- XeLaTeX com `tcolorbox` e fontes TeX Gyre.

Em Ubuntu ou Debian:

```bash
python -m pip install --requirement requirements.txt
sudo apt-get update
sudo apt-get install pandoc texlive-xetex texlive-latex-extra texlive-fonts-recommended
```

### 2. Valide o conteúdo

```bash
python scripts/renderizar.py --validar-apenas
```

Se um campo obrigatório estiver ausente ou uma imagem local não existir, a
compilação será interrompida com uma mensagem que identifica o problema.

### 3. Gere os documentos

```bash
python scripts/renderizar.py --formato todos
```

Para formatos específicos:

```bash
python scripts/renderizar.py exemplos/atividade-usinagem.md --formato pdf,docx
python scripts/renderizar.py exemplos/nota-aula-metrologia.md --formato tex
```

Os resultados são gravados em `dist/` preservando a pasta de origem.

## Documento canônico

Os identificadores internos são previsíveis e não usam espaços ou acentos. O
texto exibido no documento continua normalmente em português.

```markdown
---
versao_schema: 1
tipo_documento: atividade_avaliativa
titulo: "Pressão de corte e tempo de usinagem"
autor: "Richar Allan Macedo"
instituicao: "SENAI/MT"
unidade_operacional: "Rondonópolis"
unidade_curricular: "Processos de Fabricação Mecânica"
publico: "Aprendizagem industrial"
carga_horaria: "4 h"
---

::: {.questao #q1 pontos=2 tipo=calculo}
Determine a rotação adequada para a operação de desbaste.
:::
```

Assistentes de IA devem preservar o cabeçalho YAML, os identificadores e a
sintaxe dos blocos. O conteúdo pode permanecer legível e versionável mesmo sem
uma ferramenta de IA.

## Testes e integração contínua

```bash
python -m unittest discover --start-directory tests --verbose
```

O workflow `compilar-documentos.yml` executa os testes, valida todas as fontes,
gera os três formatos e publica o artefato `documentos-gerados` em cada pull
request e alteração relevante na `main`.

## Créditos e licença

O projeto reconhece como referência o trabalho de Emerson Mello, do Instituto
Federal de Santa Catarina. Consulte [CREDITS.md](CREDITS.md) para o commit
consultado, os componentes estudados e os limites desta adaptação.

O conteúdo próprio deste repositório é disponibilizado sob a dedicação ao
domínio público [CC0 1.0 Universal](LICENSE), sem afetar direitos de terceiros,
marcas ou materiais incorporados futuramente sob outras licenças.
