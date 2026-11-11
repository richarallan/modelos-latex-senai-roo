-- Markdown -> IR comum, independente do template e formato.
local base = (PANDOC_SCRIPT_FILE:match("^(.*[/\\])") or "")
local function modulo(nome) return dofile(base .. "../nucleo/lua/" .. nome .. ".lua") end
return {{Pandoc = modulo("semantica").interpretar}}
