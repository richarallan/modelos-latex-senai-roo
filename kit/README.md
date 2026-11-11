# Comece por um Markdown

Escolha um arquivo inicial, copie-o para a pasta onde ficará o conteúdo e edite
o texto. Os arquivos iniciais usam autoria coletiva, sem nomes de pessoas
inventados.

| Modelo | Markdown inicial | Demonstração gerável | PDF |
|---|---|---|---|
| Artigo institucional | [modelos/artigo.md](modelos/artigo.md) | [artigo-demonstracao.md](../exemplos/nucleo/artigo-demonstracao.md) | [Abrir](../exemplos/nucleo/artigo-demonstracao.pdf) |
| Nota de aula | [modelos/nota-aula.md](modelos/nota-aula.md) | [nota-aula-demonstracao.md](../exemplos/nucleo/nota-aula-demonstracao.md) | [Abrir](../exemplos/nucleo/nota-aula-demonstracao.pdf) |
| Atividade avaliativa | [modelos/atividade-avaliativa.md](modelos/atividade-avaliativa.md) | [atividade-demonstracao.md](../exemplos/nucleo/atividade-demonstracao.md) | [Abrir](../exemplos/nucleo/atividade-demonstracao.pdf) |

O [exemplo mínimo](../exemplos/nucleo/minimo.md) contém apenas a identificação
obrigatória e um parágrafo. O [exemplo completo](../exemplos/nucleo/completo.md)
exercita o catálogo: Markdown comum, sete blocos pedagógicos, objetos numerados,
painel, fontes, notas, citações e links. A ausência dos campos pessoais de
contato, orientação e banca é intencional.

## Gere em um comando

Na raiz do repositório, com Python, Pandoc e XeLaTeX instalados:

```bash
python scripts/renderizar.py kit/modelos/artigo.md
```

A saída padrão é LaTeX e PDF em `dist/`. Para essa entrada, os arquivos são
`dist/artigo.tex` e `dist/artigo.pdf`. O arquivo `.md` é a fonte que deve ser
editada; o `.tex` é gerado novamente a cada execução.

```bash
# Verifique a entrada sem gerar arquivos.
python scripts/renderizar.py exemplos/nucleo/completo.md --validar-apenas

# Gere as três demonstrações em um único comando.
python scripts/renderizar.py exemplos/nucleo/artigo-demonstracao.md exemplos/nucleo/nota-aula-demonstracao.md exemplos/nucleo/atividade-demonstracao.md

# Escolha a pasta de saída.
python scripts/renderizar.py exemplos/nucleo/minimo.md --saida dist/revisao
```

O comando sem entradas processa `documentos/` e `exemplos/`. `--formato tex,pdf`
é o padrão. `--formato docx` continua disponível para nota de aula e atividade;
o Word do artigo permanece reservado para uma próxima etapa.

## Preencha o cabeçalho

O cabeçalho YAML fica entre as duas linhas `---` no início do Markdown. Use
aspas para datas e textos que contenham dois-pontos. A ordem de `autor` é a
ordem apresentada no documento.

