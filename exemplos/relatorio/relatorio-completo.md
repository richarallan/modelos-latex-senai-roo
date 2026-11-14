---
versao_schema: 1
tipo_documento: nota_aula
modelo: relatorio
titulo: "Relatório de estudo do registro técnico de inspeção de um conjunto motor-bomba"
subtitulo: "Demonstração de rastreabilidade e revisão de evidências"
autor:
  - "Equipe de preparação"
  - "Equipe de registro"
  - "Equipe de revisão"
instituicao: "SENAI/MT"
unidade_operacional: "Rondonópolis"
unidade_curricular: "Manutenção Mecânica"
publico: "Educação profissional técnica"
carga_horaria: "4 h"
curso: "Habilitação Técnica em Mecânica"
habilitacao: "Mecânica"
tipo_trabalho: "TRABALHO DE CONCLUSÃO DE CURSO"
natureza: >-
  Relatório didático de estudo apresentado ao curso de Habilitação Técnica em
  Mecânica. O conteúdo utiliza dados simulados para demonstrar o registro e a
  revisão de evidências, sem representar uma intervenção ou pesquisa de campo.
local: "Rondonópolis – MT"
data: "2026"
idioma: "pt-BR"
pre_textuais: true
sumario: true
bibliografia: "../referencias/artigo.yaml"
---

# Introdução {#introducao}

Este relatório demonstra a apresentação institucional e o núcleo documental
compartilhado. O objetivo é organizar um registro de inspeção, relacionando
identificação, unidade, condição de medição e revisão das evidências.

Todos os valores numéricos são **simulados para estudo**. O texto não descreve
uma manutenção executada nem atribui resultados a uma empresa ou pessoa.
As autorias representam equipes de elaboração do exemplo.

## Contexto do estudo

