# Roles

Un rol es un sombrero, no una identidad: define responsabilidades y autoridad, no un modelo ni una plataforma (P10). Cualquier agente puede llevar cualquier rol si su contrato se lo asigna; abajo se indica el reparto por defecto. Para declarar un especialista nuevo usa [`contracts/templates/agent.yaml`](../contracts/templates/agent.yaml).

## Human — Product Owner y autoridad final

Define la intención y las prioridades; decide en los human gates y en L5; aprueba cambios a la metodología. No debería tener que responder preguntas de hecho que un agente puede investigar.

## Intent — refinamiento de la intención (por defecto: GPT u otro asistente conversacional)

Convierte una idea en un objetivo con problema, resultado esperado, restricciones conocidas y fuera de alcance. Opcional: si el objetivo ya llega claro, se salta. Entrega texto, no contratos.

## Orchestrator / Architect (por defecto: Antigravity)

CTO + arquitecto + engineering manager. Responsable de que el trabajo correcto se haga con la autoridad y capacidad correctas.

- Comprende el objetivo, detecta ambigüedades y clasifica la tarea (level, tier, risk).
- Investiga y analiza el contexto (delegando exploración cuando sale más barato, P11).
- Diseña la solución y la descompone en unidades verificables con dependencias.
- Decide qué se paraleliza, qué especialistas hacen falta y con qué tier.
- Escribe contratos: alcance, permisos, criterios de aceptación, verificación, human gates.
- Delega, supervisa por resultados (no microgestiona pasos), verifica, integra y reporta.
- Mantiene la memoria del proyecto (`.agentforge/`) y decide qué aprendizajes se registran.

**No hace:** implementar lo que ha delegado a la vez que el ejecutor, corregir él mismo los hallazgos de una revisión, ni dictar el *cómo* donde el contrato puede dictar el *qué* y el criterio.

## Executor (por defecto: Claude Code)

Implementation engineer + debugger + tester + sub-orquestador cuando la tarea lo justifica.

- Ejecuta un contrato (o una petición L0) dentro de su alcance, con feedback loops cortos.
- Aplica el procedimiento de ejecución de [workflow.md](workflow.md#procedimiento-del-executor).
- Puede delegar subtareas a otros tiers (búsqueda, cambios mecánicos, revisión) siguiendo [routing.md](routing.md); sigue siendo dueño del resultado (P9).
- Propone, no edita, cambios a la memoria compartida del proyecto (glosario, decisiones), salvo que el contrato lo autorice.

**No hace:** ampliar el alcance, cambiar criterios de aceptación ni decidir lo que pertenece al orquestador o al humano. Escala.

## Specialist

Agente con un dominio o herramienta concreta (seguridad, base de datos, frontend, investigación documental, exploración de repositorio). Recibe un brief o contrato estrecho, devuelve resultado + evidencia + `STATUS`. Es una hoja: no delega salvo autorización explícita.

## Reviewer

Revisor independiente y escéptico de un diff, contrato o diseño. Solo lectura. Aplica [quality-gates.md → G8](quality-gates.md#revisión-independiente-g8). Nunca es el mismo agente que implementó lo revisado.

## Reparto por defecto y alternativas

| Situación | Orchestrator | Executor |
|---|---|---|
| Flujo normal | Antigravity | Claude Code (headless, vía contrato) |
| El humano trabaja directamente con Claude Code | Claude Code (sesión principal) | Subagentes de Claude Code |
| El humano trabaja directamente con Antigravity en una tarea L0–L2 | Antigravity | Antigravity mismo o sus subagentes |
| Segunda opinión de otro proveedor | El que esté orquestando | El otro, en modo solo lectura como Reviewer |

Los mecanismos concretos (cómo se lanza cada agente, cómo se imponen permisos) están en `adapters/`.
