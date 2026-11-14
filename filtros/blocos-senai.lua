-- Adapter de compatibilidade dos blocos pedagógicos.
local base = (PANDOC_SCRIPT_FILE:match("^(.*[/\\])") or "")
local function modulo(nome) return dofile(base .. "../nucleo/lua/" .. nome .. ".lua") end
return {{Pandoc = function(doc)
  if not doc.meta["senai-ir-versao"] then doc = modulo("semantica").interpretar(doc) end
  return modulo("apresentacao").apresentar(doc, {objetos = false, pedagogicos = true})
end}}
