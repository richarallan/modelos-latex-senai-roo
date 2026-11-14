---
versao_schema: 1
tipo_documento: nota_aula
titulo: Rastreabilidade do registro técnico
autor: Equipe de elaboração
instituicao: SENAI/MT
unidade_operacional: Rondonópolis
unidade_curricular: Manutenção Mecânica
publico: Educação profissional
carga_horaria: 4 h
idioma: pt-BR
modelo: artigo
subtitulo: Demonstração do núcleo documental compartilhado
pre_textuais: true
curso: Habilitação Técnica em Mecânica
habilitacao: Mecânica
local: Rondonópolis – MT
data: '2026'
bibliografia: ../referencias/artigo.yaml
resumo: Este exemplo didático apresenta um registro técnico de medição para demonstrar
  o núcleo documental compartilhado. O objetivo é relacionar a identificação da grandeza,
  a unidade e a condição de medição à interpretação do resultado. O roteiro utiliza
  valores simulados e uma ilustração do conjunto motor-bomba, sem representar uma
  intervenção industrial real. A apresentação reúne figura, tabela, gráfico e equação
  com identificadores estáveis, além de citações autor-data e links internos. A mesma
  interpretação é utilizada pelos perfis de artigo, nota de aula e atividade avaliativa.
  A conclusão destaca que a revisão do registro exige a origem das informações e o
  critério da decisão. Dados pessoais de orientação, contato e banca foram omitidos
  porque não foram fornecidos.
palavras_chave:
- registro técnico
- medição
- rastreabilidade
---

# Leitura de um registro {#leitura}

Segundo @jcgm2012, os conceitos de medição dependem da definição clara das
grandezas. Este exemplo usa **dados simulados**, com finalidade didática,
e permite voltar à [seção de leitura](#leitura).

::: {.objetivo identificador="objetivo-registro"}
Relacionar grandeza, unidade e condição de medição em um registro verificável.
:::

A disposição está na @fig:conjunto, os valores estão na @tab:leituras e no
@gra:leituras, e o cálculo é apresentado na @eq:desvio.

::: {.figura identificador="fig:conjunto" titulo="Conjunto motor-bomba" arquivo="../recursos/conjunto-motor-bomba.png" largura="75%" fonte="Ilustração didática gerada para este repositório com IA; elaboração própria (2026)." nota="Esquema sem escala." idioma="pt-BR"}
:::

## Sequência de revisão

1. Identificar o equipamento e o instrumento.
2. Registrar grandeza, unidade e condição de medição.
3. Comparar o resultado ao critério fornecido pelo procedimento.

::: {.tabela identificador="tab:leituras" titulo="Desvios em registros simulados" fonte="Elaboração própria, com dados simulados para fins didáticos (2026)." nota="Os valores não representam uma intervenção real." manter_junto="true"}
| Verificação | Desvio (mm) |
|:---|---:|
| 1ª | 0,18 |
| 2ª | 0,12 |
| 3ª | 0,07 |
| 4ª | 0,03 |
:::

::: {.grafico identificador="gra:leituras" titulo="Desvios nas quatro verificações simuladas" arquivo="../recursos/grafico-medicoes.pdf" largura="75%" fonte="Elaboração própria, com os mesmos dados simulados da tabela (2026)." nota="A sequência não demonstra eficácia de uma manutenção real."}
:::

O desvio compara o valor observado e o valor de referência. Seu sinal e sua
unidade precisam acompanhar o registro [@jcgm2012].

::: {.equacao identificador="eq:desvio" fonte="Relação didática de diferença entre valores de uma mesma grandeza."}
$$
\Delta x = x_{\mathrm{observado}} - x_{\mathrm{referência}}
$$
:::

# Síntese

O registro permite revisar o resultado quando identifica a origem dos dados,
as condições de obtenção e o critério usado na decisão. O exemplo não define
tolerâncias para equipamentos reais.

# Referências {.unnumbered}

::: {#refs}
:::
