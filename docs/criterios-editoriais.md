# Citações, elementos numerados e critérios editoriais

## Referencial adotado e alcance da consulta

Consulta realizada em 11 de novembro de 2026. O projeto usa como referencial:

| Documento | Aplicação nesta implementação |
|---|---|
| ABNT NBR 6022:2018 | Artigo técnico/científico; o modelo institucional aprovado continua determinando as margens, a tipografia e os pré-textuais. |
| ABNT NBR 10520:2023 | Sistema autor-data, chamadas narrativas/parentéticas e localizadores de citações. |
| ABNT NBR 6023:2025 | Organização dos dados bibliográficos e das referências. |
| ABNT NBR 14724:2024 | Referência subsidiária de apresentação de ilustrações, títulos, fontes e equações; não é uma migração para ABNTeX. |
| IBGE, *Normas de apresentação tabular*, 3. ed., 1993 | Apresentação de dados numéricos em tabelas, com título, fonte/notas e linhas laterais abertas. |

Foram consultadas implementações acadêmicas abertas e seus comentários:

- [Modelo de artigo do projeto abnTeX2, versão fixada](https://github.com/abntex/abntex2/blob/0cb2fe32e3ca5dbcbb08098497603777837f5098/doc/latex/abntex2/examples/abntex2-modelo-artigo.tex), que identifica a NBR 6022:2018 e explica que ela não fixa margens específicas para artigos.
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

- As chamadas usam autor-data: `Silva (2023)` ou `(Silva, 2023)`. Sobrenomes em
  caixa mista nas chamadas seguem o referencial de 2023; siglas institucionais
  preservam sua grafia. Citações diretas devem informar página ou outro localizador.
- O citeproc gera as referências em ordem alfabética e faz a desambiguação de
  autores/anos quando necessária. Nome, título, edição, data, editora, local,
  DOI/URL e acesso vêm dos dados bibliográficos fornecidos, sem preenchimento inventado.
- Figuras e gráficos têm identificação, número arábico, travessão e título
  acima da imagem. A fonte aparece abaixo, inclusive nas elaborações próprias.
  A nota aparece somente quando informada. Ambos ficam alinhados à esquerda
  dentro da largura da imagem; a imagem é centralizada.
- Tabelas têm título acima, cabeçalhos e regras horizontais, fonte e nota
  abaixo, com laterais abertas. O exemplo numérico e o gráfico compartilham
  os mesmos quatro valores, explicitamente simulados. Conteúdo predominantemente
  textual costuma exigir tratamento de quadro, que não foi acrescentado nesta etapa.
- Equações destacadas recebem números entre parênteses à direita. O título e
  a fonte adicionais são recursos pedagógicos opcionais do projeto, não uma
  exigência atribuída à ABNT.
- Cada tipo tem sequência própria: Figura 1, Gráfico 1, Tabela 1, Equação (1).
  Essa separação e os links internos são escolhas de implementação. Os números
  são recalculados pela ordem dos objetos a cada geração, nunca pelo nome do ID.
- As legendas/fontes/notas usam 10 pontos e entrelinha de 12 pontos. As
  referências usam espaço simples. Corpo, capas, folha de rosto, autores,
  logotipo e regras condicionais de cidade/data permanecem no modelo aprovado.

## Bibliografia estruturada e chamadas

No cabeçalho do Markdown, informe um arquivo relativo ao próprio documento:

```yaml
bibliografia: referencias/artigo.yaml
```

Também é aceita uma lista de arquivos. Use CSL-YAML com a chave `references`
ou CSL-JSON com uma lista na raiz. BibTeX não é aceito por esta interface.

```yaml
references:
  - id: silva2023
    type: book
    author:
      - family: Silva
        given: Ana
    title: "Manual de inspeção mecânica"
    issued:
      date-parts: [[2023]]
    publisher: "Editora de exemplo"
    publisher-place: "Cuiabá"
```

O exemplo acima é uma referência fictícia para demonstrar a sintaxe. O artigo
do repositório possui sua própria bibliografia em
[`exemplos/referencias/artigo.yaml`](../exemplos/referencias/artigo.yaml).

```markdown
Segundo @silva2023, o registro deve permitir a revisão das evidências.
A mesma origem pode ser chamada entre parênteses [@silva2023, p. 17].

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
e fonte são opcionais e o conteúdo deve ser uma única expressão matemática
destacada. Objetos numerados não podem ser aninhados.

Título, fonte e nota aceitam texto Markdown simples e citações, por exemplo
`fonte="Adaptado de [@silva2023]."`. Figuras e gráficos aceitam imagens em
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

Os testes inserem e reorganizam objetos dos quatro tipos, verificam as chamadas
e os destinos, exercitam citações narrativas/parentéticas e compilam um PDF sem
interrogações de referências não resolvidas. Uma pergunta legítima em outro
documento não deve ser confundida com uma referência quebrada.

A ilustração motor-bomba foi criada para este exemplo com apoio de inteligência
artificial. O gráfico contém dados simulados, não resultados de pesquisa ou de
uma manutenção real. Essas origens também aparecem no PDF, junto aos elementos.
