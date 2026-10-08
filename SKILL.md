---
name: agentforge
description: Usar al recibir una tarea de desarrollo de software no trivial (feature, bug, refactor, migración, investigación de código, diseño), al planificar o descomponer trabajo, al decidir si ejecutar directamente o delegar en subagentes y con qué modelo o esfuerzo, al escribir o ejecutar un contrato de tarea (.agentforge/contracts/*.yaml), al revisar o aceptar trabajo de otro agente, o cuando el prompt diga "usa agentforge". No usar para preguntas puras ni ediciones triviales de una línea.
---

# AgentForge

Metodología para que agentes de IA produzcan software correcto y verificable: cada trabajo recibe **el proceso justo, la autoridad justa y la capacidad cognitiva justa**, y ningún agente puede ocultar un error detrás de otro.

## Bucle esencial (todas las tareas)

1. **Clasifica** la tarea en tres ejes independientes y decláralo en una línea (en L0 de riesgo bajo basta hacerlo mentalmente; [routing.md](methodology/routing.md)):
   `Route: <L0–L5> · <FAST|STANDARD|DEEP|MAX> · risk <low|medium|high|critical> · <direct|delegate|parallel> — <por qué>`
2. **Decide ejecutar o delegar** (§3 de routing): delega lo que consume contexto sin exigir razonamiento, lo que necesita otro tier y lo independiente; lo pequeño se hace directamente.
3. **Trabaja dentro de tu autoridad**: el contrato (o la petición explícita en L0) define alcance y permisos ([governance.md](methodology/governance.md)).
4. **Verifica con evidencia** las gates que tocan ([quality-gates.md](methodology/quality-gates.md)); lo delegado también: el resultado sigue siendo tuyo.
5. **Reporta** con estado honesto ([`report.yaml`](contracts/templates/report.yaml)); en L0–L1 basta "qué cambió + cómo se verificó".

Los principios que gobiernan todo lo anterior están en [principles.md](methodology/principles.md): P1 piensa antes de programar · P2 no asumas · P3 simplicidad · P4 cambios quirúrgicos · P5 orientado al objetivo · P6 verifica antes de declarar éxito · P7 no amplíes el alcance · P8 capacidad ≠ autoridad · P9 el orquestador es dueño del resultado · P10 enruta la tarea, no el agente · P11 delega cuando el contexto es más caro que el pensamiento · P12 nada crítico vive solo en una conversación. Léelo una vez por sesión.

## Qué leer según la situación

| Situación | Lee |
|---|---|
| Cualquier tarea L1+ | [principles.md](methodology/principles.md), [routing.md](methodology/routing.md) |
| Vas a orquestar (L3–L4) o a ejecutar un contrato | [workflow.md](methodology/workflow.md) (tu procedimiento), [roles.md](methodology/roles.md) |
| Escribes o interpretas un contrato; algo se sale del alcance | [governance.md](methodology/governance.md), [`task.yaml`](contracts/templates/task.yaml), [ejemplos](contracts/examples/) |
| Vas a aceptar trabajo (propio o delegado) | [quality-gates.md](methodology/quality-gates.md) |
| El proyecto tiene `.agentforge/` o aparece vocabulario/decisiones a conservar | [knowledge.md](methodology/knowledge.md) |
| Necesitas el mecanismo concreto de tu plataforma | [Claude Code](adapters/claude-code/README.md) · [Antigravity](adapters/antigravity/README.md) |
| Necesitas el modelo/esfuerzo de un tier | `python3 scripts/af.py tier <TIER> --platform <claude-code\|antigravity>` ([profiles.yaml](routing/profiles.yaml)) |

L0 no requiere leer nada más que esta página. Si el proyecto tiene `.agentforge/CONTEXT.md`, léelo antes de diseñar o implementar en L2+.

## Herramienta

`scripts/af.py` (rutas relativas a esta skill): `tier` / `role` (mapeo de modelos), `validate` (estructura de contratos y reportes), `check-scope` (gate G5 contra el diff de git), `init` (crea `.agentforge/` en un proyecto).
