#!/usr/bin/env bash
# Instala AgentForge como skill enlazada (una sola fuente de verdad: este directorio).
#   ./install.sh [--claude] [--antigravity] [--agents] [--dry-run]
# Sin flags de plataforma instala en ambas. Nunca sobrescribe: si el destino existe y no es
# un enlace a este directorio, lo informa y lo deja intacto.
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"  # ruta física, comparable con readlink -f
claude=0; agy=0; agents=0; dry=0
for a in "$@"; do
  case "$a" in
    --claude) claude=1 ;;
    --antigravity) agy=1 ;;
    --agents) agents=1 ;;
    --dry-run) dry=1 ;;
    *) echo "uso: $0 [--claude] [--antigravity] [--agents] [--dry-run]" >&2; exit 2 ;;
  esac
done
(( claude || agy )) || { claude=1; agy=1; }

run() { if (( dry )); then echo "[dry-run] $*"; else "$@"; fi; }

link() {  # link <destino>
  local dst="$1"
  if [[ -L "$dst" && "$(readlink -f "$dst")" == "$SRC" ]]; then
    echo "ok      $dst (ya enlazado)"
  elif [[ -e "$dst" || -L "$dst" ]]; then
    echo "omitido $dst existe y no apunta a $SRC; revísalo a mano" >&2
  else
    run mkdir -p "$(dirname "$dst")"
    run ln -s "$SRC" "$dst"
    echo "enlazado $dst -> $SRC"
  fi
}

(( claude )) && link "$HOME/.claude/skills/agentforge"
(( agy )) && link "$HOME/.gemini/config/skills/agentforge"

if (( agents )); then
  run mkdir -p "$HOME/.claude/agents"
  for f in "$SRC"/adapters/claude-code/agents/*.md; do
    dst="$HOME/.claude/agents/$(basename "$f")"
    if [[ -L "$dst" && "$(readlink -f "$dst")" == "$(readlink -f "$f")" ]]; then
      echo "ok      $dst (ya enlazado)"
    elif [[ -e "$dst" || -L "$dst" ]]; then
      echo "omitido $dst existe y no apunta a $f; revísalo a mano" >&2
    else
      run ln -s "$f" "$dst"; echo "enlazado $dst -> $f"
    fi
  done
fi

python3 -c 'import yaml' 2>/dev/null || echo "aviso: scripts/af.py necesita PyYAML (pip install pyyaml)" >&2
