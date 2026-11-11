# Modelos LaTeX SENAI Rondonópolis

[![Licença: CC0 1.0](https://img.shields.io/badge/licen%C3%A7a-CC0%201.0-blue.svg)](LICENSE)
[![Compilar documentos](https://github.com/richarallan/modelos-latex-senai-roo/actions/workflows/compilar-documentos.yml/badge.svg)](https://github.com/richarallan/modelos-latex-senai-roo/actions/workflows/compilar-documentos.yml)

Modelos abertos para criar materiais educacionais com uma fonte única de
conteúdo. O professor ou uma IA escreve Markdown com metadados YAML; o projeto
valida essa estrutura e gera LaTeX e PDF via Pandoc e XeLaTeX. Os modelos
anteriores também mantêm a exportação opcional para DOCX.

> [!IMPORTANT]
> Este é um projeto independente e não constitui publicação oficial do SENAI.
> Marcas, logotipos e manuais de identidade visual não são licenciados por este
> repositório e somente devem ser usados por pessoas autorizadas.

## Princípio do projeto

**A IA redige e classifica; o esquema valida; o renderizador formata.**

O primeiro MVP mantém três camadas separadas:

1. conteúdo e metadados em Markdown/YAML;
2. significado dos blocos pedagógicos em JSON Schema e Lua;
3. apresentação em classe e templates LaTeX, com referência DOCX para os
   modelos anteriores.

Assim, a identidade visual poderá evoluir sem reescrever atividades, notas de
aula ou a lógica de validação.

## Escopo do primeiro MVP

- tipos documentais `atividade_avaliativa` e `nota_aula`;
- validação por JSON Schema;
- blocos para objetivo, situação-problema, questão, segurança, prática e
  rubrica;
- classe LaTeX com apresentação neutra e opção institucional de artigo;
- artigo baseado em `templates/artigo/original/Modelo Artigo.docx`, com capa,
  folha de rosto e termo de aprovação opcionais;
- geração de TEX e PDF por um único comando;
- exportação DOCX preservada para os modelos anteriores; Word do artigo
  reservado para uma próxima etapa;
- testes automatizados de validação, conversão e compatibilidade;
- validação e compilação no GitHub Actions.

## Estrutura

```text
.
├── documentos/                         # conteúdos mantidos pelo projeto
├── exemplos/                           # tipos atuais e apresentação de artigo
├── schemas/
│   └── documento.schema.json           # contrato documental
├── filtros/
│   └── blocos-senai.lua                # tradução dos blocos semânticos
├── scripts/
│   ├── renderizar.py                   # valida e coordena a conversão
│   └── criar_reference_docx.py         # recria a referência do Word
├── templates/
│   ├── latex/classes/senaiarticle.cls  # estrutura e apresentação LaTeX
│   ├── artigo/artigo.latex             # template Pandoc do artigo
│   ├── artigo/recursos/logo-senai.png   # marca extraída da referência
│   ├── artigo/original/                # documentos de referência preservados
│   └── docx/reference.docx             # estilos do Word
├── tests/
│   ├── test_renderizar.py
│   └── test_artigo.py
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
sudo apt-get install pandoc texlive-xetex texlive-latex-extra \
  texlive-fonts-recommended texlive-plain-generic poppler-utils
```

O artigo prioriza Times New Roman e usa fontes livres compatíveis quando ela
não está disponível, como TeX Gyre Termes ou Liberation Serif.
O pacote `poppler-utils` permite conferir o conteúdo dos PDFs nos testes.

### 2. Valide o conteúdo

```bash
python scripts/renderizar.py --validar-apenas
```

Se um campo obrigatório estiver ausente ou uma imagem local não existir, a
compilação será interrompida com uma mensagem que identifica o problema.

### 3. Gere os documentos

```bash
python scripts/renderizar.py
```

O padrão agora é `tex,pdf`. Para gerar o artigo em um comando:

```bash
python scripts/renderizar.py exemplos/artigo-exemplo.md --formato tex,pdf
```

O renderizador valida os metadados, aplica o template Pandoc com a classe
`senaiarticle` e compila com XeLaTeX. As saídas são
`dist/exemplos/artigo-exemplo.tex` e `dist/exemplos/artigo-exemplo.pdf`.
Uma cópia do PDF de demonstração acompanha o exemplo em
[`exemplos/artigo-exemplo.pdf`](exemplos/artigo-exemplo.pdf); regenere as saídas
em `dist/` sempre que alterar o conteúdo.

Para formatos específicos dos modelos anteriores:

```bash
python scripts/renderizar.py exemplos/atividade-usinagem.md --formato pdf,docx
python scripts/renderizar.py exemplos/nota-aula-metrologia.md --formato tex
python scripts/renderizar.py exemplos/atividade-usinagem.md --formato todos
```

Os resultados são gravados em `dist/` preservando a pasta de origem.
`todos` mantém TEX, PDF e DOCX para entradas sem `modelo: artigo`. Pedir
`docx` ou `todos` em um lote que inclua artigo interrompe a execução antes de
gerar qualquer arquivo, com orientação para usar `tex,pdf`.

## Documento canônico

Os identificadores internos são previsíveis e não usam espaços ou acentos. O
texto exibido no documento continua normalmente em português.

O campo `autor` aceita um nome em texto ou uma lista YAML de nomes. A ordem
informada é preservada na apresentação:

```yaml
autor:
  - "Nome do primeiro autor"
  - "Nome do segundo autor"
  - "Nome do terceiro autor"
```

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

## Apresentação de artigo

O campo opcional `modelo: artigo` seleciona a apresentação; ele não cria um
novo tipo documental. Continue usando `nota_aula` ou `atividade_avaliativa`
conforme a finalidade do conteúdo. Sem esse campo, a apresentação anterior é
preservada.

Parta de [`exemplos/artigo-exemplo.md`](exemplos/artigo-exemplo.md), que mantém
todos os metadados obrigatórios do documento canônico. Acrescente ou ajuste:

```yaml
modelo: artigo
pre_textuais: true
curso: "Habilitação Técnica em Mecânica"
habilitacao: "Mecânica"
local: "Rondonópolis – MT"
data: "2026"
resumo: >-
  Apresente o objetivo, o método, os resultados e as conclusões do trabalho.
palavras_chave:
  - manutenção mecânica
  - metrologia
  - registro técnico
```

A apresentação preserva o A4, as margens superior/esquerda de 3 cm e
inferior/direita de 2 cm, a fonte serifada de 12 pontos, o corpo justificado
com entrelinha de 1,5 e recuo inicial de 1,25 cm. O resumo usa espaço simples;
os títulos primários são destacados em negrito e caixa alta. Os ajustes de
espaçamento e alinhamento seguem a estrutura institucional da referência.

Por padrão, o artigo inclui capa, folha de rosto e termo de aprovação. Use
`pre_textuais: false` para começar diretamente pelo título e resumo. Os campos
opcionais `orientador`, `coordenacao`, `banca` (lista de nomes),
`data_aprovacao` e `email` permitem completar a identificação. Nomes de
avaliadores, resultado e data de aprovação não são inventados: os campos não
informados ficam sem preenchimento.

Na ausência de `curso` ou `habilitacao`, usa-se `unidade_curricular`. Cidade e
data são exibidas somente quando `local` e `data` forem informados no Markdown,
cada um de forma independente. A cidade não é inferida de `unidade_operacional`;
a aprovação usa apenas `data_aprovacao`, quando fornecida. A capa mantém o logo
institucional sem repetir a instituição e a unidade abaixo dele.
Resumo e palavras-chave são opcionais no esquema, mas devem
ser preenchidos em um artigo completo. A referência recomenda um resumo de
100 a 250 palavras; o renderizador não acrescenta texto para atingir esse
limite nem o número de páginas indicado no documento original.

A linha “Palavras-chave” aparece somente quando `palavras_chave` contém itens,
mesmo que o resumo não tenha sido informado. Com o campo ausente ou uma lista
vazia (`[]`), a linha é omitida.

Escreva as seções em Markdown. Para referências e anexos sem numeração, use
por exemplo `# Referências {.unnumbered}`. Blocos pedagógicos, tabelas e fórmulas
continuam disponíveis. O exemplo é didático e reduzido; não representa uma
pesquisa de campo.

## Testes e integração contínua

```bash
python -m unittest discover --start-directory tests --verbose
```

O workflow `compilar-documentos.yml` executa os testes, valida todas as fontes,
gera TEX/PDF e verifica a exportação DOCX dos exemplos anteriores. As saídas
são disponibilizadas no artefato `documentos-gerados` em cada pull request
para `main` e alteração relevante na `main` ou na feature
`feat/primeiro-mvp-documentos`.

## Créditos e licença

O projeto reconhece como referência o trabalho de Emerson Mello, do Instituto
Federal de Santa Catarina. Consulte [CREDITS.md](CREDITS.md) para o commit
consultado, os componentes estudados e os limites desta adaptação.

O conteúdo próprio deste repositório é disponibilizado sob a dedicação ao
domínio público [CC0 1.0 Universal](LICENSE), sem afetar direitos de terceiros,
marcas ou materiais incorporados futuramente sob outras licenças.
