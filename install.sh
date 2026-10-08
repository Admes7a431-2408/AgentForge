#!/usr/bin/env bash
# Instala AgentForge como skill enlazada (una sola fuente de verdad: este directorio).
#   ./install.sh [--claude] [--antigravity] [--agents] [--uninstall] [--dry-run] [-h|--help]
# Sin flags de plataforma actúa sobre ambas. Nunca sobrescribe: si el destino existe y no es
# un enlace a este directorio, lo informa y lo deja intacto. --uninstall elimina únicamente
# los enlaces que apuntan a AgentForge.
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"  # ruta física, comparable con readlink -f
claude=0; agy=0; agents=0; dry=0; uninstall=0

usage() {
  cat <<EOF
uso: $0 [--claude] [--antigravity] [--agents] [--uninstall] [--dry-run] [-h|--help]

  --claude       enlaza la skill en ~/.claude/skills/agentforge
  --antigravity  enlaza la skill en ~/.gemini/config/skills/agentforge
  --agents       enlaza adapters/claude-code/agents/*.md en ~/.claude/agents/
  --uninstall    elimina solo los enlaces que apuntan a este directorio
  --dry-run      muestra lo que haría sin modificar nada
  -h, --help     muestra esta ayuda

Sin --claude ni --antigravity se actúa sobre ambas plataformas.
EOF
}

for a in "$@"; do
  case "$a" in
    --claude) claude=1 ;;
    --antigravity) agy=1 ;;
    --agents) agents=1 ;;
    --uninstall) uninstall=1 ;;
    --dry-run) dry=1 ;;
    -h|--help) usage; exit 0 ;;
    *) usage >&2; exit 2 ;;
  esac
done
(( claude || agy )) || { claude=1; agy=1; }

run() { if (( dry )); then echo "[dry-run] $*"; else "$@"; fi; }

link() {  # link <destino> <origen>
  local dst="$1" target="$2"
  if [[ -L "$dst" && "$(readlink -f "$dst")" == "$(readlink -f "$target")" ]]; then
    echo "ok      $dst (ya enlazado)"
  elif [[ -e "$dst" || -L "$dst" ]]; then
    echo "omitido $dst existe y no apunta a $target; revísalo a mano" >&2
  else
    run mkdir -p "$(dirname "$dst")"
    run ln -s "$target" "$dst"
    echo "enlazado $dst -> $target"
  fi
}

unlink_ours() {  # unlink_ours <destino> <origen>: solo borra si es un enlace a <origen>
  local dst="$1" target="$2"
  if [[ -L "$dst" && "$(readlink -f "$dst")" == "$(readlink -f "$target")" ]]; then
    run rm "$dst"
    echo "eliminado $dst"
  elif [[ -e "$dst" || -L "$dst" ]]; then
    echo "omitido $dst no apunta a $target; no se toca" >&2
  else
    echo "ok      $dst (no existe)"
  fi
}

if (( uninstall )); then act=unlink_ours; else act=link; fi

(( claude )) && "$act" "$HOME/.claude/skills/agentforge" "$SRC"
(( agy )) && "$act" "$HOME/.gemini/config/skills/agentforge" "$SRC"

if (( agents )); then
  (( uninstall )) || run mkdir -p "$HOME/.claude/agents"
  for f in "$SRC"/adapters/claude-code/agents/*.md; do
    "$act" "$HOME/.claude/agents/$(basename "$f")" "$f"
  done
fi

if (( ! uninstall )); then
  python3 -c 'import yaml' 2>/dev/null || echo "aviso: scripts/af.py necesita PyYAML (pip install pyyaml)" >&2
fi
