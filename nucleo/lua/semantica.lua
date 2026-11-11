-- Interpretação comum: Markdown/Pandoc AST -> representação semântica.
local tipos = {
  figura = {prefixo = "fig:", nome = "Figura"},
  grafico = {prefixo = "gra:", nome = "Gráfico"},
  tabela = {prefixo = "tab:", nome = "Tabela"},
  equacao = {prefixo = "eq:", nome = "Equação"},
}

local aliases = {ilustracao = "figura", desenho = "figura"}

local M = {}
local objetos = {}
local contadores = {}
local paineis = {}
local membros_painel = {}
local diretorio_fonte = "."
local base_filtro = (PANDOC_SCRIPT_FILE:match("^(.*[/\\])") or "")
local pedagogicos = dofile(base_filtro .. "../nucleo/lua/catalogo.lua")

local function falhar(mensagem)
  error("Referências cruzadas: " .. mensagem, 0)
end

local function texto_preenchido(texto)
  return texto ~= nil and texto:match("%S") ~= nil
end

local function tipo_do_objeto(div)
  local encontrado
  for _, classe in ipairs(div.classes) do
    local tipo = aliases[classe] or (tipos[classe] and classe)
    if tipo then
      if encontrado and encontrado ~= tipo then
        falhar("o bloco " .. div.identifier .. " deve ter apenas um tipo de objeto")
      end
      encontrado = tipo
    end
  end
  return encontrado
end

local function eh_painel(div)
  for _, classe in ipairs(div.classes) do
    if classe == "painel-imagens" then return true end
  end
  return false
end

local function anotar_painel(div)
  if not eh_painel(div) then return nil end
  if tipo_do_objeto(div) then
    falhar("painel-imagens não pode ser um objeto numerado")
  end
  local valor = div.attributes.colunas or "2"
  if not valor:match("^[234]$") then
    falhar("painel-imagens: colunas deve ser um inteiro de 2 a 4")
  end
  if #div.content < 2 then
    falhar("painel-imagens deve conter ao menos duas imagens identificadas")
  end
  pandoc.Pandoc(div.content):walk({Div = function(interno)
    if eh_painel(interno) then falhar("painéis de imagens não podem ser aninhados") end
  end})
  local indice = #paineis + 1
  -- Os IDs dos filhos preservam o contexto mesmo depois de renderizar os Divs.
  for _, filho in ipairs(div.content) do
    local tipo = filho.t == "Div" and tipo_do_objeto(filho)
    if tipo ~= "figura" and tipo ~= "grafico" then
      falhar("painel-imagens aceita apenas filhos diretos figura, gráfico, ilustração ou desenho")
    end
    membros_painel[filho.identifier] = indice
  end
  paineis[indice] = {colunas = tonumber(valor)}
  div.attributes["senai-painel-colunas"] = tostring(valor)
  return div
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
  return encontrados
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
  local _, elemento = conteudo_visual(div, tipo)
  if elemento and (tipo == "figura" or tipo == "grafico") then
    elemento.attributes["senai-contexto"] = id
    -- A imagem passa a ser conteúdo visual comum no contrato canônico.
    div.content = sem_figuras_implicitas(div.content)
    div.content[1].content[1] = elemento
  end
  if membros_painel[id] and elemento then
    local largura = elemento.attributes.width
    if largura then
      local numero = largura:match("^([%d.]+)%%$")
      if not numero or not tonumber(numero) or tonumber(numero) <= 0 or tonumber(numero) > 100 then
        falhar(id .. ": no painel, width deve ser um percentual maior que 0 e até 100% da célula")
      end
    end
  end
  contadores[tipo] = (contadores[tipo] or 0) + 1
  objetos[id] = {tipo = tipo, numero = contadores[tipo], nome = config.nome}
  div.attributes["senai-tipo"] = tipo
  div.attributes["senai-numero"] = tostring(contadores[tipo])
  div.attributes["senai-nome"] = config.nome
  if membros_painel[id] then div.attributes["senai-em-painel"] = "true" end
  return div
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


local function idioma_valido(valor)
  local partes = {}
  for parte in valor:gmatch("[^%-]+") do table.insert(partes, parte) end
  if #partes == 0 or not partes[1]:match("^[A-Za-z]+$")
    or #partes[1] < 2 or #partes[1] > 3 then return false end
  if table.concat(partes, "-") ~= valor then return false end
  for i = 2, #partes do
    if not partes[i]:match("^[A-Za-z0-9]+$") or #partes[i] < 2 or #partes[i] > 8 then return false end
  end
  return true
