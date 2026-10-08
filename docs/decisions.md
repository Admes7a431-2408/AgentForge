# Decisiones de AgentForge

Registro de por qué AgentForge es como es. Las propuestas de cambio a la metodología (desde el learning loop) se añaden aquí con su evidencia; una decisión se reemplaza con otra nueva, no se reescribe.

## Matriz de integración (estudio de referencias, 2026-10-07)

Referencias: **SP** = obra/superpowers · **MP** = mattpocock/skills · **KP** = multica-ai/andrej-karpathy-skills · **NR** = nobodyohm-web/claude-code-model-router · **BG** = BearGare/claude-skills (model-routing, scope-control, verification-standards) · **CR** = shaaz1000/claude-router.

| Mecanismo | Origen | Veredicto | Dónde vive en AgentForge |
|---|---|---|---|
| Cuatro principios (pensar antes, simplicidad, quirúrgico, orientado al objetivo) | KP | **Conservar** | `principles.md` P1–P5 |
| "Para tareas triviales, usa el juicio" | KP | **Conservar** como rigor proporcional | Levels + gates por nivel/riesgo |
| Iron laws absolutas (TDD siempre, "1 % de probabilidad → invocar skill") | SP | **Descartar** | Sustituidas por gates proporcionales; TDD cuando hay cambio de comportamiento + harness |
| Evidencia fresca antes de afirmar éxito; tabla afirmación/requisito | SP, BG | **Conservar** | P6, `quality-gates.md` (estándar de evidencia) |
| "Unverified" honesto cuando no se puede comprobar | BG | **Conservar** | gate `not_run`, `verified: false` |
| Clasificar en voz alta y trinquete hacia arriba (spike/bounded/architectural) | SP | **Adaptar** | Línea `Route:` con 3 ejes; el trinquete solo es obligatorio para el riesgo |
| Plan = decisiones que el implementador no puede tomar solo; interfaces consumes/produces; restricciones globales literales | SP | **Adaptar** | Campos del contrato (`context.interfaces`, `constraints`) |
| Brief en archivo + contrato de retorno corto; punteros, no copias | SP, MP | **Conservar** | `routing.md §4`, handoff de `workflow.md` |
| Estados DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED | SP | **Conservar** + `ESCALATE` de CR | `routing.md §4` |
| "No confíes en el informe"; revisión en dos ejes (spec/contrato vs calidad) reportados por separado | SP, MP | **Conservar** | G8, `af-reviewer` |
| El controlador no corrige hallazgos él mismo; re-revisión limitada al diff de la corrección | SP | **Conservar** | G8 |
| Bucle de corrección de 5 rondas, tabla de conflictos previa, ledger para todo, worktree para todo | SP | **Descartar** (peso) | Límite de 2 rondas + escalamiento; worktrees solo para ediciones paralelas |
| Rulings `qué — por qué — coste si me equivoco` y 4 condiciones de parada | SP | **Conservar** | `governance.md` (rulings, human gates) |
| Especificar siempre el modelo al delegar; "los turnos pesan más que el precio por token" | SP | **Conservar** | `routing.md §7` |
| Descripción de la skill = solo disparadores, nunca el flujo | SP | **Conservar** | Frontmatter de `SKILL.md` |
| Verbos abstractos + tabla por plataforma (incl. mapeo Antigravity `invoke_subagent`) | SP | **Conservar** | `adapters/` |
| Hook SessionStart que inyecta la skill completa | SP | **Descartar** | Descubrimiento nativo por descripción en ambas plataformas; menos contexto fijo |
| Feedback loop primero; comando red-capable ejecutado una vez antes de teorizar | MP | **Conservar** (generalizado a toda tarea con comportamiento) | Executor "Durante", estándar de evidencia |
| Debugging: reproducir → minimizar → 3–5 hipótesis falsables → una variable → regresión; logs etiquetados | MP | **Adaptar** (condensado) | `workflow.md` Executor |
| Seams acordados con el usuario antes de cada test | MP | **Adaptar** | El contrato nombra los seams (`verification.seams`); el ejecutor no pregunta |
| Tests no tautológicos, por interfaz pública, cortes verticales | MP | **Conservar** | Estándar de evidencia, Executor |
| GLOSSARY con `_Avoid_`, una palabra por concepto, sin implementación; ADR solo si difícil de revertir + sorprendente + trade-off | MP | **Conservar** | `knowledge.md` (CONTEXT.md, decisions.md) |
| Edición interactiva del glosario por el ejecutor | MP | **Conflicto → resuelto**: el executor propone en el reporte; escribe el orchestrator/humano | `knowledge.md` |
| Grilling sin límite de preguntas | MP | **Descartar** | Una ronda, solo lo que bloquea, con recomendación (`governance.md`) |
| Tickets como cortes verticales que caben en un contexto fresco; frontera de dependencias; expand-contract para cambios amplios | MP | **Conservar** | Orchestrator paso 4 |
| Dependencia de issue tracker y etiquetas | MP | **Descartar** | Contratos en `.agentforge/contracts/` |
| Escalera de tiers + "config, no prosa" | NR | **Conservar** | `profiles.yaml` es el único lugar con modelos |
| Esfuerzo como palanca independiente (±1) antes de cambiar de modelo | NR, BG | **Conservar** | `routing.md §1, §6` |
| No reintentar el mismo tier; diagnosticar antes de que el superior rehaga; recordar el tier que funcionó | NR | **Conservar** | `routing.md §6` |
| Supervisión hacia abajo; FAST no orquesta; no anidar orquestación en workers | NR | **Conservar** | `routing.md §7` |
| Verificador independiente que intenta refutar | NR | **Conservar** | G8 |
| Clasificador por regex en hook `UserPromptSubmit` | NR, CR | **Descartar** | El agente clasifica con más contexto que un regex; CR necesitó 4 versiones para corregir malas rutas |
| Telemetría en JSONL + estadísticas de ahorro | NR | **Adaptar (diferido)** | Las líneas `Route:` y `delegations` del reporte son el registro; un hook de telemetría es una extensión futura (AD-006) |
| Posturas quality-first / balanced / max-savings | NR | **Adaptar** | `postures` en `profiles.yaml` |
| La sesión principal no cambia de modelo por hook; los subagentes son el mecanismo real | CR, BG | **Conservar** | P10, adapters |
| Brief autocontenido; `ESCALATE: <motivo>` del worker barato | CR | **Conservar** | `routing.md §4` |
| Contenido pegado ≠ complejidad; las continuaciones se quedan en la sesión principal | CR | **Conservar** | `routing.md §3` |
| Profundidad máxima de spawn; un subagente no se auto-escala | BG | **Conservar** | `routing.md §7` |
| Prerrequisito > ~1/3 de la tarea = decisión de alcance; señales de deriva | BG | **Conservar** | `governance.md` (desviaciones) |
| Precios y nombres de modelos en la prosa de la skill | BG, NR | **Descartar** | Caducan; solo en `profiles.yaml` con `verified_on` |

