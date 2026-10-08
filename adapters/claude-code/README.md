# Adapter: Claude Code

Solo diferencias de plataforma. La metodología está en `methodology/`; el mapeo tier → modelo en `routing/profiles.yaml` (`platforms.claude-code`).

## Capacidades reales

| Necesidad | Mecanismo | Nota |
|---|---|---|
| Cambiar modelo/esfuerzo de la sesión principal | `/model`, `/effort` (humano) o `claude --model --effort` al arrancar | Una skill no puede cambiarlo a mitad de sesión. No lo intentes: delega. |
| Ejecutar con otro tier | Herramienta **Agent** con `model` y `effort` | `model` del Agent tiene prioridad sobre el frontmatter del agente. Esta skill autoriza explícitamente fijar `effort` según el tier. |
| Restringir herramientas de un subagente | Agentes en `~/.claude/agents/*.md` (`tools`, `disallowedTools`) | Ver `agents/` de este adapter. |
| Paralelizar | Varias llamadas Agent en el mismo turno; `run_in_background` | Si editan los mismos archivos: `isolation: "worktree"`. |
| Aislar ediciones | `isolation: "worktree"` | Revisa e integra el diff tú mismo. |
| Imponer permisos de un contrato en modo headless | `claude -p --allowedTools … --disallowedTools … --permission-mode …` | Traduce `permissions.commands` a reglas `Bash(<cmd>:*)`. |
| Gate de alcance | `python3 <AgentForge>/scripts/af.py check-scope <contrato>` | Tras la ejecución, antes de aceptar. |

## Delegar desde Claude Code

1. Decide el tier con [routing.md §3](../../methodology/routing.md#3-ejecutar-o-delegar).
2. Elige el agente por **función** (`profiles.yaml → agents`): explorar → `af-scout` (o `scout`), ejecutar → `af-worker` (o `worker`), revisar → `af-reviewer` (o `reviewer`). Para lo que no encaja: `general-purpose`.
3. Pasa `model` y `effort` del tier (`python3 scripts/af.py tier DEEP --platform claude-code`). Especifícalos siempre: omitirlos usa el frontmatter del agente (un valor de respaldo que puede quedar desfasado respecto a `profiles.yaml`) o hereda el de la sesión.
4. El prompt es el brief de [routing.md §4](../../methodology/routing.md#4-el-brief-todo-encargo-delegado) o un puntero al contrato.
5. Verifica el resultado (P9) antes de seguir.

Los subagentes de Claude Code pueden anidarse, pero AgentForge limita la profundidad a tres niveles ([routing.md §7](../../methodology/routing.md#7-límites-estructurales)); por eso `af-worker` y `af-reviewer` no reciben la herramienta Agent.

## Recibir un contrato de Antigravity (modo headless)

Antigravity invoca a Claude con un prompt autocontenido que apunta al contrato, p. ej.:

```
Usa la skill agentforge. Ejecuta el contrato .agentforge/contracts/AF-0012-x.yaml como executor.
Escribe el reporte en .agentforge/reports/AF-0012-x.yaml y responde solo STATUS + 5 líneas de resumen.
```

Claude actúa como Executor ([workflow.md](../../methodology/workflow.md#procedimiento-del-executor)): puede sub-delegar dentro de lo que permita `routing.allow_delegation`, y su respuesta final es `STATUS` + ruta del reporte. No ve la conversación de Antigravity: si el contrato no basta, responde `NEEDS_CONTEXT` con las preguntas concretas.

## Instalación

`install.sh` en la raíz enlaza la skill en `~/.claude/skills/agentforge` y, con `--agents`, copia `agents/*.md` a `~/.claude/agents/` (no sobrescribe archivos existentes). Si ya tienes `scout`, `worker` y `reviewer`, no hacen falta: `profiles.yaml` los reconoce como equivalentes.
