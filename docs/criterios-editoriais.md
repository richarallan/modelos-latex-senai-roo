# Citações, elementos numerados e critérios editoriais

## Referencial adotado e alcance da consulta

Consulta realizada em 11 de novembro de 2026. O projeto usa como referencial:

No pedido de ajuste das fórmulas, o número “14742” foi interpretado como
provável transposição de **14724**: o referencial encontrado para apresentação
de trabalhos acadêmicos e expressões matemáticas é a **NBR 14724:2024**.
Essa interpretação não afirma a inexistência de outra norma com o número citado.

| Documento | Aplicação nesta implementação |
|---|---|
| ABNT NBR 6022:2018 | Artigo técnico/científico; o modelo institucional aprovado continua determinando as margens, a tipografia e os pré-textuais. |
| ABNT NBR 10520:2023 | Sistema autor-data, chamadas narrativas/parentéticas e localizadores de citações. |
| ABNT NBR 6023:2025 | Organização dos dados bibliográficos e das referências. |
| ABNT NBR 14724:2024 | Referência subsidiária de apresentação de ilustrações, títulos, fontes e equações; não é uma migração para ABNTeX. |
| IBGE, *Normas de apresentação tabular*, 3. ed., 1993 | Apresentação de dados numéricos em tabelas, com título, fonte/notas e linhas laterais abertas. |

Foram consultadas implementações acadêmicas abertas e seus comentários:

