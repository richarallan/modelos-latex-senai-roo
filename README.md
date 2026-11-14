# Modelos LaTeX SENAI Rondonópolis

[![Licença: CC0 1.0](https://img.shields.io/badge/licen%C3%A7a-CC0%201.0-blue.svg)](LICENSE)
[![Compilar documentos](https://github.com/richarallan/modelos-latex-senai-roo/actions/workflows/compilar-documentos.yml/badge.svg)](https://github.com/richarallan/modelos-latex-senai-roo/actions/workflows/compilar-documentos.yml)

Crie materiais educacionais em Markdown com metadados YAML e gere LaTeX e PDF
por Pandoc e XeLaTeX em um comando. Artigo institucional, relatório, nota de aula e
atividade avaliativa compartilham o mesmo núcleo de interpretação, validação e
referenciamento. A apresentação é selecionada por um perfil documental.

> [!IMPORTANT]
> Este é um projeto independente e não constitui publicação oficial do SENAI.
> Marcas, logotipos e manuais de identidade visual não são licenciados por este
> repositório e somente devem ser usados por pessoas autorizadas.

## Comece pelo kit

O [kit de início rápido](kit/README.md) reúne:

- [Markdown inicial para cada modelo](kit/modelos/);
- [exemplo mínimo](exemplos/nucleo/minimo.md) e [completo](exemplos/nucleo/completo.md);
- [exemplos copiáveis de cada elemento](kit/elementos.md);
- comando de geração e explicação dos campos;
- [prompt curto para uma IA](kit/prompt-ia.md);
- [instruções para criar o próximo template](docs/novo-template.md).

A [matriz de cobertura](docs/matriz-cobertura.md) define o catálogo, os campos,
as condições dos opcionais e a cobertura de testes. O artigo aprovado em
[Markdown](exemplos/artigo-exemplo.md) e [PDF](exemplos/artigo-exemplo.pdf)
permanece preservado como referência de regressão. As demonstrações do núcleo
ficam em [exemplos/nucleo/](exemplos/nucleo/). O [relatório](docs/relatorio.md) tem
demonstrações mínima, completa e com título longo em
[exemplos/relatorio/](exemplos/relatorio/), mantendo a composição da página inicial
do documento institucional de referência.

## Gere em um comando

Instale Python 3.10 ou superior, as dependências Python, Pandoc e XeLaTeX. O CI
usa Ubuntu 24.04 com o Pandoc 3.1.3 da distribuição; a compatibilidade desse
writer é verificada diretamente. Em Ubuntu ou Debian:

```bash
python -m pip install --requirement requirements.txt
sudo apt-get update
sudo apt-get install pandoc texlive-xetex texlive-latex-extra \
  texlive-fonts-recommended texlive-plain-generic poppler-utils
```

Na raiz do repositório:

```bash
python scripts/renderizar.py exemplos/nucleo/artigo-demonstracao.md
```

O padrão é TEX e PDF. As saídas desse exemplo são
`dist/exemplos/nucleo/artigo-demonstracao.tex` e
`dist/exemplos/nucleo/artigo-demonstracao.pdf`. Edite o Markdown; o LaTeX é uma
saída gerada, não uma segunda fonte de conteúdo.

```bash
# Valide sem gerar arquivos.
python scripts/renderizar.py exemplos/nucleo/completo.md --validar-apenas

# Gere todas as fontes de documentos/ e exemplos/.
python scripts/renderizar.py

# Gere os quatro perfis em um comando.
python scripts/renderizar.py exemplos/nucleo/artigo-demonstracao.md exemplos/relatorio/relatorio-completo.md exemplos/nucleo/nota-aula-demonstracao.md exemplos/nucleo/atividade-demonstracao.md

# Preserve a exportação Word dos perfis pedagógicos anteriores.
python scripts/renderizar.py exemplos/atividade-usinagem.md --formato pdf,docx
```

`--saida` escolhe o diretório de saída. `--pandoc` permite informar um
executável específico. O DOCX do artigo e do relatório continua reservado para
uma próxima etapa; pedir DOCX em um lote que inclua esses perfis é rejeitado antes de gerar
saídas parciais.

## Quatro responsabilidades

1. **Conteúdo**: Markdown comum para parágrafos, títulos e listas; YAML e
   propriedades chave-valor para metadados e elementos especializados.
2. **Núcleo**: leitura, contrato, interpretação semântica, recursos,
   identificadores, links, numeração, citações e coordenação da geração.
3. **Perfis documentais**: seleção declarativa de apresentação, classe,
   formatos permitidos, sumário e pré-textuais.
4. **Apresentação visual**: templates, classe, estilos e recursos; consome a
   mesma representação semântica, sem reimplementar a interpretação.

```text
Markdown + YAML → núcleo comum → representação semântica Pandoc JSON
                                      ↓
                         perfil + apresentação comum
                                      ↓
                           LaTeX → XeLaTeX → PDF
```

A fonte é interpretada uma vez para as saídas de cada geração. Os formatos
consomem a mesma representação: um template não recalcula números, cria um
segundo sistema de referências ou exige uma versão diferente do conteúdo.

```text
.
├── documentos/             # conteúdos mantidos pelo projeto
├── exemplos/               # artigo de regressão e demonstrações
├── kit/                    # arquivos iniciais, exemplos e prompt
├── nucleo/                 # leitura, perfis e geração compartilhados
│   └── lua/                # interpretação e apresentação dos elementos
├── perfis/                 # artigo, relatorio, nota_aula e atividade_avaliativa
├── schemas/                # contrato dos metadados
├── filtros/                # entradas dos filtros e compatibilidade legada
├── scripts/renderizar.py   # interface de linha de comando
├── templates/              # classe, templates visuais, CSL e referência DOCX
├── docs/                   # catálogo, critérios e extensão
└── tests/                  # validação, PDFs e regressão
```

## Conteúdo e modelos

Os tipos documentais continuam sendo `nota_aula` e `atividade_avaliativa`.
`modelo` seleciona `artigo`, `relatorio`, `nota_aula` ou `atividade_avaliativa`;
sem ele, o perfil segue o tipo documental. Artigo e relatório são apresentações
dos tipos atuais, com layouts institucionais próprios.

```markdown
---
versao_schema: 1
tipo_documento: nota_aula
modelo: artigo
titulo: "Registro técnico de uma atividade"
autor: "Equipe de elaboração"
instituicao: "SENAI/MT"
unidade_operacional: "Rondonópolis"
unidade_curricular: "Manutenção Mecânica"
publico: "Educação profissional"
carga_horaria: "4 h"
pre_textuais: false
---

# Finalidade

O texto permanece em Markdown comum.

::: {.objetivo identificador="objetivo-registro"}
Relacionar grandeza, unidade e condição de medição em um registro verificável.
:::
```

`autor` aceita texto ou lista YAML, preservando a ordem. Use autoria real,
institucional ou coletiva; não invente pessoas, contatos ou aprovações.
Elementos opcionais ausentes ou vazios não criam páginas, títulos ou rótulos.
Cidade e data são independentes e só aparecem quando fornecidas. A página de
aprovação exige dados efetivos; orientação sozinha não a cria.

## Relatório institucional

Parta do [Markdown inicial](kit/modelos/relatorio.md) ou da
[demonstração completa](exemplos/relatorio/relatorio-completo.md):

```bash
python scripts/renderizar.py exemplos/relatorio/relatorio-completo.md
```

O perfil `modelo: relatorio` preserva a hierarquia da capa de
`templates/Relatorio/Modelo Relatorio.doc`: logo no alto, identificação do
trabalho, curso e título centralizados, autores à direita e cidade/data no
rodapé. O corpo usa fonte de 12 pontos, margens 3/3/2/2 cm, entrelinha de 1,5 e
seções primárias em nova página. `tipo_trabalho` e `natureza` permitem informar
o contexto real do relatório; os campos e pré-textuais opcionais seguem as
regras do núcleo. Veja o [guia e os critérios de layout](docs/relatorio.md).

## Elementos compartilhados

O catálogo inclui os sete blocos pedagógicos (`objetivo`,
`situacao_problema`, `questao`, `seguranca`, `pratica`, `rubrica`, `atencao`),
figuras, gráficos, tabelas e equações numerados, aliases de ilustração/desenho,
painéis de duas a quatro colunas, citações autor-data e bibliografia
CSL-YAML/JSON. Todos os perfis usam os mesmos elementos.

```markdown
A disposição aparece na @fig:conjunto.

::: {.figura identificador="fig:conjunto" titulo="Conjunto motor-bomba" arquivo="imagens/conjunto.png" fonte="Elaboração própria." nota="Esquema sem escala." idioma="pt-BR"}
:::
```

O arquivo deve existir relativamente ao Markdown. Identificador, título,
arquivo, fonte, nota e idioma são propriedades chave-valor; as formas anteriores
`#id` e `![Descrição](arquivo)` continuam aceitas. A fonte e o título são
obrigatórios nos três tipos visuais; na equação, esses campos são opcionais.
As chamadas acompanham a numeração recalculada após inserir ou reorganizar
objetos.

Uma imagem isolada mantém o título centralizado; painéis lado a lado usam
alinhamento à esquerda. Equações recebem número à direita, sem legenda gráfica
automática. Os critérios e as fontes normativas consultadas estão em
[Critérios editoriais](docs/criterios-editoriais.md).

## Validação e testes

Metadados inválidos, IDs duplicados, destinos internos inexistentes, arquivos
ausentes e citações sem cadastro interrompem a geração com mensagens que
identificam o problema. Os exemplos do kit evitam dados pessoais fictícios.

```bash
python -m unittest discover --start-directory tests --verbose
```

O CI executa a suíte, valida todas as fontes e gera TEX/PDF; verifica também a
exportação DOCX dos exemplos pedagógicos. O artefato `documentos-gerados`
contém as saídas de cada execução. A suíte cobre campos obrigatórios e
opcionais, links, numeração, legendas, citações, tabelas, matemática, painéis e
o artigo de regressão.

O template de relatório e o artigo compartilham o preâmbulo, a bibliografia e
os elementos interpretados pelo núcleo. O documento Word de referência é
preservado para inspeção da origem do layout. O catálogo completo e seus limites estão na
[matriz de cobertura](docs/matriz-cobertura.md).

## Créditos e licença

O projeto reconhece como referência o trabalho de Emerson Mello, do Instituto
Federal de Santa Catarina. Consulte [CREDITS.md](CREDITS.md) para o commit
consultado, os componentes estudados e os limites desta adaptação.

O conteúdo próprio deste repositório é disponibilizado sob a dedicação ao
domínio público [CC0 1.0 Universal](LICENSE), sem afetar direitos de terceiros,
marcas ou materiais incorporados sob outras licenças.
