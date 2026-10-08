# Knowledge: lenguaje compartido y learning loop

Separa dos memorias que nunca se mezclan:

- **La metodología** (este repositorio AgentForge): cómo se trabaja. Igual para todos los proyectos.
- **La memoria del proyecto** (`.agentforge/` en la raíz de cada proyecto): qué significa cada cosa *en ese proyecto*, qué se decidió y qué no se puede romper. Es la fuente única de verdad que cualquier agente lee al empezar y que sobrevive a las conversaciones (P12).

## Estructura en el proyecto

```
<proyecto>/.agentforge/
├── CONTEXT.md        # glosario, términos de dominio y restricciones importantes
├── decisions.md      # decisiones de arquitectura (ADR breves)
├── learnings.md      # aprendizajes del proceso en este proyecto (opcional)
├── contracts/        # contratos L2+ (<id>.yaml)
└── reports/          # reportes finales (<id>.yaml)
```

Se crea perezosamente: cada archivo nace cuando hay algo que poner en él. Si el proyecto ya tiene equivalentes (`GLOSSARY.md`, `docs/adr/`, `CONTEXT.md`), **no se duplica**: `CONTEXT.md` contiene solo un puntero a ellos. Plantilla: [`contracts/templates/CONTEXT.md`](../contracts/templates/CONTEXT.md).

## CONTEXT.md

Tres secciones, cada entrada de una o dos líneas:

- **Glossary** — términos propios del proyecto y del dominio (PROJECT_GLOSSARY + DOMAIN_TERMS). Formato: `**Término**: qué ES (no qué hace). _Evitar_: sinónimos`. Una palabra por concepto; sin conceptos generales de programación; sin detalles de implementación.
- **Constraints** — restricciones importantes que ningún cambio puede romper (IMPORTANT_CONSTRAINTS), cada una con su motivo.
- **Pointers** — dónde viven otras fuentes de verdad (specs, ADRs externos, glosario existente).

Reglas de uso:

- Todo agente lo lee antes de diseñar o implementar en L2+ y usa sus términos en código, contratos y reportes.
- Si el humano o un documento usa un término que contradice el glosario, se señala; no se adopta en silencio.
- **Quién escribe:** el orchestrator o el humano. El executor *propone* altas o cambios en `unexpected_findings` del reporte (salvo que su contrato lo autorice).

## decisions.md (ARCHITECTURAL_DECISIONS)

Registra una decisión solo si se cumplen las tres: **difícil de revertir**, **sorprendente sin contexto** y **con un trade-off real**. Formato:

```
## AD-007 — <título> (2026-10-07, accepted)
Contexto: <una o dos frases>. Decisión: <qué>. Alternativas descartadas: <cuáles y por qué>. Consecuencias: <qué implica>.
```

Una decisión se reemplaza con otra nueva (`superseded by AD-012`), nunca se reescribe.

## Learning loop

No es una retrospectiva obligatoria. Se activa solo con una **señal**:

- Un subagente o tier falló y hubo que escalar.
- Una gate detectó un defecto que el proceso debió prevenir.
- Hubo una desviación del contrato o un permiso incorrecto (faltó o sobró).
- El humano corrigió el enfoque, el alcance o la ruta.
- El proceso se sintió claramente pesado o claramente insuficiente para la tarea.

Ante una señal, el reporte incluye `learnings` con: qué funcionó · qué falló · qué regla faltó · qué permiso fue incorrecto · qué parte del contrato sobró · qué fue demasiado pesado · qué se podría automatizar. Una línea por punto; omite los vacíos.

**Destino del aprendizaje** (el más local que sirva):

| Alcance | Dónde | Quién decide |
|---|---|---|
| Este proyecto | `.agentforge/learnings.md`, `CONTEXT.md` o reglas del proyecto | Orchestrator / humano |
| Mapeo de modelos | `routing/profiles.yaml` de AgentForge | Humano |
| La metodología | Propuesta en `docs/decisions.md` de AgentForge, con la evidencia | Humano |

Los agentes **proponen** cambios a la metodología; nunca la editan como efecto secundario de una tarea. Una regla nueva entra solo si responde "sí" al principio rector: ¿produce software más correcto, verificable y mantenible con menos errores, menos desperdicio de contexto y menos intervención humana innecesaria?