### Conflictos resueltos

1. **"Ante la duda, el camino más pesado" (SP) vs "las tareas simples siguen siendo simples" (KP).** El trinquete se aplica al *riesgo* (ante la duda, más alto); el *tamaño* empieza ligero y sube solo con evidencia. Ver `routing.md §2`.
2. **TDD obligatorio (SP) vs rigor proporcional.** TDD es el modo por defecto cuando hay cambio de comportamiento y harness; si no, la verificación red-capable más barata. Nunca "sin verificación".
3. **Implementadores nunca en paralelo (SP) vs L4 multi-stream.** Paralelo solo con alcances disjuntos (comprobables con `check-scope`) o worktrees.
4. **Seams confirmados por el usuario (MP) vs ejecutor autónomo.** Los decide el orchestrator en el contrato.

## Decisiones

**AD-001 — Tres ejes (level, tier, risk) en vez de una sola "complejidad".** Lo pedido mezcla tamaño del proceso, capacidad cognitiva y consecuencia; una tarea fácil puede ser crítica. Separarlos permite que el riesgo active gates sin inflar el proceso y que una tarea L1 use DEEP. Coste: tres valores que declarar; se mitiga con una sola línea `Route:`.

**AD-002 — Tiers abstractos (FAST/STANDARD/DEEP/MAX) mapeados solo en `profiles.yaml`.** Los catálogos de modelos cambian cada pocos meses y difieren por plataforma. El contrato usa `preferred_tier`; `preferred_model` existe solo como override excepcional.

