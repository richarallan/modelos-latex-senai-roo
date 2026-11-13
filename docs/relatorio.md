# Relatório institucional

O perfil `modelo: relatorio` usa a referência
[`templates/Relatorio/Modelo Relatorio.doc`](../templates/Relatorio/Modelo%20Relatorio.doc)
e a mesma representação semântica dos demais perfis. A interpretação de
Markdown, validação, citações, numeração, legendas, fontes, notas e links continua
no núcleo comum. O perfil seleciona a apresentação do relatório.

## Gerar um relatório

Parta do [Markdown inicial](../kit/modelos/relatorio.md) ou das demonstrações:

| Documento | Markdown | PDF |
|---|---|---|
| Mínimo, sem pré-textuais ou opcionais preenchidos | [Fonte](../exemplos/relatorio/relatorio-minimo.md) | [PDF](../exemplos/relatorio/relatorio-minimo.pdf) |
| Completo, com objetos, fontes, notas, citações e tabelas | [Fonte](../exemplos/relatorio/relatorio-completo.md) | [PDF](../exemplos/relatorio/relatorio-completo.pdf) |
| Título longo e três autorias coletivas | [Fonte](../exemplos/relatorio/relatorio-titulo-longo.md) | [PDF](../exemplos/relatorio/relatorio-titulo-longo.pdf) |

Na raiz do repositório:

```bash
python scripts/renderizar.py exemplos/relatorio/relatorio-completo.md
```

O comando valida a entrada e gera TEX/PDF via Pandoc e XeLaTeX, em
`dist/exemplos/relatorio/`. Para validar sem gravar as saídas:

```bash
python scripts/renderizar.py exemplos/relatorio/relatorio-completo.md --validar-apenas
```

O relatório oferece `tex,pdf`. A saída Word permanece para uma etapa posterior.
Os tipos documentais atuais, `nota_aula` e `atividade_avaliativa`, são mantidos;
`relatorio` é um perfil de apresentação, não um novo `tipo_documento`.

## Campos e páginas opcionais

Os nove campos obrigatórios do contrato continuam os mesmos: `versao_schema`,
`tipo_documento`, `titulo`, `autor`, `instituicao`, `unidade_operacional`,
`unidade_curricular`, `publico` e `carga_horaria`. Veja a explicação completa no
[guia rápido](../kit/README.md).

| Campo | Uso no relatório |
|---|---|
| `modelo: relatorio` | Seleciona a apresentação de relatório. |
| `tipo_trabalho` | Texto do bloco superior da capa; padrão `RELATÓRIO TÉCNICO`. Para um TCC, informe a designação real correspondente. |
| `titulo`, `subtitulo` | Título central da capa e identificação da folha de rosto; subtítulo só aparece quando fornecido. |
| `autor` | Texto ou lista YAML na ordem de apresentação. Use dados reais ou autoria institucional/coletiva. |
| `curso`, `habilitacao` | Contexto acadêmico fornecido; quando ausentes, o núcleo usa `unidade_curricular` como referência. |
| `natureza` | Texto próprio da folha de rosto. Sem ele, usa-se uma descrição simples de apresentação ao curso, sem atribuir grau ou aprovação. |
| `pre_textuais` | `false` começa pelo corpo. O padrão do perfil habilita os pré-textuais aplicáveis. |
| `capa`, `folha_rosto` | Booleanos para desativar individualmente essas páginas. |
| `aprovacao` | `false` desativa a aprovação; mesmo com `true`, a página exige dados de coordenação, banca ou data de aprovação. |
| `orientador`, `coordenacao`, `banca` | Somente os dados informados são apresentados; `banca` é uma lista. Orientação isolada não cria aprovação. |
| `local`, `data`, `data_aprovacao` | Cidade e datas independentes; nenhuma cidade é inferida da unidade operacional. |
| `sumario` | Padrão `true`; `false` desativa o sumário. Sem títulos no conteúdo, ele é omitido. |
| `resumo`, `palavras_chave` | Opcionais; a ausência ou o conteúdo vazio não gera rótulos vazios. |
| `idioma` | `pt-BR` por padrão; também são suportados `en` e `es`, sem tradução automática do conteúdo. |
| `bibliografia` | Arquivo CSL-YAML/CSL-JSON relativo ao Markdown, com identificadores estáveis. |