O cenário didático é um conjunto motor-bomba. A equipe recebe uma sequência
de valores e deve verificar quais informações faltam antes de emitir uma
conclusão técnica. A [atividade de revisão](#questao-revisao) e o
[roteiro do apêndice](#apendice-registro) podem ser consultados por links internos.

- Identificar a grandeza e a unidade.
- Registrar o instrumento e a condição de leitura.
- Solicitar o critério de aceitação autorizado.

O relatório mantém os parágrafos, títulos e listas em Markdown comum. Não é
necessário escrever comandos de paginação, legenda ou referência em LaTeX.

# Fundamentação

Segundo @jcgm2012, os conceitos de medição devem ser apresentados de forma
coerente. A mesma publicação pode ser citada entre parênteses
[@jcgm2012, p. 2]. A origem deve permitir que outra equipe confira a informação.

> Um valor isolado não documenta, sozinho, as condições em que foi obtido.

A frase acima é uma orientação de elaboração do exemplo, não uma transcrição
atribuída à publicação. A referência ao [BIPM](https://www.bipm.org/) demonstra
um link externo comum.

A diferença em linha é escrita como $\Delta x = x_o - x_r$.
A expressão destacada abaixo permanece sem número, pois está fora de `.equacao`:

$$
x_o = x_r + \Delta x
$$

```text
Grandeza: desvio dimensional
Unidade: mm
Origem: valores simulados para estudo
```

Uma nota de rodapé pode explicar o alcance de uma informação.[^alcance]

[^alcance]: Este documento demonstra recursos de composição, sem substituir procedimentos técnicos autorizados.

# Atividades desenvolvidas {#atividades}

::: {.objetivo identificador="objetivo-registro"}
Relacionar o valor registrado à grandeza, à unidade e à condição de medição.
:::

::: situacao_problema
Um registro apresenta quatro valores, mas não identifica o critério de
aceitação. A equipe deve apontar essa lacuna antes de avaliar o conjunto.
:::

::: {.questao identificador="questao-revisao" pontos="2" tipo="analise"}
Quais informações devem ser solicitadas antes de interpretar os valores?
:::

::: seguranca
O cenário didático não autoriza uma intervenção no equipamento. Atividades
reais exigem procedimento e análise de riscos aplicáveis.
:::

::: pratica
Prepare uma ficha de registro e troque-a com outra equipe para revisão.
:::

::: rubrica
Identificar grandeza, unidade, condição de medição e ausência do critério de aceitação.
:::

::: atencao
Não preencha lacunas com dados, nomes ou resultados inventados.
:::

## Identificação dos elementos

O arranjo está na @fig:conjunto. O painel apresenta os componentes da
@fig:motor e da @fig:bomba. As chamadas acompanham os números calculados pelo
núcleo, inclusive quando aparecem antes das imagens.

::: {.figura identificador="fig:conjunto" titulo="Conjunto motor-bomba" arquivo="../recursos/conjunto-motor-bomba.png" largura="55%" fonte="Ilustração didática gerada para este repositório com IA; elaboração própria (2026)." nota="Esquema sem escala." idioma="pt-BR"}
:::

:::: {.painel-imagens colunas="2"}
::: {.ilustracao identificador="fig:motor" titulo="Motor elétrico" arquivo="../recursos/motor-eletrico.png" largura="65%" fonte="Ilustração didática gerada com IA para este repositório (2026)."}
:::

::: {.desenho identificador="fig:bomba" titulo="Bomba centrífuga" arquivo="../recursos/bomba-centrifuga.png" largura="65%" fonte="Ilustração didática gerada com IA para este repositório (2026)." nota="Representação sem escala."}
:::
::::

## Registro e interpretação

Os dados da @tab:leituras e do @gra:leituras são os mesmos. A fonte identifica
a elaboração do exemplo e a nota esclarece o que os valores não representam.

::: {.tabela identificador="tab:leituras" titulo="Desvios dimensionais simulados" fonte="Elaboração própria, com dados simulados (2026)." nota="Os valores não descrevem uma intervenção real." manter_junto="true"}
| Verificação | Desvio (mm) |
|:---|---:|
| 1ª | 0,18 |
| 2ª | 0,12 |
| 3ª | 0,07 |
| 4ª | 0,03 |
:::

::: {.grafico identificador="gra:leituras" titulo="Desvio nas verificações simuladas" arquivo="../recursos/grafico-medicoes.pdf" largura="65%" fonte="Elaboração própria, com os mesmos dados simulados da tabela (2026)."}
:::

A @eq:desvio demonstra uma expressão numerada. Sua origem e explicação podem
ficar em prosa ou nos campos opcionais do bloco, sem criar uma legenda gráfica.

::: {.equacao identificador="eq:desvio" fonte="Relação didática entre valores de uma mesma grandeza." nota="Use unidades coerentes."}
$$
\Delta x = x_{\mathrm{observado}} - x_{\mathrm{referência}}
$$
:::

1. Conferir a identificação e a unidade.
2. Revisar a condição de medição.
3. Solicitar os dados ausentes.

# Conclusão

O exemplo organiza a identificação, o registro e a revisão em uma sequência
verificável. Os valores simulados permitem exercitar a comunicação técnica,
mas não fundamentam uma decisão sobre a condição real de um equipamento.

O mesmo conteúdo utiliza o núcleo comum de citações, numeração e links.
A apresentação de relatório acrescenta a capa e a estrutura visual própria,
mantendo o conteúdo em Markdown.

# Referências {.unnumbered}

::: {#refs}
:::

# Apêndice A — Roteiro de registro {#apendice-registro .unnumbered}

Material elaborado para este exemplo, escrito como uma seção comum de Markdown.
A designação do apêndice é conteúdo informado na fonte, sem sequência automática.

| Campo | Informação a registrar |
|:---|:---|
| Grandeza | O que está sendo medido |
| Unidade | Unidade utilizada |
| Condição | Situação em que se realiza a leitura |
| Critério | Referência autorizada para interpretar o resultado |

# Anexo A — Referência de consulta {#anexo-consulta .unnumbered}

Este anexo demonstra uma seção opcional de consulta, sem reproduzir um documento
de terceiros. A publicação real citada está disponível no
[portal do BIPM](https://www.bipm.org/). O título do anexo é informado em Markdown,
sem uma numeração automática própria.
