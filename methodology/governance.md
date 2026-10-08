# Governance: contratos, autoridad y escalamiento

Los contratos son el mecanismo central de autoridad (P8). No son prompts: son la frontera explícita de responsabilidad, alcance, permisos, criterios de éxito, verificación y escalamiento de un trabajo. Plantilla: [`contracts/templates/task.yaml`](../contracts/templates/task.yaml).

## Fuentes de autoridad (de mayor a menor)

1. **El humano** — en la conversación o en un human gate. Puede ampliar o revocar cualquier cosa.
2. **Reglas del proyecto** — `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, configuración de permisos de la plataforma. Un contrato no puede autorizar lo que estas prohíben.
3. **El contrato** de la tarea.
4. **El brief del agente padre** — nunca concede más de lo que el contrato del padre le concede a él (la autoridad solo se estrecha al delegar).
5. **Valores por defecto** de AgentForge (ver abajo).

## Cuándo hace falta un contrato escrito

| Level | Forma |
|---|---|
| L0 | Ninguna: la petición explícita del humano es la autoridad. |
| L1 | El brief de 6 líneas ([routing.md §4](routing.md#4-el-brief-todo-encargo-delegado)). |
| L2 | Contrato ligero: `id`, `level`, `risk`, `objective`, `scope`, `acceptance_criteria`, `verification`. |
| L3–L4 | Contrato completo en `.agentforge/contracts/<id>.yaml`; uno por stream en L4. |

Escribe solo los campos que aportan. Un campo vacío no es una restricción: es ruido.

## Valores por defecto (cuando el contrato no dice nada)

- **Alcance:** solo los archivos necesarios para el objetivo; nada en `excluded_areas`; nada fuera del workspace.
- **Comandos:** lectura, build, tests, linters y formateadores *en modo comprobación* están permitidos. Instalar dependencias, migraciones, cambiar configuración global, operaciones de red con efectos y cualquier operación git que publique o reescriba historia (`push`, `merge`, `rebase`, `reset --hard`, `commit` si no se pidió) requieren autorización.
- **Delegación:** según `routing.allow_delegation` ([routing.md §7](routing.md#7-límites-estructurales)); si el contrato no lo dice, `down`.

## Permisos: declarativos + mecánicos

`permissions.commands.{allow, ask, deny}` declara la intención. Donde la plataforma lo permite, el adapter la traduce a una restricción real (herramientas permitidas, modo de solo lectura, allowlist de comandos). Donde no puede, la protección es doble: el agente la respeta (P8) y la gate de alcance la comprueba después contra el diff (`scripts/af.py check-scope`). Una restricción que no se puede ni imponer ni comprobar debe reformularse para que sí se pueda.

## Human gates

Detente y pide decisión humana antes de:

1. Acciones **irreversibles o destructivas** (borrar datos, `reset --hard`, sobrescribir trabajo ajeno).
2. Cambios **sensibles para la seguridad** (auth, secretos, permisos, cifrado) cuando no estaban explícitamente en el contrato.
3. **Efectos fuera del workspace** (push, merge, publicar, desplegar, enviar mensajes, llamar APIs con efectos).
4. Un contrato o plan **tan roto que cualquier camino es una suposición**.
5. Lo que el contrato liste en `human_gates`.

Fuera de estos casos, no interrumpas: decide dentro de tu autoridad y deja constancia (ver *rulings*). Para preguntar bien: una sola ronda, solo lo que bloquea, cada pregunta con tu recomendación y el coste de equivocarse. Los hechos los investigas tú; las decisiones son del humano.

## Desviaciones

Cuando durante la ejecución aparece algo no previsto:

```
¿Se puede resolver dentro del contrato (alcance, permisos, criterios)?
 ├─ sí, y es una decisión menor  → decide y regístrala como ruling
 ├─ sí, pero cambia el enfoque   → decide, regístrala y márcala en el reporte como deviation
 └─ no                           → detente y escala (al padre o al humano) con:
                                   qué encontraste · por qué bloquea · opciones · recomendación
```

- **Ruling** (una línea en el reporte): `Ruling: <qué decidí> — <por qué> — <coste si me equivoco>`.
- **Prerrequisito grande:** si "tengo que arreglar X antes de Y" supera aproximadamente un tercio del tamaño de la tarea, es una decisión de alcance, no de implementación: escala.
- **Hallazgos fuera de alcance** (bugs ajenos, código muerto, deuda): van a `unexpected_findings` del reporte, no al diff (P7).
- **Señales de deriva de alcance:** explicar el cambio requiere la palabra "además"; se está editando un tercer grupo de archivos sin relación; el plan se ha reiniciado más de una vez.

## Reglas de escalamiento

| Desde | Hacia | Cuándo |
|---|---|---|
| Subagente | Agente padre | `ESCALATE`/`BLOCKED`: tier insuficiente, fuera de alcance, falta permiso o información. |
| Executor | Orchestrator | El contrato es ambiguo, contradictorio o insuficiente; la solución requiere ampliar alcance. |
| Cualquiera | Humano (L5) | Human gates; fallo en MAX; conflicto entre requisitos que nadie tiene autoridad para resolver. |

Escalar no es fallar: un `ESCALATE` bien fundado vale más que trabajo hecho sobre una suposición. Nadie es penalizado por escalar; sí por ocultar.

## Trazabilidad

Cada trabajo de L2+ deja: contrato (o brief) → líneas `Route:` → rulings → reporte. El `id` del contrato aparece en el reporte y, si aplica, en el mensaje de commit. Con eso cualquier agente o humano puede reconstruir *quién autorizó qué, quién lo hizo, con qué capacidad y cómo se verificó*.
