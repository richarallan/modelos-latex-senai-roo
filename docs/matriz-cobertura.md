# Matriz de cobertura do núcleo documental

Esta matriz delimita o catálogo oferecido pelo projeto. Os perfis `artigo`,
`nota_aula` e `atividade_avaliativa` compartilham a interpretação e a
representação semântica; o perfil escolhe os recursos de saída e a apresentação.
Um elemento não precisa ser incluído em todo documento para que o perfil o
suporte. Campos, blocos e páginas opcionais ausentes não são preenchidos com
dados inventados.

Os exemplos copiáveis estão no [catálogo do kit](../kit/elementos.md). Os
[modelos iniciais](../kit/modelos/) e as
[demonstrações](../exemplos/nucleo/) fornecem documentos geráveis, com caminhos
de recursos e metadados completos. O [artigo aprovado](../exemplos/artigo-exemplo.pdf)
é a referência preservada de regressão visual; as demonstrações do núcleo são
arquivos separados.

## Como ler a cobertura

- **Todos**: os três perfis, em TEX e PDF. DOCX permanece disponível apenas
  nos perfis pedagógicos anteriores.
- **Nativo**: escreva Markdown comum. Não crie um bloco especial para
  parágrafos, títulos ou listas.
- **Semântico**: o núcleo interpreta o bloco ou a propriedade uma vez,
  valida e registra seu significado na representação Pandoc JSON compartilhada.
- **Apresentação**: o template ou a classe apenas compõe os dados já
  interpretados; não calcula novamente números nem resolve identificadores.

As referências a testes abaixo identificam os casos de regressão existentes.
Os novos casos de interpretação, validação e integração estão em
[`tests/test_nucleo.py`](../tests/test_nucleo.py), detalhados na seção de
rastreabilidade desta matriz. A presença de um caso na matriz não é um
relatório de execução: o resultado da suíte é registrado nas verificações do PR.
A execução completa, inclusive os casos adicionados na consolidação, deve
passar com o Pandoc 3.1.3 usado pelo CI. A geração de demonstrações complementa
os testes; uma compilação bem-sucedida, isoladamente, não demonstra a correção
visual de todos os elementos.

## Conteúdo em Markdown comum

| Elemento | Forma / significado | Propriedades obrigatórias e opcionais | Perfis | Evidência de cobertura |
|---|---|---|---|---|
| Parágrafo | Texto separado por linha em branco | Sem propriedades especiais | Todos | Demonstrações mínima e completa; regressão do corpo do artigo |
| Título e subtítulo de seção | `#`, `##`, `###` | Texto; ID estável opcional | Todos | Seções dos exemplos; teste de metadados e corpo em `test_artigo.py` |
| Lista não ordenada | `- item` | Conteúdo dos itens | Todos | Demonstração completa |
| Lista ordenada | `1. item` | Conteúdo dos itens; sequência do Markdown | Todos | Demonstração completa |
| Ênfase e destaque | `*texto*`, `**texto**` | Texto | Todos | Demonstração completa |
| Citação em bloco | `> texto` | Texto; a origem deve ser informada quando aplicável | Todos | Demonstração completa |
| Código em linha e bloco | Crases; bloco com três crases | Conteúdo; linguagem opcional | Todos | Demonstração completa |
| Matemática em linha | `$x$` | Expressão matemática | Todos | Exemplos matemáticos e `test_matematica_paineis.py` |
| Matemática destacada sem número | `$$...$$` fora de `.equacao` | Expressão matemática | Todos | Demonstração completa; não integra a sequência de equações |
| Imagem simples | `![descrição](arquivo)` | Arquivo existente; texto alternativo recomendado | Todos | Validação de recursos e demonstração completa |
| Tabela simples | Tabela Markdown com cabeçalho | Cabeçalho e células | Todos | Demonstração completa; não integra a sequência de tabelas numeradas |
| Link externo | `[texto](https://...)` | Destino e texto | Todos | Conteúdo e links das demonstrações; não exige consulta de rede para gerar |
| Link interno comum | `[texto](#destino)` | Destino existente; ID único | Todos | Validação semântica de destinos; testes do núcleo |
| Nota de rodapé | `[^nota]` e definição correspondente | Chamada e definição | Todos | Demonstração completa |

Um título sem número continua sendo Markdown comum, por exemplo
`# Referências {.unnumbered}`. Não escreva o número de uma figura ou de uma
equação manualmente no texto: use a chamada semântica correspondente.