| Campo | Obrigatório | Como preencher |
|---|---|---|
| `versao_schema` | Sim | `1`, como número. |
| `tipo_documento` | Sim | `nota_aula` ou `atividade_avaliativa`, conforme a finalidade. |
| `modelo` | Não | `artigo`, `nota_aula` ou `atividade_avaliativa`; sem o campo, o perfil segue o tipo documental. |
| `titulo` | Sim | Título do documento, com pelo menos três caracteres. |
| `autor` | Sim | Texto de autoria ou lista YAML de autorias reais, na ordem desejada. É possível usar uma equipe ou instituição responsável. |
| `instituicao` | Sim | Instituição responsável pelo documento. |
| `unidade_operacional` | Sim | Unidade à qual o documento se refere. |
| `unidade_curricular` | Sim | Unidade curricular; também serve de referência para curso e habilitação quando esses campos não são informados. |
| `publico` | Sim | Público a que o conteúdo se destina. |
| `carga_horaria` | Sim | Texto como `"4 h"`, `"1,5 h"` ou `"30 min"`. |
| `subtitulo`, `data` | Não | Subtítulo e data em texto; são omitidos se não preenchidos. |
| `idioma` | Não | `pt-BR` (padrão), `en` ou `es`; seleciona o idioma de composição, sem traduzir o conteúdo. |
| `bibliografia` | Não | Caminho relativo ao Markdown para CSL-YAML/JSON, ou lista de caminhos. |
| `resumo`, `palavras_chave` | Não | Resumo em texto; palavras-chave como lista YAML. Lista vazia não gera rótulo. |
| `pre_textuais` | Não | No artigo, `true` inclui os pré-textuais que tenham conteúdo; `false` começa pelo corpo. |
| `capa`, `folha_rosto` | Não | Booleanos; permitem desativar individualmente essas páginas do artigo. |
| `aprovacao` | Não | `false` desativa a aprovação; `true` só a inclui quando há coordenação, banca ou data de aprovação fornecidas. |
| `sumario` | Não | Booleano que altera o padrão do perfil; sem títulos de seção, o sumário é omitido. |
| `capa`, `folha_rosto`, `aprovacao` | Não | No artigo, controlam cada pré-textual com `true`/`false`. A aprovação continua exigindo dados efetivos, mesmo com `aprovacao: true`. |
| `sumario` | Não | `true`/`false` substitui a preferência do perfil; sem títulos de seção, não é criado um sumário vazio. |
| `curso`, `habilitacao` | Não | Dados acadêmicos fornecidos para a folha de rosto. |
| `local`, `data_aprovacao` | Não | Cidade e data de aprovação somente quando conhecidas e fornecidas. Não há inferência de cidade a partir da unidade. |
| `orientador`, `coordenacao`, `banca`, `email` | Não | Dados reais de orientação, coordenação, banca (lista) e contato. Omita os desconhecidos. |

Propriedades desconhecidas, tipos incorretos e valores obrigatórios vazios são
erros de entrada. Campos opcionais sem conteúdo são omitidos: não preencha com
traços, nomes inventados ou frases que simulem assinaturas. A aprovação só é
composta quando há dados de aprovação; a presença de um orientador, sozinha,
não cria uma página de aprovação.

## Escreva o corpo

Use Markdown comum para parágrafos, títulos e listas. Reserve blocos semânticos
para os elementos que precisam de tratamento próprio:

````markdown
# Preparação {#preparacao}

Um parágrafo com **ênfase** e uma [chamada interna](#preparacao).

1. Identificar a tarefa.
2. Registrar as evidências.

::: {.objetivo identificador="objetivo-registro"}
Relacionar a leitura do instrumento à unidade e à condição de medição.
:::
````

Em elementos numerados, `identificador` é estável e não contém a posição do
elemento. O número é calculado a cada geração:

```markdown
O arranjo está na @fig:conjunto.

::: {.figura identificador="fig:conjunto" titulo="Conjunto motor-bomba" arquivo="imagens/conjunto.png" fonte="Elaboração própria." nota="Esquema sem escala." idioma="pt-BR"}
:::
```

O arquivo deve existir relativamente ao Markdown. Título e fonte são
obrigatórios para figura, gráfico e tabela; nota é opcional. Equações usam
corpo matemático `$$...$$`, com título, fonte e nota opcionais. As formas
anteriores `#fig:conjunto` e `![Descrição](arquivo.png)` continuam aceitas.
Veja os [exemplos copiáveis de todos os elementos](elementos.md), o
[prompt curto para IA](prompt-ia.md) e a
[matriz de cobertura](../docs/matriz-cobertura.md).

## Revise antes de entregar

O núcleo rejeita IDs repetidos, chamadas internas sem destino, arquivos
ausentes, citações sem referência e metadados inválidos. Leia a mensagem de erro,
corrija a entrada indicada e execute o mesmo comando novamente. Confira também
o PDF: a validação estrutural não substitui a revisão do conteúdo.

Para acrescentar uma apresentação, siga
[Como criar o próximo template](../docs/novo-template.md). O contrato do núcleo
e os critérios normativos estão em
[Critérios editoriais](../docs/criterios-editoriais.md).