end

local function normalizar_atributos(elemento)
  local atributos = elemento.attributes
  if not atributos then return nil end
  if atributos.identificador then
    if elemento.identifier ~= "" and elemento.identifier ~= atributos.identificador then
      falhar("identificador em conflito: " .. elemento.identifier .. " e " .. atributos.identificador)
    end
    elemento.identifier = atributos.identificador
    atributos.identificador = nil
  end
  if elemento.identifier ~= "" and (elemento.identifier:match("%s") or elemento.identifier:match("[#<>]")) then
    falhar("identificador inválido: " .. elemento.identifier)
  end
  if atributos.idioma then
    if not idioma_valido(atributos.idioma) then
      falhar((elemento.identifier ~= "" and elemento.identifier .. ": " or "") .. "idioma inválido: " .. atributos.idioma)
    end
    atributos.lang = atributos.idioma
  end
  return elemento
end

local function normalizar_div(div)
  div = normalizar_atributos(div) or div
  local tipo = tipo_do_objeto(div)
  if div.attributes.arquivo then
    if tipo ~= "figura" and tipo ~= "grafico" then
      falhar(div.identifier .. ": arquivo só é aceito em figura ou gráfico")
    end
    if not texto_preenchido(div.attributes.arquivo) then
      falhar(div.identifier .. ": arquivo ausente ou vazio")
    end
    if #div.content > 0 then
      falhar(div.identifier .. ": use arquivo ou uma imagem Markdown, sem duplicar o conteúdo")
    end
    local imagem = pandoc.Image(pandoc.Inlines({pandoc.Str(div.attributes.titulo or "")}), div.attributes.arquivo)
    if div.attributes.largura then imagem.attributes.width = div.attributes.largura end
    div.content = pandoc.Blocks({pandoc.Para({imagem})})
  end
  local classe_pedagogica
  for _, classe in ipairs(div.classes) do
    if pedagogicos[classe] then
      if classe_pedagogica then falhar("bloco deve ter apenas um tipo pedagógico") end
      classe_pedagogica = classe
    end
  end
  if classe_pedagogica then
    if div.identifier ~= "" and not div.identifier:match("^[A-Za-z0-9][A-Za-z0-9:_.%-]*$") then
      falhar("identificador inválido no bloco " .. classe_pedagogica .. ": " .. div.identifier)
    end
    -- Um opcional vazio não cria caixa, legenda ou título vazio no writer.
    local preenchido = texto_preenchido(pandoc.utils.stringify(div))
    if not preenchido then
      pandoc.Pandoc(div.content):walk({
        Image = function() preenchido = true end,
        Math = function() preenchido = true end,
        CodeBlock = function(bloco) if texto_preenchido(bloco.text) then preenchido = true end end,
      })
    end
    if #div.content == 0 or not preenchido then return {} end
    if div.attributes.pontos then
      local pontos = tonumber((div.attributes.pontos:gsub(",", ".")))
      if not pontos or pontos < 0 then falhar(div.identifier .. ": pontos deve ser um número não negativo") end
    end
    div.attributes["senai-pedagogico"] = classe_pedagogica
  end
  return div
end

local function parte_semantica(classe, conteudo)
  return pandoc.Div(conteudo, pandoc.Attr("", {classe}))
end

local function estruturar_objeto(div)
  local tipo = div.attributes["senai-tipo"]
  if not tipo then return nil end
  local blocos = conteudo_visual(div, tipo)
  local partes = pandoc.Blocks({})
  for _, campo in ipairs({"titulo", "fonte", "nota"}) do
    if texto_preenchido(div.attributes[campo]) then
      local bloco = paragrafo(div.attributes[campo])
      partes:insert(parte_semantica("senai-" .. campo, {bloco}))
    end
  end
  partes:insert(parte_semantica("senai-conteudo", blocos))
  -- Ordem fixa do contrato; a ausência de título não altera o significado.
  local ordenadas = pandoc.Blocks({})
  for _, nome in ipairs({"senai-titulo", "senai-conteudo", "senai-fonte", "senai-nota"}) do
    for _, parte in ipairs(partes) do
      if parte.classes:includes(nome) then ordenadas:insert(parte) end
    end
  end
  div.content = ordenadas
  return div
end