## Blocos pedagógicos

Todos os blocos abaixo aceitam conteúdo Markdown. `identificador` e `titulo`
são propriedades opcionais quando utilizadas pelo bloco; `#id` continua
compatível como forma de informar o identificador. Blocos sem conteúdo útil
não devem gerar caixas ou títulos vazios.

| Elemento | Significado | Campos específicos | Perfis | Evidência de cobertura |
|---|---|---|---|---|
| `objetivo` | Resultado de aprendizagem pretendido | Conteúdo | Todos | Exemplo de nota de aula e demonstração completa |
| `situacao_problema` | Contexto que mobiliza a atividade | Conteúdo | Todos | Exemplo de atividade e demonstração completa |
| `questao` | Solicitação de resposta ou produção | Conteúdo; `pontos` e `tipo` opcionais | Todos | Exemplo de atividade e demonstração completa |
| `seguranca` | Condição ou procedimento de segurança | Conteúdo | Todos | Exemplo de atividade e demonstração completa |
| `pratica` | Orientação para execução prática | Conteúdo | Todos | Exemplo de nota de aula e demonstração completa |
| `rubrica` | Critério de avaliação | Conteúdo | Todos | Exemplo de atividade e demonstração completa |
| `atencao` | Observação que precisa de destaque | Conteúdo | Todos | Exemplo de nota de aula e demonstração completa |

## Objetos, composição e referências

| Elemento | Significado / sequência | Campos obrigatórios | Campos opcionais | Perfis e cobertura |
|---|---|---|---|---|
| `figura` | Ilustração numerada; sequência `fig:` | `identificador`, `titulo`, `fonte` e imagem por `arquivo` ou Markdown | `nota`, `idioma`; dimensões da imagem | Todos; `test_referencias.py` |
| `ilustracao` | Alias de `figura`; mesma sequência | Os mesmos de `figura` | Os mesmos de `figura` | Todos; `test_ilustracao_e_desenho_usam_a_mesma_sequencia_de_figuras` |
| `desenho` | Alias de `figura`; mesma sequência | Os mesmos de `figura` | Os mesmos de `figura` | Todos; mesmo teste de aliases |
| `grafico` | Gráfico numerado; sequência `gra:` | `identificador`, `titulo`, `fonte` e imagem por `arquivo` ou Markdown | `nota`, `idioma`; dimensões da imagem | Todos; teste dos quatro tipos em `test_referencias.py` |
| `tabela` | Tabela numerada; sequência `tab:` | `identificador`, `titulo`, `fonte` e tabela Markdown | `nota`, `idioma`, `manter_junto="true"` ou `"false"` | Todos; teste de tabela curta e das legendas em `test_referencias.py` |
| `equacao` | Expressão numerada; sequência `eq:` | `identificador` e uma expressão `$$...$$` | `titulo`, `fonte`, `nota`, `idioma` | Todos; `test_matematica_paineis.py` |
| `painel-imagens` | Container sem número, com duas a quatro colunas | Ao menos duas figuras/gráficos identificados como filhos diretos | `colunas="2"`, `"3"` ou `"4"` | Todos; testes de ordem, paginação e alinhamento em `test_matematica_paineis.py` |
| Chamada de objeto | Link para o número calculado, inclusive antes do objeto | `@fig:id`, `@gra:id`, `@tab:id` ou `@eq:id` | Prefixos e sufixos de chamadas | Todos; teste de referências antecipadas e renumeração dos quatro tipos |
| ID estável | Destino único no documento | ID não vazio e válido; prefixo do tipo para objetos numerados | Forma `#id` ou `identificador="id"` | Todos; validação de duplicidade e destino |
| Citação narrativa | Autor-data integrada à frase | Chave bibliográfica cadastrada, como `@jcgm2012` | Localizador conforme a citação | Todos; teste de citações autor-data com links |
| Citação parentética | Autor-data entre parênteses | Chamada como `[@jcgm2012]` | Página ou outro localizador | Todos; mesmo teste e chamadas mistas |
| Bibliografia | Referências citadas geradas por citeproc | Arquivo CSL-YAML/CSL-JSON; cada registro com `id`, `type`, `title` | Campos bibliográficos reais da publicação | Todos; testes de YAML/JSON e duplicidade em `test_referencias.py` |
| Fontes e notas dos objetos | Origem e explicação junto ao objeto | `fonte` nos três tipos visuais | `nota`; Markdown simples e citações nos campos | Todos; teste de títulos/fontes/notas escapados e de chamadas mistas |

