# Modelos LaTeX SENAI Rondonópolis

[![Licença: CC0 1.0](https://img.shields.io/badge/licen%C3%A7a-CC0%201.0-blue.svg)](LICENSE)
[![Compilar documentos](https://github.com/richarallan/modelos-latex-senai-roo/actions/workflows/compilar-documentos.yml/badge.svg)](https://github.com/richarallan/modelos-latex-senai-roo/actions/workflows/compilar-documentos.yml)
[![Verificação de CI](https://github.com/richarallan/modelos-latex-senai-roo/actions/workflows/verificar-ci.yml/badge.svg)](https://github.com/richarallan/modelos-latex-senai-roo/actions/workflows/verificar-ci.yml)

Modelos abertos para criar apostilas, planos, atividades e outros materiais
educacionais. O MVP separa **conteúdo** de **apresentação**: o texto é escrito
em Markdown, fácil de revisar com qualquer assistente de inteligência
artificial, e o mesmo arquivo gera LaTeX, PDF e DOCX.

> [!IMPORTANT]
> Este é um projeto independente e não constitui publicação oficial do SENAI.
> Marcas, logotipos e manuais de identidade visual não são licenciados por este
> repositório e só devem ser usados por pessoas autorizadas.

## O que o primeiro MVP entrega

- fonte única em Markdown;
- saída editável em `.tex` e `.docx`;
- saída final em `.pdf`;
- blocos pedagógicos para objetivo, atenção e prática;
- compilação local por um único comando;
- compilação automática no GitHub Actions;
- artefatos gerados disponíveis em cada execução do workflow.

## Estrutura

```text
.
├── documentos/                         # conteúdo editável
│   └── apostila-exemplo.md
├── filtros/
│   └── bloco-senai.lua                 # blocos pedagógicos no PDF/DOCX
├── scripts/
│   └── renderizar.py                   # orquestra Pandoc e XeLaTeX
├── templates/
│   └── blocos-senai.tex                # dependências LaTeX dos blocos
├── .github/workflows/
│   └── compilar-documentos.yml         # automação de compilação
├── CREDITS.md
└── LICENSE
```

## Uso rápido

### 1. Instale as dependências

- Python 3.10 ou superior;
- Pandoc 2.17 ou superior;
- XeLaTeX com o pacote `tcolorbox`.

Em Ubuntu ou Debian:

```bash
sudo apt-get update
sudo apt-get install pandoc texlive-xetex texlive-latex-extra
```

### 2. Edite ou crie um documento

Duplique `documentos/apostila-exemplo.md`, altere os metadados do cabeçalho e
escreva o conteúdo. Um bloco pedagógico usa esta sintaxe:

```markdown
::: objetivo
Identificar os principais elementos de uma máquina.
:::
```

As classes disponíveis no MVP são `objetivo`, `atencao` e `pratica`.

### 3. Gere os arquivos

```bash
python scripts/renderizar.py --formato todos
```

Os resultados serão gravados em `dist/`. Para gerar apenas um formato:

```bash
python scripts/renderizar.py --formato tex
python scripts/renderizar.py --formato pdf
python scripts/renderizar.py --formato docx
```

Também é possível compilar somente arquivos específicos:

```bash
python scripts/renderizar.py documentos/apostila-exemplo.md --formato todos
```

## Uso com inteligência artificial

Para reduzir alterações acidentais na automação, peça à IA para trabalhar
principalmente nos arquivos de `documentos/`. Um comando inicial possível é:

> Revise `documentos/apostila-exemplo.md`, preserve o cabeçalho YAML e a
> sintaxe dos blocos pedagógicos e adapte o conteúdo para a unidade curricular
> informada. Não altere os arquivos de automação.

O conteúdo permanece legível e versionável mesmo sem uma ferramenta de IA.

## Verificação contínua

O workflow `verificar-ci.yml` executa automaticamente em todo pull request e
em alterações na branch `main`. Ele verifica:

- sintaxe dos scripts Python;
- testes unitários do orquestrador de renderização;
- estrutura mínima dos documentos de exemplo;
- sintaxe dos workflows YAML.

Para executar as mesmas verificações localmente:

```bash
python -m pip install -r requirements-dev.txt
python -m compileall -q scripts tests
python -m unittest discover -s tests -p "test_*.py" -v
```

## Compilação no GitHub

O workflow `compilar-documentos.yml` é executado em pull requests, alterações
relevantes na branch `main` e acionamento manual. Ao final, a execução publica
um artefato chamado `documentos-gerados` contendo LaTeX, PDF e DOCX.

## Créditos e licença

O projeto reconhece como referência o trabalho de Emerson Mello, do Instituto
Federal de Santa Catarina. Consulte [CREDITS.md](CREDITS.md) para os créditos e
o histórico da adaptação.

O conteúdo próprio deste repositório é disponibilizado sob a dedicação ao
domínio público [CC0 1.0 Universal](LICENSE), sem afetar direitos de terceiros,
marcas ou materiais incorporados futuramente sob outras licenças.
