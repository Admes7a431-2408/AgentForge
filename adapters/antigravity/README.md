# Adapter: Antigravity

Solo diferencias de plataforma. La metodología está en `methodology/`; el mapeo tier → modelo en `routing/profiles.yaml` (`platforms.antigravity`).

## Capacidades reales

| Necesidad | Mecanismo | Nota |
|---|---|---|
| Cambiar modelo de la sesión principal | `/model` (humano; persiste entre sesiones) | No se asume cambio por tarea. Para otro tier, delega. |
| Descargar contexto / paralelizar **con el mismo modelo** | Subagente nativo `invoke_subagent` — `TypeName: research` (solo lectura) o `self` (capacidad completa) | La documentación no garantiza modelo/esfuerzo por subagente: trátalos como *mismo tier*. Ideales para P11 (contexto caro, razonamiento barato). |
| Ejecutar con **otro tier** de Gemini | Subproceso headless: `agy -p "<brief>" --model <m> --effort <e> --mode plan --output-format json` | Valores con `python3 scripts/af.py tier <TIER> --platform antigravity`. `--mode plan` = solo lectura; `--mode accept-edits` solo con contrato que autorice escribir. |
| Delegar la **ejecución** a Claude Code | Skill `claude`: `~/.gemini/config/skills/claude/scripts/ask-claude.sh [--write] --model <m> --effort <e> "<prompt>"` | Tier con `af.py tier <TIER> --platform claude-code`. Es el handoff Orchestrator → Executor por defecto. |
| Seguimiento de tareas | Task artifact (`write_to_file`, `IsArtifact: true`, `ArtifactType: "task"`) | `manage_task` es para procesos en segundo plano, no checklists. |
| Supervisar subagentes | `/agents` (estado, pasos, permisos pendientes) | |
| Imponer permisos de comandos en headless | `~/.gemini/antigravity-cli/settings.json → permissions.allow` | Sintaxis `command(<binario> <subcomando>)`. Nunca `--dangerously-skip-permissions`. |
| Gate de alcance | `python3 <AgentForge>/scripts/af.py check-scope <contrato>` | Tras recibir el resultado del executor. |

## Antigravity como Orchestrator

1. Aplica el [procedimiento del Orchestrator](../../methodology/workflow.md#procedimiento-del-orchestrator). Investiga con subagentes `research` cuando la exploración es amplia.
2. Escribe cada contrato en `.agentforge/contracts/<id>.yaml` y valídalo: `python3 <AgentForge>/scripts/af.py validate <ruta>`.
3. Lanza al executor con un prompt corto que apunta al contrato (Claude no ve esta conversación):

   ```bash
   eval "$(python3 <AgentForge>/scripts/af.py tier STANDARD --platform claude-code)"   # define $model y $effort
   ~/.gemini/config/skills/claude/scripts/ask-claude.sh --write --model "$model" --effort "$effort" \
     "Usa la skill agentforge. Ejecuta el contrato .agentforge/contracts/AF-0012-x.yaml como executor. \
      Escribe el reporte en .agentforge/reports/AF-0012-x.yaml y responde solo STATUS + 5 líneas."
   ```

   El tier sale de `routing.preferred_tier` del contrato. `--write` solo si el contrato autoriza escribir; nunca mientras tú editas los mismos archivos.
4. **Verifica** (P9): lee el reporte, `git diff`, ejecuta `verification.commands` y `af.py check-scope <contrato> --base <commit de partida>`. Si la [matriz de gates](../../methodology/quality-gates.md#selección) exige G8, pide revisión independiente (Claude `af-reviewer`/DEEP en solo lectura, o `agy` en `--mode plan` con un tier DEEP).
5. Integra, reporta y, si hubo señal, registra aprendizajes.

## Antigravity como Executor

Cuando el humano le da una tarea L0–L2 directamente, Antigravity la ejecuta él mismo siguiendo el [procedimiento del Executor](../../methodology/workflow.md#procedimiento-del-executor) y aplica la misma decisión ejecutar/delegar ([routing.md §3](../../methodology/routing.md#3-ejecutar-o-delegar)).

## Límites

- Las llamadas anidadas entre puentes están bloqueadas por `AGENT_BRIDGE_DEPTH` (Claude invocado por Antigravity no puede invocar a Antigravity). Encaja con el límite de tres niveles.
- Si la salida de un headless dice `[denegado en headless: …]`, faltó un permiso: repórtalo, no reintentes a ciegas.
- En `agy -p` una acción denegada puede terminar el turno **sin respuesta** (`status: SUCCESS`, `response` vacío). Comprueba `denied_actions` en el JSON. Para encargos de solo lectura, indica en el brief que use únicamente herramientas de lectura de archivos y no comandos de terminal (verificado 2026-10-07).

## Instalación

`install.sh` en la raíz enlaza la skill en `~/.gemini/config/skills/agentforge` (descubrimiento global de Antigravity). Para un solo proyecto, enlázala en `<proyecto>/.agents/skills/agentforge`.