IDs não dependem do número impresso: `fig:conjunto` permanece estável depois
de inserir outra figura. Figura/ilustração/desenho compartilham a sequência;
gráficos, tabelas e equações têm sequências próprias. Equações recebem o número
entre parênteses à direita e não uma legenda gráfica automática.

## Identificação e elementos opcionais

| Elemento | Origem dos dados | Obrigatoriedade e condição | Perfis | Evidência de cobertura |
|---|---|---|---|---|
| Identificação comum | `versao_schema`, `tipo_documento`, `titulo`, `autor`, `instituicao`, `unidade_operacional`, `unidade_curricular`, `publico`, `carga_horaria` | Obrigatória, validada antes da geração | Todos | `test_renderizar.py` e validação dos modelos iniciais |
| Autoria | Texto ou lista YAML | Lista não vazia; ordem preservada | Todos | Testes de autoria em texto/lista e três autores |
| Subtítulo | `subtitulo` | Opcional; ausente/vazio não cria linha ou rótulo | Todos | Testes do artigo e do núcleo |
| Idioma | `idioma` | Padrão `pt-BR`; valores suportados `pt-BR`, `en`, `es` | Todos | Schema e testes do núcleo |
| Cidade e data | `local`, `data` | Independentes; nenhuma cidade ou data é inferida | Artigo | Testes condicionais de cidade e data em `test_artigo.py` |
| Capa | Título, autoria e identificação existente | Pré-textual configurável; sem preenchimento inventado | Artigo | Regressão da marca, título, autoria e posições da capa |
| Folha de rosto | Título, autoria, curso/habilitação e natureza do trabalho | Pré-textual configurável; orientação apenas quando fornecida | Artigo | Regressão do artigo e condições dos opcionais |
| Aprovação | Coordenação, banca e/ou data de aprovação informadas | Página somente quando há dados efetivos; sem assinaturas genéricas vazias | Artigo | Testes de aprovação e do núcleo |
| Orientação, coordenação e banca | `orientador`, `coordenacao`, `banca` | Opcionais; rótulos e assinaturas somente com dados | Artigo | Testes de campos opcionais |
| Resumo | `resumo` | Opcional; sem campo não há título de resumo vazio | Artigo | Testes de campos opcionais |
| Palavras-chave | `palavras_chave` | Opcional; lista ausente ou vazia não gera rótulo | Artigo | `test_tex_exibe_palavras_chave_apenas_quando_preenchidas` |
| Contato | `email` | Opcional; quando informado deve ser válido | Artigo | Schema e testes do núcleo |

## Erros e critérios de aceitação

| Situação | Comportamento exigido | Cobertura |
|---|---|---|
| Campo obrigatório ausente, tipo errado ou valor inválido | Interromper com arquivo e campo identificáveis | Schema, `test_renderizar.py`, `test_artigo.py`, testes do núcleo |
| ID duplicado | Interromper indicando o identificador | `test_referencias.py` e testes do núcleo |
| Chamada ou link interno sem destino | Interromper indicando o destino | `test_referencias.py` e testes do núcleo |
| Imagem ou bibliografia ausente | Interromper indicando o arquivo | `test_renderizar.py`, `test_referencias.py` e leitura do AST |
| Citação sem registro bibliográfico | Interromper; não entregar PDF com referência indefinida | Testes de validação e PDF em `test_referencias.py` |
| Elemento visual sem título/fonte obrigatórios | Interromper indicando ID e propriedade | Testes de objetos inválidos |
| Colunas, dimensões ou composição de painel inválidas | Interromper com orientação específica | Testes de painéis inválidos |
| Elementos inseridos ou reorganizados | Recalcular numeração e preservar destinos por ID | Testes de renumeração e links dos quatro tipos |
| Opcionais ausentes ou vazios | Omitir elemento, título, rótulo ou página correspondente | Testes do artigo e do núcleo |
| PDF final | Links resolvidos, numeração coerente, legendas/fontes presentes e sem interrogações de referências não resolvidas | Testes de PDF e conferência visual das demonstrações |
| Pandoc do CI | Mesma semântica com o Pandoc 3.1.3; bibliografia compatível com o writer real | Suíte completa e geração das demonstrações com essa versão |

Uma interrogação legítima no texto não constitui erro. A verificação trata
marcadores de referência não resolvida e destinos inválidos, sem proibir sinais
de pontuação do conteúdo.

