# Elementos para copiar

Parágrafos, títulos e listas usam Markdown comum. Os blocos semânticos são
reservados aos elementos que precisam de apresentação ou numeração próprias.
Os trechos deste guia podem ser inseridos no
[exemplo completo](../exemplos/nucleo/completo.md), que já possui o cabeçalho e a
bibliografia necessários. Os caminhos de recursos mostrados são relativos a
`exemplos/nucleo/`; ajuste-os se mover o Markdown para outra pasta.

Escolha identificadores únicos ao copiar vários trechos para o mesmo arquivo.
Não escreva a numeração no título nem no ID. As propriedades usam chave-valor:

| Propriedade | Uso |
|---|---|
| `identificador` | Destino estável, como `fig:conjunto`; `#fig:conjunto` continua aceito. Não use as duas formas com valores diferentes. |
| `titulo` | Texto da identificação de figura, gráfico ou tabela. Opcional em equações. |
| `arquivo` | Imagem/arquivo gráfico relativo ao Markdown. A imagem também pode ser escrita com `![Descrição](arquivo)`. |
| `fonte` | Origem real do conteúdo. Obrigatória em figura, gráfico e tabela. Aceita citação bibliográfica. |
| `nota` | Informação complementar; o rótulo só aparece quando há texto. |
| `idioma` | Idioma do elemento, como `pt-BR`, `en` ou `es`; não traduz o texto. |
| `largura` | Largura da imagem, como `"85%"`; no painel, relativa à célula. |
| `colunas` | No painel, `2`, `3` ou `4`. |
| `manter_junto` | Em tabela curta, `"true"` conserva título, tabela, fonte e nota no mesmo bloco. |
| `pontos`, `tipo` | Na questão, complemento de identificação, como `pontos="2" tipo="analise"`. |

## Markdown comum

````markdown
# Seção {#secao-registro}

Um parágrafo com **ênfase forte**, *ênfase* e `código em linha`.

## Subseção

- Grandeza e unidade.
- Instrumento e condição.

1. Preparar o registro.
2. Revisar as evidências.

> Registre a origem das informações antes de tomar uma decisão.

