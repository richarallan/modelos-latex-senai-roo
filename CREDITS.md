# Créditos

## Referência original

Este projeto reconhece e agradece o trabalho de **Emerson Mello**, professor do
Instituto Federal de Santa Catarina (IFSC), autor do repositório
[emersonmello/modelos-latex](https://github.com/emersonmello/modelos-latex).

O projeto original está disponibilizado sob a dedicação ao domínio público
**Creative Commons Zero — CC0 1.0 Universal**. Embora a CC0 dispense atribuição
como condição de reutilização, este registro é mantido por reconhecimento
acadêmico, transparência e respeito ao trabalho que tornou esta iniciativa
possível.

Referência consultada para esta etapa:

- repositório: `emersonmello/modelos-latex`;
- branch: `master`;
- commit: [`b7660256425e58fa81d3cf7919832247ff564721`](https://github.com/emersonmello/modelos-latex/commit/b7660256425e58fa81d3cf7919832247ff564721);
- data da consulta: 11 de novembro de 2026;
- licença declarada no repositório original: CC0 1.0 Universal.

Foram estudadas principalmente a separação por tipos documentais e as
responsabilidades das classes e modelos presentes em:

- `classes/ifscarticle.cls`;
- `classes/ifscexam.cls`;
- `classes/ifscutils.sty`;
- `lista-ou-prova/lista-ou-prova-exam.tex`;
- `nota-de-aula/nota-de-aula.tex`;
- `plano-de-ensino/plano-de-ensino.tex`;
- `relatorio/relatorio.tex`.

O código do primeiro MVP deste repositório não é uma cópia literal desses
arquivos. Ele adota uma arquitetura própria, baseada em documento canônico,
JSON Schema, Markdown, Pandoc, filtro Lua, classe LaTeX e referência DOCX.

## Adaptação para o contexto educacional local

**Richar Allan Macedo da Silva** iniciou e mantém esta adaptação voltada à
produção de materiais educacionais em Rondonópolis, Mato Grosso.

O primeiro MVP estabelece um contrato documental independente da ferramenta de
inteligência artificial utilizada. A IA pode redigir ou classificar o conteúdo;
o esquema valida a estrutura; e renderizadores determinísticos produzem TEX,
PDF e DOCX.

## Modelo visual de artigo

O perfil de artigo toma como referência o arquivo
[`Modelo Artigo.docx`](templates/artigo/original/Modelo%20Artigo.docx),
já fornecido no repositório. Foram preservadas a estrutura dos elementos
pré-textuais, a hierarquia dos títulos, as margens e a tipografia acadêmica.
Os arquivos originais não foram modificados.

A imagem `templates/artigo/recursos/logo-senai.png` é uma cópia integral de
`word/media/image1.png` desse DOCX. A utilização da marca continua sujeita
aos direitos de seus titulares; a adaptação não atribui uma licença nova
à imagem ou ao documento de referência.

## Independência institucional e direitos de terceiros

O estilo bibliográfico `templates/bibliografia/abnt-autor-data.csl` é de
**Ícaro Gonçalves Pereira**, distribuído sob **CC BY-SA 3.0**, com origem e versão
fixadas em [FONTE.md](templates/bibliografia/FONTE.md). Ele mantém essa licença
própria, distinta da CC0 aplicada ao código original do projeto.

A ilustração motor-bomba foi gerada para o exemplo com apoio de inteligência
artificial. O gráfico utiliza quatro dados simulados para fins didáticos.
Ambos têm suas fontes explicitadas no Markdown e no PDF, sem representar
resultados experimentais ou projetos construtivos de equipamentos.

Este repositório não representa endosso, participação ou responsabilidade de
Emerson Mello, do IFSC, do SENAI ou de suas entidades mantenedoras sobre as
adaptações aqui realizadas.

A dedicação CC0 deste repositório alcança somente os direitos que cada
colaborador pode validamente disponibilizar. Ela não concede direitos sobre
marcas, logotipos, fotografias, fontes, dados pessoais ou materiais de
terceiros. Cada contribuição futura deve identificar separadamente eventuais
fontes e licenças aplicáveis.