- [Modelo de artigo do projeto abnTeX2, versão fixada](https://github.com/abntex/abntex2/blob/0cb2fe32e3ca5dbcbb08098497603777837f5098/doc/latex/abntex2/examples/abntex2-modelo-artigo.tex), que identifica a NBR 6022:2018 e explica que ela não fixa margens específicas para artigos.
- [Exemplos matemáticos do mesmo projeto](https://github.com/abntex/abntex2/blob/0cb2fe32e3ca5dbcbb08098497603777837f5098/doc/latex/abntex2/examples/abntex2-modelo-include-comandos.tex#L273-L292), com equação destacada e numerada, sem legenda gráfica.
- [Exemplo matemático da implementação UNIVALI](https://github.com/fockingf/template-latex-univali/blob/ce0a677426f796c91bbe2e03202e57faf2c64308/tex/fundamentacao-teorica.tex#L106-L118), com referência cruzada e explicação de variáveis em prosa.
- [Referências do mesmo modelo](https://github.com/abntex/abntex2/blob/0cb2fe32e3ca5dbcbb08098497603777837f5098/doc/latex/abntex2/examples/referencias.bib), incluindo a publicação tabular do IBGE.
- [Implementação acadêmica para UNIVALI, versão fixada](https://github.com/fockingf/template-latex-univali/blob/ce0a677426f796c91bbe2e03202e57faf2c64308/README.md), que declara as edições 2024/2025/2023 e os critérios de títulos/fontes. Trata-se de uma implementação secundária, não de publicação normativa oficial da universidade.
- [Implementação acadêmica PPgEA/UFRN](https://github.com/paoloo/PPGEA-UFRN-Template), que também documenta as edições adotadas.
- [Origem, versão e licença do CSL usado pelo renderizador](../templates/bibliografia/FONTE.md).

Os textos integrais no catálogo ABNT e as páginas originais do IBGE não ficaram
acessíveis neste ambiente (bloqueio de rede). Assim, esta documentação registra
os critérios implementados com apoio dessas fontes secundárias; não afirma
consulta direta aos textos integrais nem certificação de conformidade completa.
O CSL é comunitário e tem licença própria, preservada no repositório.

## Decisões de apresentação

- As chamadas usam autor-data: `JCGM (2012)` ou `(JCGM, 2012)`. Sobrenomes em
  caixa mista nas chamadas seguem o referencial de 2023; siglas institucionais
  preservam sua grafia. Citações diretas devem informar página ou outro localizador.
- O citeproc gera as referências em ordem alfabética e faz a desambiguação de
  autores/anos quando necessária. Nome, título, edição, data, editora, local,
  DOI/URL e acesso vêm dos dados bibliográficos fornecidos, sem preenchimento inventado.
- Figuras e gráficos têm identificação, número arábico, travessão e título
  acima da imagem. A fonte aparece abaixo, inclusive nas elaborações próprias.
  A nota aparece somente quando informada. Nos elementos isolados, que ocupam
  uma linha de composição, a legenda fica centralizada na largura do bloco;
  fonte e nota continuam à esquerda. Nos painéis de duas ou mais imagens,
  títulos e conteúdo das células alinham à esquerda e pelo topo. Essa distinção
  estética foi solicitada para o projeto; não é atribuída como imposição da ABNT.
- Tabelas têm título acima, cabeçalhos e regras horizontais, fonte e nota
  abaixo, com laterais abertas. O exemplo numérico e o gráfico compartilham
  os mesmos quatro valores, explicitamente simulados. Conteúdo predominantemente
  textual costuma exigir tratamento de quadro, que não foi acrescentado nesta etapa.
- Fórmulas destacadas usam espaço suficiente para índices e expoentes. Quando
  numeradas, recebem algarismos arábicos entre parênteses à direita. A expressão
  fica centralizada e não recebe legenda gráfica “Equação N — título”. A origem
  e a explicação podem ser apresentadas em prosa ou citação próxima à fórmula.
  O campo opcional `titulo`, se mantido em documentos anteriores, é apresentado
  como prosa introdutória, sem prefixo e sem numeração adicional. `fonte` e
  `nota` continuam opcionais como recursos pedagógicos, não como exigência normativa.
- Cada tipo tem sequência própria: Figura 1, Gráfico 1, Tabela 1, Equação (1).
  Essa separação e os links internos são escolhas de implementação. Os números
  são recalculados pela ordem dos objetos a cada geração, nunca pelo nome do ID.
- As legendas/fontes/notas usam 10 pontos e entrelinha de 12 pontos. As
  referências usam espaço simples. Corpo, capas, folha de rosto, autores,
  logotipo e regras condicionais de cidade/data preservam a composição aprovada.
  No núcleo consolidado, campos sem conteúdo não geram rótulos, linhas de
  assinatura ou páginas vazias; a aprovação exige dados efetivos.

## Bibliografia estruturada e chamadas

No cabeçalho do Markdown, informe um arquivo relativo ao próprio documento:

```yaml
bibliografia: referencias/artigo.yaml
```

Também é aceita uma lista de arquivos. Use CSL-YAML com a chave `references`
ou CSL-JSON com uma lista na raiz. BibTeX não é aceito por esta interface.

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

O exemplo acima usa uma publicação real com autoria corporativa, sem dados
pessoais fictícios. O artigo do repositório mantém sua bibliografia em
[`exemplos/referencias/artigo.yaml`](../exemplos/referencias/artigo.yaml).

```markdown
A terminologia de medição é apresentada por @jcgm2012.
A mesma obra pode ser chamada entre parênteses [@jcgm2012].

# Referências {.unnumbered}

::: {#refs}
:::
```

Os IDs bibliográficos são estáveis e sensíveis a maiúsculas/minúsculas. Cada
referência deve ter `id`, `type` e `title`; os demais campos devem refletir a
publicação real. IDs duplicados entre arquivos são rejeitados. As chamadas
criam links internos para a entrada correspondente. Se `#refs` não for
informado, o citeproc acrescenta a bibliografia ao final do documento.
A lista inclui as obras citadas no texto; cadastrar uma obra não equivale a
citá-la.

## Objetos e referências cruzadas em Markdown

Use os prefixos `fig:`, `gra:`, `tab:` e `eq:`. Após o prefixo, escolha um nome
estável com letras ASCII, números, hífen, ponto ou sublinhado. Não escreva o
número no ID: `fig:motor-bomba` continua correto depois de inserir outra figura.
Os IDs devem ser únicos em todo o documento.
Use esses blocos para todos os elementos que precisam participar das sequências
e das referências cruzadas; imagens e fórmulas soltas não entram nessa contagem.

```markdown
A disposição aparece na @fig:motor-bomba. Os dados estão em @tab:desvios
e no @gra:verificacoes; o cálculo usa a @eq:desvio.

::: {.figura #fig:motor-bomba titulo="Conjunto motor-bomba" fonte="Elaboração própria (2026)." nota="Esquema sem escala."}
![Motor, acoplamento e bomba sobre base comum.](recursos/conjunto-motor-bomba.png){width=80%}
:::

::: {.tabela #tab:desvios titulo="Desvios dimensionais simulados" fonte="Elaboração própria, com dados simulados (2026)."}
| Verificação | Desvio (mm) |
|:---|---:|
| 1ª | 0,18 |
| 2ª | 0,12 |
:::

::: {.grafico #gra:verificacoes titulo="Verificações simuladas" fonte="Elaboração própria, com dados simulados (2026)."}
![Desvios em duas verificações.](recursos/grafico-medicoes.pdf){width=85%}
:::

::: {.equacao #eq:desvio titulo="Desvio dimensional" fonte="Elaboração própria."}
$$
\Delta x = x_{observado} - x_{referencia}
$$
:::
```

Cada bloco visual contém exatamente uma imagem ou tabela. Título e fonte são
obrigatórios para figura, gráfico e tabela; nota é opcional. Na equação, título
e fonte são opcionais e o conteúdo deve ser um bloco matemático destacado.
Objetos numerados não podem ser aninhados em outro objeto numerado; o painel
descrito abaixo é um container sem número, com filhos visuais identificados.

Título, fonte e nota aceitam texto Markdown simples e citações, por exemplo
`fonte="Adaptado de [@jcgm2012]."`. Figuras e gráficos aceitam imagens em
formatos compatíveis com XeLaTeX, como PNG e PDF; o gráfico do exemplo é vetorial.
As tabelas podem continuar em outras páginas; revise a composição de tabelas
longas no documento final, inclusive identificação de continuação conforme a
regra institucional aplicável.
Para uma tabela curta, como a do exemplo, `manter_junto="true"` conserva
identificação, dados, fonte e nota no mesmo bloco, movendo-o à próxima página
quando necessário. Não use essa opção para uma tabela maior que a área útil
de uma página; sem ela, a paginação da tabela permanece disponível.

As chamadas `@fig:motor-bomba` etc. já incluem o tipo e o número. São resolvidas
mesmo quando aparecem antes do objeto. Ao inserir ou reorganizar os blocos,
gere novamente o documento: rótulos e chamadas acompanham a nova ordem.
Não é necessário escrever comandos LaTeX de legenda, numeração, `label` ou `ref`.

## Fórmulas simples e em várias linhas

A numeração é aplicada aos blocos `.equacao` com ID estável, necessários às
chamadas no texto. Fórmulas em linha (`$...$`) e expressões soltas (`$$...$$`)
permanecem sem essa numeração. O ambiente matemático comporta frações,
expoentes e índices sem reduzir a entrelinha do texto para acomodá-los.

```markdown
A relação é apresentada na @eq:desvio-relativo.

::: {.equacao #eq:desvio-relativo}
$$
\varepsilon_r &= \frac{\Delta x}{x_{referencia}} \\
E_r &= 100\,\varepsilon_r
$$
:::
```

As quebras matemáticas `\\` e os marcadores `&` são organizados em `aligned`
pelo filtro quando aparecem no nível externo da expressão. Ambientes já
escritos pelo autor são preservados: um `aligned` externo não é duplicado e
`cases` ou matrizes internas podem participar de uma expressão maior, alinhada.
Marcadores escapados e comentários não provocam alinhamento. O bloco recebe
um único número à direita, inclusive quando tem mais de uma linha.
As quebras devem respeitar o raciocínio matemático;
não há tentativa de partir automaticamente uma expressão em qualquer símbolo.

## Imagens lado a lado

Use `.figura`, `.grafico` ou os aliases `.ilustracao` e `.desenho`. Os dois
aliases compartilham a designação e a sequência **Figura**, com IDs `fig:`.
Elementos isolados têm título centralizado; o painel torna explícita a escolha
de colocar imagens lado a lado, evitando depender da proporção do arquivo.

```markdown
:::: {.painel-imagens colunas=2}
::: {.desenho #fig:motor titulo="Motor elétrico" fonte="Elaboração própria (2026)."}
![Motor elétrico.](recursos/motor-eletrico.png){width=100%}
:::

::: {.ilustracao #fig:bomba titulo="Bomba centrífuga" fonte="Elaboração própria (2026)."}
![Bomba centrífuga.](recursos/bomba-centrifuga.png){width=100%}
:::
::::
```

O painel aceita de duas a quatro colunas, com duas por padrão, e pelo menos
dois elementos visuais como filhos diretos. Cada elemento mantém ID, título,
fonte, nota e chamada próprios. A contagem continua na ordem de leitura do
documento; o painel não cria uma segunda numeração. Elementos excedentes são
distribuídos em novas linhas, com espaçamento entre células e alinhamento no topo.

A largura da imagem é relativa à célula; `width=100%` aproveita sua área útil.
No painel, são aceitas larguras percentuais maiores que zero e até 100%; medidas
absolutas ficam reservadas aos objetos isolados para evitar ultrapassar a célula.
Títulos e conteúdo das células ficam à esquerda. Tabelas, equações e painéis
aninhados são rejeitados dentro desse container. Figuras muito detalhadas ou
legendas extensas devem ficar isoladas para preservar a legibilidade. Fontes
e notas seguem obrigatórias/opcionais conforme as mesmas regras do objeto isolado.

## Geração e validação

Na raiz do repositório:

```bash
python scripts/renderizar.py exemplos/artigo-exemplo.md
python scripts/renderizar.py exemplos/artigo-exemplo.md --validar-apenas
python -m unittest discover --start-directory tests --verbose
```

O primeiro comando valida e gera TEX/PDF. O segundo também executa os filtros
e o citeproc, descartando a saída TEX: não gera PDF nem altera arquivos de saída.
São erros: recurso/bibliografia inexistente, ID inválido ou repetido, objeto
sem título/fonte exigidos, referência cruzada ausente e citação sem cadastro.
Avisos do Pandoc/citeproc tornam a execução malsucedida.

O CI em Ubuntu 24.04 utiliza o Pandoc 3.1.3 do repositório da distribuição.
Essa versão ainda escreve as referências como parágrafos, enquanto o Pandoc
3.1.11.1 usa itens bibliográficos. O filtro inspeciona a convenção real do
writer para selecionar o ambiente compatível; o número principal da versão
não é suficiente para essa decisão. As versões verificadas para esse caminho
incluem 2.17.1.1, 3.1.3 e 3.1.11.1. O workflow registra as versões das ferramentas
nos logs de instalação para facilitar a reprodução de falhas.

Os testes inserem e reorganizam objetos dos quatro tipos, verificam as chamadas
e os destinos, exercitam citações narrativas/parentéticas e compilam um PDF sem
interrogações de referências não resolvidas. Uma pergunta legítima em outro
documento não deve ser confundida com uma referência quebrada.

A ilustração motor-bomba foi criada para este exemplo com apoio de inteligência
artificial. O gráfico contém dados simulados, não resultados de pesquisa ou de
uma manutenção real. Essas origens também aparecem no PDF, junto aos elementos.


## Núcleo documental e catálogo compartilhado

A consolidação separa Markdown/YAML, interpretação e geração comuns, perfis
documentais e apresentação visual. Os perfis `artigo`, `nota_aula` e
`atividade_avaliativa` consomem a mesma representação semântica Pandoc JSON;
numeração, IDs e validação não são reimplementados por template.

A [matriz de cobertura](matriz-cobertura.md) delimita todos os elementos
suportados e suas condições. O [kit](../kit/README.md) fornece entradas prontas
e propriedades chave-valor (`identificador`, `titulo`, `arquivo`, `fonte`,
`nota`, `idioma`); `#id` e imagens Markdown continuam compatíveis. Parágrafos,
títulos e listas permanecem em Markdown comum.

Capa e folha de rosto mantêm a apresentação institucional aprovada. Orientação,
contato, coordenação e membros da banca aparecem apenas quando fornecidos;
campos ausentes não são substituídos por rótulos ou assinaturas vazias. A
página de aprovação só é criada quando há dados de coordenação, banca ou data
de aprovação. `pre_textuais: false` continua permitindo iniciar pelo corpo.
Resumo ausente ou vazio não gera título; palavras-chave ausentes ou em lista
vazia não geram rótulo. Cidade e data não são inferidas.

O artigo original e seu PDF aprovado permanecem como referência de regressão.
As [demonstrações do núcleo](../exemplos/nucleo/) são arquivos separados, com
autoria coletiva e sem pessoas ou contatos inventados. A existência do `.doc`
de relatório é apenas uma referência para uma etapa posterior, não uma
implementação de novo modelo.
