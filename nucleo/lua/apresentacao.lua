-- Apresentação da IR comum. Não valida, enumera ou interpreta Markdown.
local M = {}
local base_filtro = (PANDOC_SCRIPT_FILE:match("^(.*[/\\])") or "")
local pedagogicos = dofile(base_filtro .. "../nucleo/lua/catalogo.lua")
local function falhar(mensagem) error("Apresentação: " .. mensagem, 0) end
local function anexar(destino, origem)
  for _, item in ipairs(origem) do destino:insert(item) end
end
local function parte(div, classe)
  for _, bloco in ipairs(div.content) do
    if bloco.t == "Div" and bloco.classes:includes(classe) then return bloco.content end
  end
  return pandoc.Blocks({})
end
local function paragrafo_de_parte(div, classe, prefixo, negrito)
  local blocos = parte(div, classe)
  if #blocos == 0 then return nil end
  local inlines = pandoc.Inlines({})
  if prefixo then
    inlines:insert(pandoc.Str(prefixo))
    inlines:insert(pandoc.Space())
  end
  for _, bloco in ipairs(blocos) do
    if #inlines > 0 and not prefixo then inlines:insert(pandoc.Space()) end
    anexar(inlines, bloco.content)
  end
  if negrito then inlines = pandoc.Inlines({pandoc.Strong(inlines)}) end
  return pandoc.Para(inlines)
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

local function renderizar_painel(div)
  local painel = {colunas = tonumber(div.attributes["senai-painel-colunas"])}
  if not FORMAT:match("latex") then
    div.attributes["senai-painel-colunas"] = nil
    return div
  end
  local saida = pandoc.Blocks({})
  local largura = (1 - 0.03 * (painel.colunas - 1)) / painel.colunas
  local inicio = string.format("\\begin{minipage}[t]{%.6f\\linewidth}\\vspace{0pt}", largura)
  for indice, filho in ipairs(div.content) do
    if (indice - 1) % painel.colunas == 0 then
      if indice > 1 then saida:insert(pandoc.RawBlock("latex", "\\vspace{0.8em}")) end
      saida:insert(pandoc.RawBlock("latex", "\\noindent" .. inicio))
    end
    -- A transformação dos filhos já ocorreu, mas suas citações ainda são AST.
    anexar(saida, filho.content)
    if indice % painel.colunas == 0 or indice == #div.content then
      saida:insert(pandoc.RawBlock("latex", "\\end{minipage}\\par"))
    else
      -- A ponte é um único RawBlock: uma linha vazia separaria as células.
      saida:insert(pandoc.RawBlock("latex", "\\end{minipage}\\hspace{0.03\\linewidth}%\n" .. inicio))
    end
  end
  return pandoc.Div(saida, pandoc.Attr(div.identifier))
end