## Rastreabilidade dos testes do núcleo

Todos os casos desta tabela estão em
[`tests/test_nucleo.py`](../tests/test_nucleo.py). Os testes anteriores de
artigo, referências e matemática permanecem como cobertura de regressão.

| Contrato coberto | Caso automatizado |
|---|---|
| Os três perfis recebem a mesma representação, sem reinterpretar conteúdo | `test_perfis_consumem_a_mesma_ir_sem_reinterpretar_conteudo` |
| Markdown nativo e catálogo semântico preservados na IR, sem LaTeX gerado na interpretação | `test_ir_preserva_markdown_nativo_e_cobre_catalogo_sem_latex_gerado` |
| Identificador chave-valor e renumeração após reorganizar elementos | `test_identificador_chave_valor_renumera_apos_reordenar` |
| IDs duplicados e conflito entre `#id` e `identificador` | `test_identificadores_duplicados_e_conflitantes_tem_diagnostico` |
| Links internos e chamadas sem destino | `test_destinos_inexistentes_e_chamadas_ausentes_sao_rejeitados` |
| Arquivo ausente em atributo e em imagem Markdown por referência | `test_arquivos_ausentes_cobrem_atributos_e_markdown_por_referencia` |
| Metadados inválidos, diagnóstico do campo e prevenção de saídas parciais | `test_metadados_invalidos_identificam_campo_e_nao_criam_saidas` |
| Cada campo obrigatório, individualmente ausente | `test_todos_os_campos_obrigatorios_tem_mensagem_identificavel` |
| Idioma dos metadados aplicado à apresentação | `test_idioma_dos_metadados_governa_apresentacao` |
| Opcionais vazios omitidos sem mascarar erros nos obrigatórios | `test_opcionais_vazios_sao_omitidos_ao_carregar_sem_ocultar_obrigatorios` |
| Propriedades de elementos inválidas com diagnóstico específico | `test_atributos_invalidos_indicam_o_elemento` |
| Questão com identificador chave-valor e pontuação inteira/decimal, rejeitando valores inválidos | `test_questao_aceita_pontos_inteiros_decimais_e_rejeita_valores_invalidos` |
| Blocos pedagógicos sem conteúdo não geram rótulos vazios | `test_blocos_pedagogicos_vazios_nao_geram_rotulos` |
| PDFs dos três perfis com objetos, tabelas e citações resolvidos | `test_pdf_dos_tres_perfis_resolve_objetos_tabelas_e_citacoes` |
| Artigo sem opcionais não cria aprovação ou rótulos vazios | `test_pdf_artigo_sem_opcionais_nao_cria_aprovacao_nem_rotulos_vazios` |
| Preservação do artigo aprovado como referência | `test_pdf_artigo_aprovado_permanece_como_referencia_de_regressao` |
| Listas vazias não ocultam tipos inválidos nos opcionais | `test_listas_vazias_nao_ocultam_tipos_invalidos_de_metadados` |
| Citação inválida interrompe o lote antes da primeira saída | `test_citacao_invalida_no_lote_impede_saida_parcial_do_primeiro_documento` |
| Link bibliográfico exige obra efetivamente citada e emitida | `test_link_para_referencia_exige_destino_efetivamente_emitido` |
| Caminho de imagem não pode ser um diretório | `test_arquivo_que_aponta_para_diretorio_e_rejeitado` |
| Idioma de elemento igual ao principal não duplica a importação Babel nos três perfis | `test_idioma_do_elemento_nao_reimporta_o_idioma_principal` |

A consolidação acrescentou 21 testes aos 44 casos anteriores: 65 testes no
total, executados também com o Pandoc 3.1.3 do CI. O contrato interno e as
responsabilidades de cada camada estão em [Arquitetura](arquitetura.md).

## Limites explícitos

Esta consolidação não apresenta um novo modelo institucional de relatório:
`templates/Relatorio/Modelo Relatorio.doc` continua como referência para uma
etapa posterior. Glossário, listas automáticas de siglas/símbolos e regras
específicas de anexos/apêndices não integram este catálogo. É possível escrever
seções correspondentes em Markdown comum, sem prometer semântica ou automação
que não foi implementada.

As decisões normativas e estéticas permanecem documentadas em
[critérios editoriais](criterios-editoriais.md). A inclusão de um novo perfil
ou template deve seguir [o contrato de extensão](novo-template.md).
