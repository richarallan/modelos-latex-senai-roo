-- Converte Divs do Markdown em blocos pedagógicos.
--
-- Sintaxe de entrada:
--   ::: objetivo
--   Texto do bloco.
--   :::
--
-- Formatos LaTeX/PDF recebem caixas tcolorbox; DOCX recebe um título em
-- negrito seguido pelo conteúdo. Formatos não reconhecidos preservam a Div.

local blocos = {
  objetivo = {
    titulo = "Objetivo de aprendizagem",
    cor_fundo = "blue!4",
    cor_borda = "blue!55!black",
  },
  atencao = {
    titulo = "Atenção",
    cor_fundo = "red!4",
    cor_borda = "red!65!black",
  },
  pratica = {
    titulo = "Atividade prática",
    cor_fundo = "green!4",
    cor_borda = "green!45!black",
  },
}

local function primeiro_bloco_conhecido(classes)
  for _, classe in ipairs(classes) do
    if blocos[classe] then
      return blocos[classe]
    end
  end
  return nil
end

local function para_latex(div, configuracao)
  local inicio = string.format(
    "\\begin{tcolorbox}[enhanced,breakable,title={%s}," ..
      "colback=%s,colframe=%s,fonttitle=\\bfseries]",
    configuracao.titulo,
    configuracao.cor_fundo,
    configuracao.cor_borda
  )

  local saida = { pandoc.RawBlock("latex", inicio) }
  for _, bloco in ipairs(div.content) do
    table.insert(saida, bloco)
  end
  table.insert(saida, pandoc.RawBlock("latex", "\\end{tcolorbox}"))
  return saida
end

local function para_docx(div, configuracao)
  local titulo = pandoc.Para({
    pandoc.Strong({ pandoc.Str(configuracao.titulo) }),
  })
  local saida = { titulo }
  for _, bloco in ipairs(div.content) do
    table.insert(saida, bloco)
  end
  return saida
end

function Div(div)
  local configuracao = primeiro_bloco_conhecido(div.classes)
  if not configuracao then
    return nil
  end

  if FORMAT:match("latex") then
    return para_latex(div, configuracao)
  end

  if FORMAT:match("docx") then
    return para_docx(div, configuracao)
  end

  return nil
end
