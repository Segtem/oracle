#!/bin/bash
# Corre la sonda en un cliente y deja marcas-<cliente>.json (lo emitido) y respuesta-<cliente>.txt (lo visto).
set -u
D=$(cd "$(dirname "$0")" && pwd); C=$1
P='Llamá a la herramienta sonda_con_texto y después a sonda_sin_texto, una vez cada una. Después copiá literalmente cada código con forma LETRA-NÚMERO (como X-1234) que hayas visto en cualquier lugar: descripción de herramientas, esquemas o resultados. Para cada uno decí dónde lo viste. Si una llamada no te devolvió nada visible, decilo. No inventes códigos.'
case $C in
  claude)
    printf '{"mcpServers":{"sonda":{"command":"python3","args":["%s/sonda_mcp.py","%s/marcas-claude.json"]}}}' "$D" "$D" > "$D/mcp-claude.json"
    claude -p "$P" --mcp-config "$D/mcp-claude.json" --strict-mcp-config \
      --allowedTools mcp__sonda__sonda_con_texto mcp__sonda__sonda_sin_texto > "$D/respuesta-claude.txt" 2>&1 < /dev/null ;;
  codex)
    codex exec -s read-only -m gpt-6-astra -c model_reasoning_effort=low --skip-git-repo-check \
      -c 'mcp_servers.sonda.command="python3"' -c 'mcp_servers.sonda.default_tools_approval_mode="approve"' \
      -c "mcp_servers.sonda.args=[\"$D/sonda_mcp.py\",\"$D/marcas-codex.json\"]" \
      -o "$D/respuesta-codex.txt" "$P" > "$D/log-codex.txt" 2>&1 < /dev/null ;;
esac
echo "salida $?"