Exemplo de propriedades próprias:

```yaml
modelo: relatorio
tipo_trabalho: "RELATÓRIO TÉCNICO"
natureza: >-
  Relatório de estudo apresentado ao curso de Manutenção Mecânica.
  O conteúdo utiliza dados simulados para demonstrar a revisão de registros.
```

Campos opcionais vazios são omitidos quando o contrato admite essa ausência.
Tipos incorretos, campos desconhecidos, obrigatórios vazios ou ausentes são
rejeitados com diagnóstico. Nomes, assinaturas e resultados não são criados
para preencher lacunas.

## Critérios de layout adotados

A primeira página conserva a composição da referência: logo centralizado na
página, identificação do trabalho e curso centralizados no miolo, título no
centro, autores alinhados à direita, cidade e data no rodapé. O texto usa o
miolo definido pelas margens assimétricas; o logo mantém o centro do papel.
O mesmo PNG do modelo de artigo é reutilizado, pois é idêntico à imagem
embutida na referência do relatório.

As medidas de referência foram verificadas por conversão do DOC para PDF.
Na capa A4, os topos dos blocos ficam aproximadamente em 9,10 cm para a
identificação do trabalho, 11,29 cm para o curso, 14,22 cm para o título,
17,87 cm para a autoria e 25,17/25,90 cm para cidade/data. Títulos longos podem
ocupar mais linhas; a variação com três autorias permite conferir a composição.
Pequenas diferenças nas métricas das fontes de fallback podem alterar a quebra
das linhas sem modificar a estrutura.

O corpo utiliza A4, margens superior/esquerda de 3 cm e inferior/direita de
2 cm, 12 pontos, fonte Times New Roman quando disponível e alternativas livres
compatíveis, entrelinha de 1,5, texto justificado e recuo inicial de 1,25 cm.
Seções primárias começam em nova página. As regras visuais acadêmicas existentes
são reutilizadas pela opção de classe `relatorio`.

As marcações vermelhas do Word são instruções e placeholders, não cores
institucionais do conteúdo final. O DOC também contém nomes fixos, campos de
resultado e referências normativas antigas; eles não são dados do novo
relatório. Os critérios vigentes do projeto continuam em
[critérios editoriais](criterios-editoriais.md), sem afirmar uma certificação
integral de conformidade normativa.

## Conteúdo e elementos

Escreva parágrafos, títulos e listas em Markdown comum. Para objetos numerados,
use o mesmo catálogo dos demais perfis:

```markdown
O arranjo está na @fig:conjunto.

::: {.figura identificador="fig:conjunto" titulo="Conjunto motor-bomba" arquivo="imagens/conjunto.png" fonte="Elaboração própria." nota="Esquema sem escala." idioma="pt-BR"}
:::
```

O arquivo deve existir relativamente ao Markdown. O núcleo calcula os números
e resolve as chamadas novamente a cada geração, inclusive após inserir ou
reorganizar elementos. A [matriz](matriz-cobertura.md) e o
[catálogo copiável](../kit/elementos.md) detalham os campos de cada elemento.

Referências são produzidas pelo citeproc a partir das obras efetivamente
citadas. Apêndices e anexos podem ser escritos como seções comuns, por exemplo
`# Apêndice A — Roteiro {.unnumbered}`. A designação é conteúdo fornecido no
Markdown; não há uma nova sequência automática de apêndices, anexos ou siglas.
Não inclua páginas opcionais sem conteúdo.

## Validação

Os testes de relatório complementam a regressão existente do artigo e do núcleo.
Eles verificam o contrato, obrigatórios e opcionais, composição da capa,
paginação, objetos, legendas, fontes/notas, citações, tabelas e destinos internos.
A compatibilidade deve ser executada com Pandoc e pandoc-data 3.1.3 do Ubuntu
24.04, TeX Live 2023 e fontes recomendadas, além da versão local do Pandoc.

```bash
python -m unittest discover --start-directory tests --verbose
python scripts/renderizar.py exemplos/relatorio/*.md
```

O artigo aprovado permanece como referência de regressão. As demonstrações do
relatório são arquivos próprios, com autoria coletiva e valores explicitamente
simulados.
