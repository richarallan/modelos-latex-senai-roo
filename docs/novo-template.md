# Criar o próximo template

Um template apresenta um documento já interpretado. Ele não deve ler o Markdown
por conta própria, inventar metadados, numerar objetos novamente nem implementar
um segundo mecanismo de citações ou referências.

O fluxo compartilhado é:

```text
Markdown + YAML
       ↓
núcleo: leitura, contrato, interpretação e validação
       ↓
representação semântica Pandoc JSON
       ↓
apresentador compartilhado + perfil + template visual
       ↓
LaTeX → XeLaTeX → PDF
```

TEX e PDF de um mesmo documento partem da mesma representação. O DOCX
preservado dos perfis pedagógicos usa essa mesma interpretação, com o
apresentador correspondente ao formato. A saída Word do artigo e do relatório permanece
reservada para uma etapa posterior.

## 1. Defina a diferença que pertence ao perfil

Use um perfil para selecionar apresentação, formatos permitidos, classe,
sumário e elementos pré-textuais. O tipo documental expressa a finalidade do
conteúdo e continua sendo `nota_aula` ou `atividade_avaliativa`; criar uma
aparência não exige criar um tipo novo.

Os perfis atuais ficam em [`perfis/`](../perfis/). Um contrato de perfil tem a
seguinte forma; adapte os valores aos recursos realmente implementados:

```json
{
  "versao": 1,
  "id": "proximo_modelo",
  "tipos_documentais": ["nota_aula", "atividade_avaliativa"],
  "template": "templates/proximo-modelo/documento.latex",
  "classe": "senaiarticle",
  "opcoes_classe": [],
  "formatos": ["tex", "pdf"],
  "sumario": false,
  "pre_textuais": false,
  "paginas_pre_textuais": []
}
```

`template: null` seleciona o template padrão do Pandoc, como nos perfis
pedagógicos legados. `id` é o valor de `modelo` no YAML. Os caminhos são
relativos à raiz do repositório, não ao diretório do documento.

`paginas_pre_textuais` declara quais páginas o perfil admite: `capa`,
`folha_rosto` e `aprovacao`. Quando `pre_textuais` for `true`, essa lista é
obrigatória e deve conter pelo menos uma página. Artigo e relatório declaram
as três; um perfil pode oferecer somente capa e folha de rosto, por exemplo.
Com `pre_textuais: false`, a lista pode ficar vazia ou ser omitida.
Os controles do Markdown e a exigência de dados de aprovação continuam sendo
aplicados. O gerador não precisa conhecer o nome do novo modelo para ativar
as páginas admitidas.

O [relatório](relatorio.md) é um exemplo implementado dessa extensão:
`perfis/relatorio.json` seleciona `templates/Relatorio/relatorio.latex`, que
reutiliza o preâmbulo comum do artigo em `templates/comum/preambulo.latex`.
A capa e as quebras de seções pertencem à apresentação; objetos, referências,
numeração e citações continuam no núcleo comum.

## 2. Acrescente o perfil ao contrato

Crie `perfis/proximo_modelo.json` com o contrato acima. Registre o identificador
no contrato de metadados quando houver uma lista explícita de modelos
permitidos. Confira que os tipos documentais e formatos do perfil são válidos.
O carregador deve rejeitar um perfil inválido ou um template inexistente com
uma mensagem clara, antes da geração.

O contrato é validado por `schemas/perfil.schema.json`. Recursos visuais
opcionais ficam em `recursos`, um mapa de variável do template para arquivo
relativo à raiz, por exemplo `"logo": "templates/proximo-modelo/logo.png"`.
O carregador valida a existência do arquivo e o entrega como variável ao
template, sem acrescentar uma regra por nome de modelo ao gerador.

Não inclua decisões de numeração, resolução de IDs, validação bibliográfica ou
interpretação de blocos no arquivo de perfil.

## 3. Escreva apenas a apresentação