**AD-003 — Delegación como mecanismo de routing portable.** Ni Claude Code ni Antigravity permiten a una skill cambiar el modelo de la sesión principal. En Antigravity, los subagentes nativos no garantizan modelo propio, así que el cambio de tier real se hace con `agy -p --model --effort` o con el puente a Claude.

**AD-004 — Una skill con divulgación progresiva, no varias skills.** Un solo disparador y un `SKILL.md` corto que enruta a los archivos de `methodology/` según la situación. Varias skills duplicarían reglas o se dispararían de forma inconsistente entre plataformas.

**AD-005 — Instalación por enlace simbólico.** El mismo directorio es la skill en ambas plataformas (`~/.claude/skills/agentforge`, `~/.gemini/config/skills/agentforge`). No hay copias que puedan divergir.

**AD-006 — Sin hooks en v1.** Los hooks (clasificador, telemetría) añaden instalación, mantenimiento y modos de fallo por plataforma. La traza de routing vive en los reportes. Revisar si los reportes muestran que hace falta medir ahorro con datos.

**AD-007 — Un script determinista (`af.py`) para lo que un modelo haría peor o más caro.** Validar estructura, comprobar alcance contra el diff y resolver tiers. Requiere Python 3 + PyYAML.

**AD-008 — Metodología en español, campos y estados en inglés.** El usuario trabaja en español; los nombres de campos, estados y tiers en inglés son estables y comunes a ambas plataformas.

**AD-009 — Endurecimientos tras la validación con agentes reales (2026-10-07).** Evidencia y cambio:
- *Executor Claude (sonnet/medium, headless) sobre un contrato L2:* corrigió el bug con un diff mínimo y un test que falla antes y pasa después (verificado de forma independiente), pero declaró G5 `pass` de memoria cuando el árbol tenía archivos generados modificados. → G5 exige la salida de `check-scope`; cada `pass` cita un comando ejecutado.
- *Orchestrator Antigravity (gemini-3.1-pro-high, headless, solo lectura):* buena clasificación, preguntas con recomendación y comando de lanzamiento correcto; pero el contrato tenía alcance `src/**/*`, comandos de verificación inventados o vacíos, `interfaces` vacío pese a un cambio de forma de datos y un id repetido. → `af.py validate` exige `verification.commands` desde L2 y avisa de alcances amplios e ids duplicados; el paso *Contratar* exige comprobar el contrato contra el repo.
- *Antigravity headless:* un comando denegado terminó el turno sin respuesta y con `status: SUCCESS`. → Nota en el adapter: comprobar `denied_actions` y pedir solo herramientas de lectura en encargos de solo lectura.
- *Clasificación (Claude sonnet/low, 6 tareas):* L0 siguió siendo L0; la búsqueda amplia se delegó a FAST; secretos y producción se detuvieron en un human gate; un fallo previo escaló a MAX con diagnóstico. Sin cambios.
- *Revisión independiente (opus/high):* 12 defectos de coherencia, todos corregidos: delegación hacia arriba y conteo de profundidad (§7), umbral único de G8 en la matriz, L2 definido sin riesgo, vocabulario de estados único, `check-scope` robusto (renombrados, globs por segmento, rutas no ASCII, contrato leído desde `--base`, `.agentforge/` no exento salvo el reporte propio), instalador.

**AD-010 — Correcciones de auditoría del tooling (AF-0020).** `af.py validate`: `DONE` exige `verified: true` y ninguna gate `not_run`/`fail`; clasifica `agent.yaml` como `agent` con validación propia; `--contract <ruta>` exige que los reportes incluyan todas las gates del contrato. `check-scope` falla si el contrato no está en git a `--base` (salvo `--allow-untracked-contract`). `af.py` calcula `ROOT` con `realpath` (robusto ante symlinks). `install.sh --agents` enlaza (`ln -s`) en vez de copiar, coherente con AD-005. `workflow.md` exige commitear el contrato antes de delegar; `governance.md` aclara que `permissions.commands` es un soft gate conductual en v1.
Los frontmatters de `adapters/claude-code/agents/*.md` (`model: sonnet|opus|haiku`) son solo un fallback de sintaxis de la plataforma: la fuente de verdad del modelo son los tiers de `routing/profiles.yaml`.
