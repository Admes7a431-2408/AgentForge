# Arquitectura

## Flujo objetivo

```
                    HUMAN / PRODUCT OWNER
                            │  intención, decisiones L5, human gates
                            ▼
                    INTENT (GPT, opcional)
                            │  objetivo refinado
                            ▼
              ORCHESTRATOR (Antigravity por defecto)
        Research ─── Architecture ─── Decomposition ─── Routing
                            │
                            ▼
                 CONTRACTS (.agentforge/contracts/)
                            │  autoridad: alcance, permisos, criterios
          ┌─────────────────┼─────────────────┐
          ▼                 ▼                 ▼
      Specialist      EXECUTOR (Claude)     Reviewer
       (hoja)       ── puede sub-delegar ──  (hoja, solo lectura)
          └─────────────────┼─────────────────┘
                            ▼
                QUALITY GATES (G1–G8 por level/risk)
                            ▼
                REPORT (.agentforge/reports/)
                            ▼
              LEARNING LOOP (solo con señal)
```

Capas transversales y dónde viven:

| Capa | Archivo |
|---|---|
| Error prevention | `methodology/principles.md` (P1–P7) |
| Authority | `methodology/principles.md` (P8), `methodology/governance.md` |
| Governance | `methodology/governance.md`, `contracts/templates/` |
| Adaptive routing | `methodology/routing.md`, `routing/profiles.yaml` |
| Traceability | líneas `Route:`, rulings, contratos y reportes enlazados por `id` |

## Escalado

El mismo flujo se comprime según el level. En L0 es "ejecutar → verificar → decir qué cambió"; en L4 es el diagrama completo con varios executors en paralelo. Cualquier nivel puede saltar a L5 (decisión humana). Ver la tabla de fases en `methodology/workflow.md`.

## Routing por plataforma

```
                    ¿tier adecuado a mi configuración?
                        │ sí → ejecutar
                        │ no ↓
Claude Code:   Agent(model, effort) ─── af-scout / af-worker / af-reviewer / general-purpose
Antigravity:   invoke_subagent (mismo tier: contexto/paralelismo)
               agy -p --model --effort (otro tier Gemini)
               ask-claude.sh --model --effort (Claude como executor o segunda opinión)
                        ↓
               resultado → verificar (P9) → accept / reject / retry / escalate
```

## Mapa de archivos

| Archivo | Responsabilidad única |
|---|---|
| `SKILL.md` | Disparador + bucle esencial + qué leer según la situación |
| `methodology/principles.md` | Las 12 reglas globales (fuente única) |
| `methodology/routing.md` | Ejes, decisión ejecutar/delegar, brief, estados, escalamiento, límites |
| `methodology/governance.md` | Autoridad, contratos por nivel, permisos, human gates, desviaciones |
| `methodology/quality-gates.md` | Gates, selección, evidencia, revisión independiente |
| `methodology/workflow.md` | Fases y procedimientos de Orchestrator y Executor |
| `methodology/roles.md` | Responsabilidades por rol y reparto por defecto |
| `methodology/knowledge.md` | Memoria del proyecto (`.agentforge/`) y learning loop |
| `contracts/templates/` | Formatos: task, report, agent, CONTEXT |
| `contracts/examples/` | Contratos y reporte realistas (validados por `af.py`) |
| `routing/profiles.yaml` | Único mapeo tier → modelo/esfuerzo por plataforma |
| `adapters/*/README.md` | Solo diferencias de mecanismo por plataforma |
| `adapters/claude-code/agents/` | Subagentes por función con herramientas restringidas |
| `scripts/af.py` | Comprobaciones deterministas |
| `install.sh` | Enlaces simbólicos en ambas plataformas |
| `docs/` | Por qué (decisions), cómo encaja (architecture), cómo se usa (usage) |
