-- Interpreta blocos semânticos do documento canônico.
--
-- Exemplo:
--   ::: {.questao #q1 pontos=2 tipo=calculo}
--   Calcule a rotação de trabalho.
--   :::

local blocos = {
  objetivo = {
    ambiente = "senaiobjetivo",
    titulo = "Objetivo de aprendizagem",
    estilo_docx = "Objetivo SENAI",
  },
  situacao_problema = {
    ambiente = "senaisituacao",
    titulo = "Situação-problema",
    estilo_docx = "Situacao-problema SENAI",
  },
  questao = {
    ambiente = "senaiquestao",
    titulo = "Questão",
    estilo_docx = "Questao SENAI",
  },
  seguranca = {
    ambiente = "senaiseguranca",
    titulo = "Segurança",
    estilo_docx = "Seguranca SENAI",
  },
  rubrica = {
    ambiente = "senairubrica",
    titulo = "Critério de avaliação",
    estilo_docx = "Rubrica SENAI",
  },
  pratica = {
    ambiente = "senaipratica",
    titulo = "Atividade prática",
    estilo_docx = "Pratica SENAI",
  },
  atencao = {
    ambiente = "senaiatencao",
    titulo = "Atenção",
    estilo_docx = "Atencao SENAI",
  },
}

local function escapar_latex(texto)
  return texto:gsub("([%%#&{}_])", "\\%1")
end

local function localizar_configuracao(classes)
  for _, classe in ipairs(classes) do
    if blocos[classe] then
      return classe, blocos[classe]
    end
  end
  return nil, nil
end

local function titulo_questao(div, configuracao)
  local partes = {}
  if div.identifier and div.identifier ~= "" then
    table.insert(partes, div.identifier)
  end
  if div.attributes.pontos then
    table.insert(partes, div.attributes.pontos .. " ponto(s)")
  end
  if div.attributes.tipo then
    table.insert(partes, div.attributes.tipo)
  end
  if #partes == 0 then
    return configuracao.titulo
  end
  return configuracao.titulo .. " — " .. table.concat(partes, " · ")
end

local function para_latex(div, classe, configuracao)
  local inicio
  if classe == "questao" then
    local complemento = titulo_questao(div, configuracao):gsub("^Questão%s*—?%s*", "")
    inicio = "\\begin{" .. configuracao.ambiente .. "}[" .. escapar_latex(complemento) .. "]"
  else
    inicio = "\\begin{" .. configuracao.ambiente .. "}"
  end

  local saida = { pandoc.RawBlock("latex", inicio) }
  for _, bloco in ipairs(div.content) do
    table.insert(saida, bloco)
  end
  table.insert(saida, pandoc.RawBlock("latex", "\\end{" .. configuracao.ambiente .. "}"))
  return saida
end

local function para_docx(div, classe, configuracao)
  local titulo = configuracao.titulo
  if classe == "questao" then
    titulo = titulo_questao(div, configuracao)
  end

  table.insert(div.content, 1, pandoc.Para({
    pandoc.Strong({ pandoc.Str(titulo) }),
  }))
  div.attributes["custom-style"] = configuracao.estilo_docx
  return div
end

function Div(div)
  local classe, configuracao = localizar_configuracao(div.classes)
  if not configuracao then
    return nil
  end

  if FORMAT:match("latex") then
    return para_latex(div, classe, configuracao)
  end

  if FORMAT:match("docx") then
    return para_docx(div, classe, configuracao)
  end

  return nil
end
