-- Objetos identificados e chamadas estáveis, sem números escritos no Markdown.
-- Executar antes de blocos-senai.lua e de --citeproc.
--
-- ::: {.figura #fig:motor titulo="Conjunto motor-bomba" fonte="Elaboração própria."}
-- ![Esquema do conjunto](imagens/motor-bomba.png){width=80%}
-- :::
-- A chamada @fig:motor acompanha a posição do objeto, inclusive antes dele.

local tipos = {
  figura = {prefixo = "fig:", nome = "Figura"},
  grafico = {prefixo = "gra:", nome = "Gráfico"},
  tabela = {prefixo = "tab:", nome = "Tabela"},
  equacao = {prefixo = "eq:", nome = "Equação"},
}

local objetos = {}
local contadores = {}

local function falhar(mensagem)
  error("Referências cruzadas: " .. mensagem, 0)
end

local function texto_preenchido(texto)
  return texto ~= nil and texto:match("%S") ~= nil
end

local function tipo_do_objeto(div)
  local encontrado
  for _, classe in ipairs(div.classes) do
    if tipos[classe] then
      if encontrado then
        falhar("o bloco " .. div.identifier .. " deve ter apenas um tipo de objeto")
      end
      encontrado = classe
    end
  end
  return encontrado
end

local function prefixo_reservado(id)
  for _, config in pairs(tipos) do
    if id:sub(1, #config.prefixo) == config.prefixo then
      return true
    end
  end
  return false
end

local function validar_identificadores(doc)
  local encontrados = {}
  local function registrar(elemento)
    local id = elemento.identifier
    if id and id ~= "" then
      if encontrados[id] then
        falhar("identificador duplicado: " .. id)
      end
      encontrados[id] = true
    end
  end
  local filtro = {
    Div = registrar, Header = registrar, Span = registrar,
    Image = registrar, Table = registrar, Code = registrar,
    CodeBlock = registrar, Link = registrar,
  }
  if PANDOC_VERSION[1] >= 3 then
    filtro.Figure = registrar
  end
  doc:walk(filtro)
end

local function sem_figuras_implicitas(blocos)
  local doc = pandoc.Pandoc(blocos)
  -- Pandoc 3 representa imagens com legenda como Figure; 2.17 usa Image.
  if PANDOC_VERSION[1] >= 3 then
    doc = doc:walk({Figure = function(figura) return figura.content end})
  end
  doc = doc:walk({Image = function(imagem)
    imagem.title = "" -- remove o marcador fig: usado pelo writer antigo
    return imagem
  end})
  return doc.blocks
end

local function conteudo_visual(div, tipo)
  local blocos = sem_figuras_implicitas(div.content)
  if #blocos ~= 1 then
    falhar(div.identifier .. ": informe exatamente um elemento no bloco " .. tipo)
  end
  local bloco = blocos[1]
  if tipo == "figura" or tipo == "grafico" then
    if (bloco.t ~= "Para" and bloco.t ~= "Plain") or #bloco.content ~= 1
      or bloco.content[1].t ~= "Image" then
      falhar(div.identifier .. ": o bloco " .. tipo .. " deve conter uma imagem Markdown")
    end
    return blocos, bloco.content[1]
  elseif tipo == "tabela" then
    if bloco.t ~= "Table" then
      falhar(div.identifier .. ": o bloco tabela deve conter uma tabela Markdown")
    end
    if pandoc.utils.stringify(bloco.caption) ~= "" then
      falhar(div.identifier .. ": informe a legenda da tabela no atributo titulo")
    end
    return blocos
  else
    if (bloco.t ~= "Para" and bloco.t ~= "Plain") or #bloco.content ~= 1
      or bloco.content[1].t ~= "Math" or bloco.content[1].mathtype ~= "DisplayMath" then
      falhar(div.identifier .. ": o bloco equacao deve conter uma única equação entre $$")
    end
    return blocos, bloco.content[1]
  end
end

local function enumerar(div)
  local tipo = tipo_do_objeto(div)
  if not tipo then return end
  local config = tipos[tipo]
  local id = div.identifier
  if id:sub(1, #config.prefixo) ~= config.prefixo
    or not id:match("^[A-Za-z0-9][A-Za-z0-9:_.%-]*$")
    or #id == #config.prefixo then
    falhar("identificador inválido para " .. tipo .. ": " .. id .. "; use " .. config.prefixo .. "nome-estavel")
  end
  if tipo ~= "equacao" then
    for _, atributo in ipairs({"titulo", "fonte"}) do
      if not texto_preenchido(div.attributes[atributo]) then
        falhar(id .. ": atributo obrigatório ausente ou vazio: " .. atributo)
      end
    end
  end
  if tipo == "tabela" and div.attributes.manter_junto
    and div.attributes.manter_junto ~= "true" and div.attributes.manter_junto ~= "false" then
    falhar(id .. ": manter_junto deve ser true ou false")
  end
  pandoc.Pandoc(div.content):walk({Div = function(interno)
    if tipo_do_objeto(interno) then
      falhar(id .. ": objetos numerados não podem ser aninhados")
    end
  end})
  conteudo_visual(div, tipo)
  contadores[tipo] = (contadores[tipo] or 0) + 1
  objetos[id] = {tipo = tipo, numero = contadores[tipo], nome = config.nome}
end

local function anexar(destino, origem)
  for _, item in ipairs(origem) do destino:insert(item) end
end

local function resolver_citacao(citacao)
  local tem_objeto = false
  for _, item in ipairs(citacao.citations) do
    if prefixo_reservado(item.id) then tem_objeto = true end
  end
  if not tem_objeto then return nil end

  local saida = pandoc.Inlines({})
  local grupo_bibliografico = {}
  local function separar()
    if #saida > 0 then
      saida:insert(pandoc.Str(";"))
      saida:insert(pandoc.Space())
    end
  end
  local function bibliografia_pendente()
    if #grupo_bibliografico > 0 then
      separar()
      saida:insert(pandoc.Cite({}, grupo_bibliografico))
      grupo_bibliografico = {}
    end
  end

  for _, item in ipairs(citacao.citations) do
    if prefixo_reservado(item.id) then
      bibliografia_pendente()
      local objeto = objetos[item.id]
      if not objeto then falhar("referência não resolvida: " .. item.id) end
      separar()
      if #item.prefix > 0 then
        anexar(saida, item.prefix)
        saida:insert(pandoc.Space())
      end
      local numero = tostring(objeto.numero)
      if objeto.tipo == "equacao" then numero = "(" .. numero .. ")" end
      saida:insert(pandoc.Link({pandoc.Str(objeto.nome .. " " .. numero)}, "#" .. item.id))
      anexar(saida, item.suffix)
    else
      table.insert(grupo_bibliografico, item)
    end
  end
  bibliografia_pendente()
  return saida
end

local function paragrafo(texto, negrito)
  -- Mantém Cite/Link no AST até --citeproc, inclusive em fonte e nota.
  -- A escrita LaTeX do Pandoc faz o escape dos demais caracteres.
  local doc = pandoc.read(texto, "markdown+citations-raw_tex-raw_html")
  local conteudo = pandoc.Inlines({})
  for _, bloco in ipairs(doc.blocks) do
    if bloco.t ~= "Para" and bloco.t ~= "Plain" then
      falhar("título, fonte e nota devem conter somente texto Markdown em parágrafo")
    end
    if #conteudo > 0 then conteudo:insert(pandoc.Space()) end
    anexar(conteudo, bloco.content)
  end
  if negrito then conteudo = {pandoc.Strong(conteudo)} end
  return pandoc.Para(conteudo)
end

local function largura_da_imagem(imagem)
  local largura = imagem.attributes.width or ""
  local percentual = largura:match("^([%d.]+)%%$")
  if percentual and tonumber(percentual) and tonumber(percentual) > 0 and tonumber(percentual) <= 100 then
    imagem.attributes.width = "100%"
    return string.format("%.6f\\linewidth", tonumber(percentual) / 100)
  end
  local valor, unidade = largura:match("^([%d.]+)(cm)$")
  if not valor then valor, unidade = largura:match("^([%d.]+)(mm)$") end
  if not valor then valor, unidade = largura:match("^([%d.]+)(in)$") end
  if valor and tonumber(valor) and tonumber(valor) > 0 then
    imagem.attributes.width = "100%"
    return valor .. unidade
  end
  return "\\linewidth"
end

local function rodape_guardado_no_longtable(blocos)
  -- Inspeciona somente a convenção do writer. As células continuam no AST
  -- original para que citações sejam processadas posteriormente pelo citeproc.
  local latex = pandoc.write(pandoc.Pandoc(blocos), "latex")
  local regra = latex:find("\\bottomrule", 1, true)
  local fim_rodape = latex:find("\\endlastfoot", 1, true)
  return regra and fim_rodape and regra < fim_rodape
end

local function renderizar(div)
  local objeto = objetos[div.identifier]
  if not objeto or not tipo_do_objeto(div) then return nil end
  local blocos, elemento = conteudo_visual(div, objeto.tipo)
  local latex = FORMAT:match("latex") ~= nil
  local saida = pandoc.Blocks({})
  local imagem = objeto.tipo == "figura" or objeto.tipo == "grafico"
  local manter_junto = imagem or (objeto.tipo == "tabela" and div.attributes.manter_junto == "true")
  if latex then
    if manter_junto then
      local largura = imagem and largura_da_imagem(elemento) or "\\linewidth"
      saida:insert(pandoc.RawBlock("latex", "\\begin{center}\n\\begin{minipage}{" .. largura .. "}\n\\setlength{\\parindent}{0pt}"))
    else
      saida:insert(pandoc.RawBlock("latex", "\\begingroup\n\\setlength{\\parindent}{0pt}"))
    end
    if objeto.tipo == "tabela" then
      saida:insert(pandoc.RawBlock("latex", "\\setlength{\\LTleft}{0pt}\n\\setlength{\\LTright}{\\fill}"))
      if manter_junto and rodape_guardado_no_longtable(blocos) then
        -- O footer de longtable não é expedido dentro de uma minipage. No
        -- writer que o utiliza, traz apenas a regra final para o corpo visível.
        -- No Pandoc 2.17 a regra já pertence ao corpo e nada é alterado.
        saida:insert(pandoc.RawBlock("latex", "\\let\\senaiFimTabelaCurta\\endlongtable\n\\def\\endlongtable{\\bottomrule\\senaiFimTabelaCurta}"))
      end
    end
  end
  if texto_preenchido(div.attributes.titulo) then
    if latex then saida:insert(pandoc.RawBlock("latex", "{\\fontsize{10}{12}\\selectfont\\raggedright")) end
    local legenda = paragrafo(objeto.nome .. " " .. objeto.numero .. " — " .. div.attributes.titulo, true)
    if latex and objeto.tipo ~= "equacao" then
      -- A âncora viaja com a legenda, inclusive quando a caixa muda de página.
      legenda.content:insert(1, pandoc.RawInline("latex", "\\leavevmode\\phantomsection\\hypertarget{" .. div.identifier .. "}{}\\label{" .. div.identifier .. "}"))
    end
    saida:insert(legenda)
    if latex then saida:insert(pandoc.RawBlock("latex", "\\par}\n\\nopagebreak[4]")) end
  end
  if latex and imagem then saida:insert(pandoc.RawBlock("latex", "\\centering")) end
  if latex and objeto.tipo == "equacao" then
    -- $$ em linhas próprias introduz quebras nas extremidades de Math.text.
    -- Linhas vazias são parágrafos inválidos dentro do ambiente equation.
    local linhas = {}
    for linha in (elemento.text .. "\n"):gmatch("([^\n]*)\n") do
      if linha:match("%S") then table.insert(linhas, linha) end
    end
    saida:insert(pandoc.RawBlock("latex", "\\begin{equation}\n\\hypertarget{" .. div.identifier .. "}{}\\label{" .. div.identifier .. "}\n" .. table.concat(linhas, "\n")
      .. "\n\\tag{" .. objeto.numero .. "}\n\\end{equation}"))
  else
    anexar(saida, blocos)
  end
  if texto_preenchido(div.attributes.fonte) or texto_preenchido(div.attributes.nota) then
    if latex then saida:insert(pandoc.RawBlock("latex", "{\\fontsize{10}{12}\\selectfont\\raggedright")) end
    if texto_preenchido(div.attributes.fonte) then
      saida:insert(paragrafo("Fonte: " .. div.attributes.fonte))
    end
    if texto_preenchido(div.attributes.nota) then
      saida:insert(paragrafo("Nota: " .. div.attributes.nota))
    end
    if latex then saida:insert(pandoc.RawBlock("latex", "\\par}")) end
  end
  if latex then
    if manter_junto then
      saida:insert(pandoc.RawBlock("latex", "\\end{minipage}\n\\end{center}"))
    else
      saida:insert(pandoc.RawBlock("latex", "\\endgroup"))
    end
  end
  -- O writer pode posicionar a âncora de um Div antes de uma caixa que quebra
  -- para a página seguinte. Em LaTeX, usamos apenas as âncoras locais acima.
  return pandoc.Div(saida, pandoc.Attr(latex and "" or div.identifier))
end

function Pandoc(doc)
  -- O writer 2.17 usa parágrafos bibliográficos; 3.x usa itens de lista.
  doc.meta["senai-csl-legado"] = pandoc.MetaBool(PANDOC_VERSION[1] < 3)
  objetos, contadores = {}, {}
  validar_identificadores(doc)
  doc:walk({Div = enumerar})
  doc = doc:walk({Cite = resolver_citacao})
  doc = doc:walk({Div = renderizar})
  -- As legendas podem introduzir chamadas escritas nos atributos Markdown.
  return doc:walk({Cite = resolver_citacao, Link = function(link)
    local id = link.target:match("^#(.+)$")
    if id and prefixo_reservado(id) and not objetos[id] then
      falhar("referência não resolvida: " .. id)
    end
  end})
end