local function tem_alinhamento_externo(texto)
  -- Detecta separadores fora de ambientes e argumentos internos. Isto não
  -- expande macros TeX; apenas distingue a composição externa de cases,
  -- matrizes, substack e de um aligned já fornecido pelo autor.
  local ambientes, grupos, posicao = 0, 0, 1
  local function pular_espacos_e_comentarios(inicio)
    while inicio <= #texto do
      local caractere = texto:sub(inicio, inicio)
      if caractere:match("%s") then
        inicio = inicio + 1
      elseif caractere == "%" then
        inicio = texto:find("\n", inicio, true) or (#texto + 1)
      else
        break
      end
    end
    return inicio
  end
  while posicao <= #texto do
    local caractere = texto:sub(posicao, posicao)
    if caractere == "%" then
      posicao = texto:find("\n", posicao, true) or (#texto + 1)
    elseif caractere == "\\" then
      local seguinte = texto:sub(posicao + 1, posicao + 1)
      if seguinte == "\\" then
        if ambientes == 0 and grupos == 0 then return true end
        posicao = posicao + 2
      else
        local inicio, fim, comando = texto:find("\\([A-Za-z@]+)", posicao)
        if inicio == posicao then
          local argumento = pular_espacos_e_comentarios(fim + 1)
          local fechamento = texto:sub(argumento, argumento) == "{"
            and texto:find("}", argumento + 1, true)
          if (comando == "begin" or comando == "end") and fechamento then
            ambientes = math.max(0, ambientes + (comando == "begin" and 1 or -1))
            posicao = fechamento + 1
          else
            posicao = fim + 1
          end
        else
          -- Controles de um caractere, como \&, \%, \{ e \}, são literais.
          posicao = posicao + 2
        end
      end
    else
      if caractere == "{" then
        grupos = grupos + 1
      elseif caractere == "}" then
        grupos = math.max(0, grupos - 1)
      elseif caractere == "&" and ambientes == 0 and grupos == 0 then
        return true
      end
      posicao = posicao + 1
    end
  end
  return false
end

local function texto_da_equacao(elemento)
  -- Em $$ com linhas próprias, linhas vazias não são parágrafos matemáticos.
  local linhas = {}
  for linha in (elemento.text .. "\n"):gmatch("([^\n]*)\n") do
    if linha:match("%S") then table.insert(linhas, linha) end
  end
  local texto = table.concat(linhas, "\n")
  -- Ambientes internos não suprimem o alinhamento exigido no nível externo.
  if tem_alinhamento_externo(texto) then
    texto = "\\begin{aligned}\n" .. texto .. "\n\\end{aligned}"
  end
  return texto
end

local function renderizar(div)
  if div.attributes["senai-painel-colunas"] then return renderizar_painel(div) end
  local tipo = div.attributes["senai-tipo"]
  if not tipo then return nil end
  local objeto = {tipo = tipo, numero = div.attributes["senai-numero"], nome = div.attributes["senai-nome"]}
  local blocos = parte(div, "senai-conteudo")
  local elemento = (tipo == "figura" or tipo == "grafico" or tipo == "equacao") and blocos[1].content[1] or nil
  local latex = FORMAT:match("latex") ~= nil
  local saida = pandoc.Blocks({})
  local imagem = objeto.tipo == "figura" or objeto.tipo == "grafico"
  local em_painel = div.attributes["senai-em-painel"] == "true"
  local manter_junto = (imagem and not em_painel)
    or objeto.tipo == "equacao"
    or (objeto.tipo == "tabela" and div.attributes.manter_junto == "true")
  if latex then
    if manter_junto then
      local largura = imagem and largura_da_imagem(elemento) or "\\linewidth"
      saida:insert(pandoc.RawBlock("latex", "\\begin{center}\n\\begin{minipage}{" .. largura .. "}\n\\setlength{\\parindent}{0pt}"))
      if objeto.tipo == "equacao" then
        -- Mantém a tinta do número dentro da margem, inclusive no XeTeX 2023.
        saida:insert(pandoc.RawBlock("latex", "\\microtypesetup{protrusion=false}"))
      end
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
  if #parte(div, "senai-titulo") > 0 then
    if objeto.tipo == "equacao" then
      -- A descrição legada é prosa, não uma legenda gráfica numerada.
      saida:insert(paragrafo_de_parte(div, "senai-titulo"))
      if latex then saida:insert(pandoc.RawBlock("latex", "\\nopagebreak[4]")) end
    else
      local alinhamento = imagem and not em_painel and "\\centering" or "\\raggedright"
      if latex then saida:insert(pandoc.RawBlock("latex", "{\\fontsize{10}{12}\\selectfont" .. alinhamento)) end
      local legenda = paragrafo_de_parte(div, "senai-titulo", objeto.nome .. " " .. objeto.numero .. " —", true)
      if latex then
        -- A âncora viaja com a legenda, inclusive quando a caixa muda de página.
        legenda.content:insert(1, pandoc.RawInline("latex", "\\leavevmode\\phantomsection\\hypertarget{" .. div.identifier .. "}{}\\label{" .. div.identifier .. "}"))
      end
      saida:insert(legenda)
      if latex then saida:insert(pandoc.RawBlock("latex", "\\par}\n\\nopagebreak[4]")) end
    end
  end
  if latex and imagem then
    saida:insert(pandoc.RawBlock("latex", em_painel and "\\raggedright" or "\\centering"))
  end
  if latex and objeto.tipo == "equacao" then
    saida:insert(pandoc.RawBlock("latex", "\\begin{equation}\n\\hypertarget{" .. div.identifier .. "}{}\\label{" .. div.identifier .. "}\n" .. texto_da_equacao(elemento)
      .. "\n\\tag{" .. objeto.numero .. "}\n\\end{equation}"))
  else
    anexar(saida, blocos)
    if objeto.tipo == "equacao" then
      saida:insert(pandoc.Para({pandoc.Str("(" .. objeto.numero .. ")")}))
    end
  end
  if #parte(div, "senai-fonte") > 0 or #parte(div, "senai-nota") > 0 then
    if latex then saida:insert(pandoc.RawBlock("latex", "{\\fontsize{10}{12}\\selectfont\\raggedright")) end
    if #parte(div, "senai-fonte") > 0 then
      saida:insert(paragrafo_de_parte(div, "senai-fonte", "Fonte:"))
    end
    if #parte(div, "senai-nota") > 0 then
      saida:insert(paragrafo_de_parte(div, "senai-nota", "Nota:"))
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
  return pandoc.Div(saida, pandoc.Attr(latex and "" or div.identifier, {}, {lang = div.attributes.lang}))
end

local function bibliografia_em_paragrafos()
  -- A transição para bibitem ocorreu dentro da série 3.1. Detectamos a
  -- convenção do writer, sem presumir que todas as versões 3.x sejam iguais.
  local entrada = pandoc.Div({pandoc.Para({pandoc.Str("Referência de prova")})},
    pandoc.Attr("ref-senai-probe", {"csl-entry"}))
  local referencias = pandoc.Div({entrada},
    pandoc.Attr("refs", {"references", "csl-bib-body"}))
  local latex = pandoc.write(pandoc.Pandoc({referencias}), "latex")
  return not latex:find("\\bibitem", 1, true)
end

local function escapar_latex(texto)
  return texto:gsub("([%%#&{}_])", "\\%1")
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


local function renderizar_pedagogico(div)
  local classe = div.attributes["senai-pedagogico"]
  if not classe then return nil end
  local configuracao = pedagogicos[classe]
  if FORMAT:match("latex") then
    local blocos = para_latex(div, classe, configuracao)
    if div.identifier ~= "" then
      -- A âncora entra na caixa e acompanha sua paginação.
      blocos[1].text = blocos[1].text .. "\n\\phantomsection\\hypertarget{" .. div.identifier .. "}{}\\label{" .. div.identifier .. "}"
    end
    return pandoc.Div(blocos, pandoc.Attr("", {}, {lang = div.attributes.lang}))
  end
  return para_docx(div, classe, configuracao)
end

function M.apresentar(doc, opcoes)
  opcoes = opcoes or {objetos = true, pedagogicos = true}
  -- O writer 3.1.3 inclui lang também em babel-otherlangs. Reimportar o
  -- idioma principal redefine comandos de data no Babel do TeX Live 2023.
  -- A IR preserva idioma; só a apresentação elimina essa marca redundante.
  local principal = pandoc.utils.stringify(doc.meta.lang or doc.meta.idioma or "pt-BR"):lower()
  local function idioma_local(elemento)
    if elemento.attributes and elemento.attributes.lang
      and elemento.attributes.lang:lower() == principal then
      elemento.attributes.lang = nil
      return elemento
    end
  end
  local idiomas = {
    Div = idioma_local, Span = idioma_local, Header = idioma_local,
    Image = idioma_local, Link = idioma_local, Table = idioma_local,
    Code = idioma_local, CodeBlock = idioma_local,
  }
  if PANDOC_VERSION[1] >= 3 then idiomas.Figure = idioma_local end
  doc = doc:walk(idiomas)
  if FORMAT:match("latex") then
    doc.meta["senai-csl-legado"] = pandoc.MetaBool(bibliografia_em_paragrafos())
  end
  if opcoes.objetos then doc = doc:walk({Div = renderizar}) end
  if opcoes.pedagogicos then doc = doc:walk({Div = renderizar_pedagogico}) end
  return doc
end
return M