Crie o template visual indicado pelo perfil. Ele recebe os mesmos metadados e
o mesmo corpo semântico que os modelos existentes. Reutilize a classe, os
ambientes e os fragmentos compartilhados quando forem adequados.

No template Pandoc, use condições ao redor de cada elemento opcional:

```latex
$if(subtitle)$
{\large $subtitle$\par}
$endif$

$if(resumo)$
\section*{Resumo}
$resumo$
$endif$

$body$
```

A condição deve envolver também o título, o espaço ou a página associados ao
campo. Um `\newpage` fora da condição pode criar uma página vazia mesmo quando
o texto foi omitido. Não acrescente linhas de assinatura genéricas, cidade,
data, nomes, cargos ou contatos para compensar dados ausentes.

O corpo já contém os elementos preparados pelo apresentador comum. Regras
visuais como cores, fontes, margens, espaços, caixas e alinhamentos pertencem
ao template ou à classe. O cálculo de números, o inventário de IDs e a
resolução dos links pertencem ao núcleo.

## 4. Preserve o catálogo comum

O template deve aceitar todo o [catálogo de elementos](matriz-cobertura.md)
suportado pelos perfis atuais: Markdown nativo, blocos pedagógicos, objetos
numerados, painéis e bibliografia. Evite implementar uma versão local de um
elemento porque ele precisa de outra cor ou outro espaçamento.

Se for necessário acrescentar um significado novo, atualize primeiro o
catálogo, a interpretação e a validação compartilhados. Depois acrescente a
apresentação para os formatos suportados. Documente propriedades obrigatórias,
opcionais e compatibilidade. Mantenha `identificador`, `titulo`, `arquivo`,
`fonte`, `nota` e `idioma` como propriedades chave-valor quando aplicáveis.

Não substitua parágrafos, títulos ou listas do Markdown comum por novos blocos
de configuração. Um novo template deve consumir a representação existente
sem exigir que o conteúdo seja reescrito.

## 5. Forneça uma entrada utilizável

Acrescente um Markdown inicial ao [kit de modelos](../kit/modelos/), um exemplo
mínimo e uma demonstração completa. Use autoria institucional, coletiva ou
dados reais fornecidos pela pessoa responsável. Não use dados pessoais
fictícios nem publicações bibliográficas inventadas.

Atualize o guia rápido com o campo `modelo` e informe qualquer limitação real
de formato. Preserve o documento de referência visual, como ocorre com
`templates/Relatorio/Modelo Relatorio.doc`, e documente quais regras vieram
dele e quais são opções do novo perfil.

## 6. Teste o contrato e a apresentação

Valide pelo menos:

- exemplo mínimo válido, todos os obrigatórios e cada obrigatório ausente;
- opcionais ausentes, vazios e preenchidos, sem páginas ou rótulos vazios;
- autoria em texto e lista, preservando a ordem;
- objetos com `identificador` e `arquivo`, além da sintaxe legada;
- duplicidade de IDs, links sem destino e arquivos ausentes;
- inserção e reorganização de figuras, gráficos, tabelas e equações;
- títulos, fontes, notas, citações e destinos internos no PDF;
- matemática com várias linhas, tabelas e painéis;
- idiomas suportados e metadados inválidos;
- geração com a versão do Pandoc usada no CI.

Gere o artigo de referência pela mesma cadeia e confira as regressões antes
de concluir. Preserve o PDF aprovado e use um novo arquivo para a demonstração
do novo modelo.

## 7. Gere e confira o resultado

Com o perfil implementado e registrado, a interface de geração continua sendo:

```bash
python scripts/renderizar.py caminho/documento.md --validar-apenas
python scripts/renderizar.py caminho/documento.md
python -m unittest discover --start-directory tests --verbose
```

O comando padrão gera TEX e PDF. Revise os PDFs visualmente, atualize a matriz
de cobertura e acrescente o novo exemplo às verificações de CI. A configuração
do workflow deve instalar as dependências visuais necessárias sem duplicar o
fluxo de interpretação do documento.