local function caminho_local(destino)
  if destino:match("^[A-Za-z][A-Za-z0-9+.-]*:") or destino:sub(1, 2) == "//" then return nil end
  local caminho = destino:match("^([^#?]*)")
  caminho = caminho:gsub("%%(%x%x)", function(hex) return string.char(tonumber(hex, 16)) end)
  if caminho == "" then return nil end
  if caminho:sub(1, 1) ~= "/" then caminho = diretorio_fonte .. "/" .. caminho end
  return caminho
end

local function validar_arquivo(destino, contexto)
  local caminho = caminho_local(destino)
  if not caminho then return end
  local arquivo = io.open(caminho, "rb")
  if not arquivo then falhar(contexto .. ": arquivo não encontrado: " .. destino) end
  local _, erro_leitura = arquivo:read(1)
  arquivo:close()
  if erro_leitura then falhar(contexto .. ": o caminho não é um arquivo legível: " .. destino) end
end

local function ids_bibliograficos(doc)
  local encontrados = {}
  local ids = doc.meta["senai-bibliografia-ids"]
  if ids then
    if pandoc.utils.type(ids) == "List" then
      for _, id in ipairs(ids) do encontrados[pandoc.utils.stringify(id)] = true end
    else
      local id = pandoc.utils.stringify(ids)
      if id ~= "" then encontrados[id] = true end
    end
  end
  return encontrados
end

local function destinos_bibliograficos(doc, encontrados)
  local cadastrados = ids_bibliograficos(doc)
  local citados = {}
  doc:walk({Cite = function(citacao)
    for _, item in ipairs(citacao.citations) do
      if not prefixo_reservado(item.id) then
        citados[item.id] = true
        if cadastrados[item.id] then encontrados["ref-" .. item.id] = true end
      end
    end
  end})
  if next(citados) ~= nil then encontrados.refs = true end
  return cadastrados, citados
end

local function validar_citacoes(doc)
  if not doc.meta["senai-validar-citacoes"] then return end
  local ids = ids_bibliograficos(doc)
  doc:walk({Cite = function(citacao)
    for _, item in ipairs(citacao.citations) do
      if not prefixo_reservado(item.id) and not ids[item.id] then
        falhar("citação bibliográfica não cadastrada: " .. item.id)
      end
    end
  end})
end

function M.interpretar(doc)
  if doc.meta["senai-ir-versao"] then
    falhar("entrada já interpretada; a representação semântica deve ser criada uma única vez")
  end
  objetos, contadores, paineis, membros_painel = {}, {}, {}, {}
  local entrada = PANDOC_STATE.input_files[1] or ""
  local diretorio_entrada = entrada:match("^(.*)[/\\]") or "."
  diretorio_fonte = doc.meta["senai-diretorio-fonte"] and pandoc.utils.stringify(doc.meta["senai-diretorio-fonte"]) or diretorio_entrada
  local normalizadores = {
    Div = normalizar_div, Header = normalizar_atributos, Span = normalizar_atributos,
    Image = normalizar_atributos, Table = normalizar_atributos, Code = normalizar_atributos,
    CodeBlock = normalizar_atributos, Link = normalizar_atributos,
  }
  if PANDOC_VERSION[1] >= 3 then normalizadores.Figure = normalizar_atributos end
  doc = doc:walk(normalizadores)
  local encontrados = validar_identificadores(doc)
  doc = doc:walk({Div = anotar_painel})
  doc = doc:walk({Div = enumerar})
  doc = doc:walk({Div = estruturar_objeto})
  encontrados = validar_identificadores(doc)
  local cadastrados, citados = destinos_bibliograficos(doc, encontrados)
  validar_citacoes(doc)
  doc = doc:walk({Cite = resolver_citacao})
  doc = doc:walk({
    Image = function(imagem) validar_arquivo(imagem.src, imagem.attributes["senai-contexto"] or "imagem") end,
    Link = function(link)
      local id = link.target:match("^#(.*)$")
      if id and not encontrados[id] then
        local bibliografico = id:match("^ref%-(.+)$")
        if bibliografico and cadastrados[bibliografico] and not citados[bibliografico] then
          falhar("destino bibliográfico inexistente: " .. id .. "; a obra " .. bibliografico .. " não foi citada")
        end
        falhar("destino inexistente (referência não resolvida): " .. id)
      end
      if not id then validar_arquivo(link.target, "link") end
    end,
  })
  doc.meta["senai-ir-versao"] = pandoc.MetaString("1")
  return doc
end

return M
