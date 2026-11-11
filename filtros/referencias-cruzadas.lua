-- Adapter de compatibilidade. Novos fluxos usam semantica.lua e apresentacao.lua.
local base = (PANDOC_SCRIPT_FILE:match("^(.*[/\\])") or "")
local function modulo(nome) return dofile(base .. "../nucleo/lua/" .. nome .. ".lua") end
return {{Pandoc = function(doc)
  doc = modulo("semantica").interpretar(doc)
  return modulo("apresentacao").apresentar(doc, {objetos = true, pedagogicos = false})
end}}