[Voltar à seção](#secao-registro) e [consultar o BIPM](https://www.bipm.org/).

Uma afirmação com nota de rodapé.[^registro]

[^registro]: Informação complementar ao parágrafo.

```text
Grandeza: desvio dimensional
Unidade: mm
```

| Campo | Finalidade |
|:---|:---|
| Unidade | Interpretar o valor |
| Instrumento | Identificar a origem da leitura |

Expressão em linha: $\Delta x = x_o - x_r$.

$$
x_o = x_r + \Delta x
$$

![Motor elétrico sobre base.](../recursos/motor-eletrico.png){width=55%}
````

A imagem, a tabela e a fórmula nativas acima não participam das sequências de
objetos semânticos. Use os blocos a seguir quando precisar de chamada numerada.

## Objetivo

```markdown
::: {.objetivo identificador="objetivo-registro"}
Relacionar grandeza, unidade e condição de medição em um registro verificável.
:::
```

## Situação-problema

```markdown
::: situacao_problema
Uma equipe recebeu uma leitura sem unidade. Identifique as informações
necessárias para interpretar o resultado, sem inventar dados.
:::
```

## Questão

```markdown
::: {.questao identificador="questao-registro" pontos="2" tipo="analise"}
Explique por que unidade e condição de medição são necessárias à revisão.
:::

Retome a [questão de análise](#questao-registro).
```

## Segurança

```markdown
::: seguranca
A análise documental não autoriza uma intervenção no equipamento. Siga o
procedimento autorizado e as medidas de controle da tarefa.
:::
```

## Prática

```markdown
::: pratica
Prepare uma ficha com dados simulados e solicite a revisão por outra equipe.
:::
```

## Rubrica

```markdown
::: rubrica
Identificar a grandeza, preservar a unidade e justificar a necessidade do
critério de aceitação sem inventar uma tolerância.
:::
```

## Atenção

```markdown
::: atencao
Uma leitura isolada não comprova a condição de aceitação de um equipamento.
:::
```

Um bloco pedagógico sem conteúdo é omitido, sem caixa ou título vazio.

## Figura

```markdown
A disposição é apresentada na @fig:conjunto.

::: {.figura identificador="fig:conjunto" titulo="Conjunto motor-bomba" arquivo="../recursos/conjunto-motor-bomba.png" largura="80%" fonte="Ilustração didática gerada com IA para este repositório (2026)." nota="Esquema sem escala." idioma="pt-BR"}
:::
```

## Ilustração e desenho

Os dois nomes abaixo usam a mesma sequência e o mesmo prefixo `fig:` das figuras.

```markdown
::: {.ilustracao identificador="fig:motor" titulo="Motor elétrico" arquivo="../recursos/motor-eletrico.png" largura="70%" fonte="Ilustração didática gerada com IA para este repositório (2026)."}
:::

::: {.desenho identificador="fig:bomba" titulo="Bomba centrífuga" arquivo="../recursos/bomba-centrifuga.png" largura="70%" fonte="Ilustração didática gerada com IA para este repositório (2026)."}
:::
```

## Gráfico

```markdown
Os desvios são apresentados no @gra:leituras.

::: {.grafico identificador="gra:leituras" titulo="Desvios em verificações simuladas" arquivo="../recursos/grafico-medicoes.pdf" largura="85%" fonte="Elaboração própria, com dados simulados (2026)." nota="Os valores não representam uma intervenção real."}
:::
```

O gráfico é um arquivo preparado pelo autor; o núcleo não transforma tabelas
de dados em gráficos automaticamente. PNG e PDF são formatos compatíveis com a
geração por XeLaTeX.

## Tabela numerada

```markdown
Consulte a @tab:leituras.

::: {.tabela identificador="tab:leituras" titulo="Leituras simuladas" fonte="Elaboração própria, com dados simulados (2026)." nota="Exemplo didático." manter_junto="true"}
| Verificação | Desvio (mm) |
|:---|---:|
| 1ª | 0,18 |
| 2ª | 0,12 |
:::
```

Em tabelas maiores do que uma página, omita `manter_junto`; revise a paginação
e a identificação de continuação no PDF final.

## Equação

```markdown
O cálculo utiliza a @eq:desvio.

::: {.equacao identificador="eq:desvio" fonte="Relação didática entre valores de uma mesma grandeza." nota="Use unidades coerentes."}
$$
\Delta x = x_{\mathrm{observado}} - x_{\mathrm{referência}}
$$
:::
```

O número fica entre parênteses à direita. Não é criada uma legenda gráfica
“Equação 1 — título”. O campo `titulo`, quando fornecido, é prosa introdutória.
Título, fonte e nota são opcionais na equação.

## Equação em várias linhas

```markdown
::: {.equacao identificador="eq:relativo"}
$$
\varepsilon_r &= \frac{\Delta x}{x_{\mathrm{referência}}} \\
E_r &= 100\,\varepsilon_r
$$
:::
```

As linhas formam uma única equação numerada. Fórmulas usam a notação matemática
do Pandoc; não exigem comandos de legenda, numeração ou referência LaTeX.

## Painel de imagens

```markdown
:::: {.painel-imagens colunas="2"}
::: {.figura identificador="fig:painel-motor" titulo="Motor elétrico" arquivo="../recursos/motor-eletrico.png" largura="90%" fonte="Ilustração didática gerada com IA para este repositório (2026)."}
:::

::: {.figura identificador="fig:painel-bomba" titulo="Bomba centrífuga" arquivo="../recursos/bomba-centrifuga.png" largura="90%" fonte="Ilustração didática gerada com IA para este repositório (2026)."}
:::
::::
```

Use de duas a quatro colunas e ao menos duas imagens identificadas. Cada filho
tem seu próprio título, fonte, ID e número; o painel não recebe um número
adicional. Uma imagem isolada tem título centralizado; no painel, os títulos
ficam à esquerda.

## Citações e bibliografia

No cabeçalho do Markdown em `exemplos/nucleo/`:

```yaml
bibliografia: "../referencias/artigo.yaml"
```

No corpo:

```markdown
Segundo @jcgm2012, os conceitos de medição precisam ser definidos.
A mesma obra pode ser citada entre parênteses [@jcgm2012].

# Referências {.unnumbered}

::: {#refs}
:::
```

Um arquivo CSL-YAML mínimo com uma referência corporativa real:

```yaml
references:
  - id: jcgm2012
    type: report
    author:
      - literal: JCGM
    title: "International vocabulary of metrology: basic and general concepts and associated terms (VIM)"
    edition: "3"
    issued:
      date-parts: [[2012]]
    publisher: BIPM
    publisher-place: Sèvres
    number: "JCGM 200:2012"
```

Também são aceitos CSL-JSON e listas de arquivos bibliográficos. Uma obra só
aparece na lista quando citada; um ID sem cadastro é erro. Os IDs de objetos
`fig:`, `gra:`, `tab:` e `eq:` são reservados e não podem ser usados como chaves
bibliográficas.

## Pré-textuais e dados opcionais

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
  - registro técnico
  - medição
```

`pre_textuais: false` inicia diretamente pelo corpo. Cidade, data, orientação,
contato, coordenação, banca, resumo e palavras-chave só aparecem quando
fornecidos. Para orientação e aprovação, use exclusivamente os dados reais
autorizados. Uma lista vazia de palavras-chave não cria rótulo; a ausência de
dados de aprovação não cria página, títulos de banca ou linhas de assinatura.
Com os pré-textuais habilitados, `capa: false`, `folha_rosto: false` e
`aprovacao: false` permitem omitir cada página separadamente. `sumario: true`
ou `false` substitui a preferência do perfil; sem títulos, não cria um sumário
vazio.
Veja todos os campos no [guia rápido](README.md#preencha-o-cabeçalho).
