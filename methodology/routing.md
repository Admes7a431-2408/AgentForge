# Adaptive Routing & Delegation

Cómo cualquier agente decide **cuánto proceso** aplica, **qué capacidad cognitiva** usa y **si ejecuta o delega**. Se aplica igual a Antigravity, Claude Code o cualquier agente futuro; las diferencias de mecanismo están en `adapters/` y el mapeo a modelos concretos en [`routing/profiles.yaml`](../routing/profiles.yaml).

## 1. Tres ejes independientes

No confundas tamaño, dificultad y consecuencia. Una tarea puede ser fácil y crítica (cambiar una variable de producción) o difícil e inocua (un prototipo desechable).

| Eje | Pregunta | Valores | Qué decide |
|---|---|---|---|
| **Level** | ¿Cuánta coordinación requiere? | L0–L5 | Fases del workflow, forma del contrato, número de agentes |
| **Tier** | ¿Cuánta capacidad de razonamiento exige *esta* (sub)tarea? | FAST · STANDARD · DEEP · MAX | Modelo + esfuerzo del agente que la ejecuta |
| **Risk** | ¿Qué cuesta equivocarse? | low · medium · high · critical | Quality gates, revisión independiente, human gates |

### Level — escala de escalamiento

| Level | Nombre | Cuándo | Mínimo exigido |
|---|---|---|---|
| L0 | DIRECT | Cambio pequeño, claro, local. | Ejecutar + verificar (P6). Sin contrato escrito. |
| L1 | SPECIALIST | Requiere conocimiento o herramienta específica (un dominio, una búsqueda amplia). | Brief autocontenido al especialista; el padre verifica. |
| L2 | REVIEWED | Cambio de comportamiento no trivial (varios archivos, lógica nueva, API visible). | Contrato ligero + implementación + revisión independiente. |
| L3 | ORCHESTRATED | Requiere investigar y diseñar antes de implementar. | Research → architecture → contrato completo → ejecución → revisión. |
| L4 | MULTI-STREAM | Varias subtareas independientes que conviene paralelizar. | L3 + descomposición con dependencias + un contrato por stream + integración. |
| L5 | HUMAN DECISION | La decisión no es técnica o excede la autoridad del agente. | Presentar opciones con recomendación y coste; esperar decisión. |

L5 no es "más grande que L4": es un *estado* al que cualquier nivel puede saltar cuando aparece una decisión que pertenece al humano.

### Tier — capacidad cognitiva (abstracta)

| Tier | Para qué | Ejemplos |
|---|---|---|
| FAST | Trabajo mecánico o de lectura con especificación completa; cero juicio de diseño. | Buscar usos, localizar archivos, renombrar, aplicar una plantilla, ejecutar un comando conocido y resumir. |
| STANDARD | Implementación normal dentro de un patrón conocido. | Feature acotada, tests, refactor en patrón, investigación con alcance. |
| DEEP | Razonamiento difícil pero bien planteado. | Bug sutil multiarchivo, arquitectura con respuesta conocible, revisión crítica, contratos de L3+. |
| MAX | Alta incertidumbre, novedad o fallo previo de DEEP. | Diseño abierto sin patrón, causa raíz que ya resistió un intento, decisiones con muchas restricciones acopladas. |

**Esfuerzo antes que modelo.** Dentro de un tier, el esfuerzo es la palanca más barata: sube el esfuerzo (±1) antes de subir de modelo, y bájalo cuando la tarea es "rápida aunque difícil". Cada plataforma mapea tier → (modelo, esfuerzo) en `profiles.yaml`; ningún otro archivo nombra modelos concretos.

### Risk

| Risk | Señales |
|---|---|
| low | Local, reversible, cubierto por tests, sin datos ni usuarios afectados. |
| medium | Cambia comportamiento visible, toca varios módulos o código sin tests. |
| high | Seguridad, autenticación, dinero, datos persistentes, migraciones, APIs públicas, concurrencia. |
| critical | Irreversible o con efecto fuera del workspace: borrar datos, producción, publicar, push/merge, secretos. |

`high` y `critical` activan gates adicionales (ver [quality-gates.md](quality-gates.md)) y `critical` exige human gate (ver [governance.md](governance.md#human-gates)).

## 2. Clasifica en voz alta (una línea)

Antes de trabajar en cualquier tarea no trivial, declara la ruta en una sola línea; es la traza mínima y permite al humano corregirla:

```
Route: L2 · STANDARD · risk medium · direct + review(DEEP) — cambia validación de pagos, hay tests
```

**Trinquete.** El nivel y el riesgo pueden subir durante la tarea cuando aparece evidencia (complejidad oculta, fallo, alcance mayor); se anuncia con una nueva línea `Route:`. No se bajan en silencio. Ante la duda sobre el **riesgo**, elige el más alto; ante la duda sobre el **tamaño**, empieza ligero y deja que la evidencia lo suba. Así las tareas simples siguen siendo simples sin esconder las peligrosas.

## 3. ¿Ejecutar o delegar?

Cada agente, al recibir trabajo (incluido un subagente que recibe un brief), recorre:

```
1. ¿Mi configuración actual (tier) es adecuada para esta (sub)tarea?
     sí → candidata a ejecución directa
     no → la parte que lo requiere se delega al tier adecuado (más alto o más barato)
2. ¿Hay subtareas que consumen mucho contexto y poco razonamiento?    → delegar a FAST (P11)
3. ¿Hay subtareas independientes entre sí?                             → paralelizar
4. ¿La matriz de gates exige revisión independiente (G8)?             → delegar a un revisor
5. Todo lo demás → ejecutar directamente
```

### El balance de costes

| Coste | Qué es | Sube cuando… |
|---|---|---|
| `delegation_cost` | Escribir un brief autocontenido, arrancar el agente, leer su resultado y verificarlo. | La tarea depende de mucho contexto de la conversación; el brief sería tan largo como hacerla. |
| `context_cost` | Tokens y atención que la tarea consumiría en el agente actual. | Hay que leer muchos archivos, logs o resultados intermedios que luego no importan. |
| `reasoning_cost` | Dificultad cognitiva; riesgo de hacerlo mal con el tier actual. | Ambigüedad, muchas restricciones acopladas, fallos previos. |

Delega cuando `context_cost` o el desajuste de `reasoning_cost` superan claramente a `delegation_cost`. Reglas prácticas:

- **Directo:** cabe en unos pocos pasos; es una continuación ("sí, adelante", "sigue") que depende del contexto acumulado; el contenido pegado es grande pero la pregunta es simple (contenido pegado ≠ complejidad).
- **Delegar hacia abajo (más barato):** búsquedas amplias, inspección de muchos archivos, ediciones repetitivas ya decididas, ejecutar y resumir comandos largos. Agrupa ediciones pequeñas del mismo tipo en un solo encargo.
- **Delegar hacia arriba (más capaz):** cuando el tier actual no basta y la plataforma no permite cambiar el modelo de la sesión principal, *si tu autoridad lo permite* (ver §7). Nunca dependas de hacks para cambiar el modelo de la sesión: la delegación es el mecanismo portable.
- **Paralelizar:** solo subtareas sin estado compartido. Si varias editan código, cada una trabaja en su propio worktree (o rama) con alcances disjuntos; así cada resultado se verifica por separado (`check-scope` mide todo el árbol de trabajo).

## 4. El brief (todo encargo delegado)

Un subagente no ve tu conversación (P12). El encargo es autocontenido y usa *punteros* (rutas a archivos, contratos, specs) en lugar de copiar contenido. Para L0–L1 basta este bloque; para L2+ el brief apunta a un contrato (`contracts/templates/task.yaml`).

```
Objetivo: <una frase verificable>
Contexto: <dónde encaja; rutas a leer; contrato si existe>
Alcance: <qué puede tocar / solo lectura>
Hecho cuando: <criterio de aceptación y cómo comprobarlo>
Devuelve: STATUS + <formato y longitud máxima de la respuesta>
Si es más difícil, ambiguo o mayor de lo descrito: detente y devuelve ESCALATE con el motivo.
```

**Protocolo de estado** (primera línea de toda respuesta delegada):

| Status | Significado | Acción del padre |
|---|---|---|
| `DONE` | Hecho y verificado según el brief. | Verificar evidencia (P9) y aceptar o rechazar. |
| `DONE_WITH_CONCERNS` | Hecho, con dudas explícitas. | Resolver las dudas antes de aceptar. |
| `NEEDS_CONTEXT` | Falta información concreta. | Aportarla y reanudar (mismo agente). |
| `BLOCKED` / `ESCALATE` | No puede o no debe seguir (tier insuficiente, fuera de alcance, sin permisos). | Añadir contexto, dividir, subir tier o escalar al humano. Nunca reintentar igual. |
| `FAILED` | Lo intentó y no lo consiguió; adjunta la evidencia del fallo. | Protocolo de escalamiento (§6). |

Este es el único vocabulario de estados: lo usan las respuestas delegadas y el campo `status` de los reportes.

## 5. Verificar lo delegado (P9)

```
resultado → ¿la evidencia respalda el STATUS? → ¿cumple el criterio "hecho cuando"? → ¿respeta el alcance?
   todo sí → accept
   corregible con poco contexto → retry (mismo agente, con la corrección concreta)
   mal enfocado / tier insuficiente → escalate (ver §6)
   inaceptable o fuera de autoridad → reject y reportarlo
```

Verificar no es releer el informe: es mirar el diff, ejecutar o reejecutar la comprobación, o leer los `archivo:línea` citados. El coste de la verificación se ajusta al riesgo: para FAST de solo lectura basta comprobar por muestreo algunas citas; para cambios de código, diff + criterio de aceptación.

## 6. Protocolo de escalamiento

1. **No reintentes el mismo tier sin cambios.** Si un intento falló, cambia algo: más contexto, tarea más pequeña, más esfuerzo o tier superior.
2. **Esfuerzo antes que modelo:** primero +1 de esfuerzo en el mismo tier si el problema es "le faltó pensar"; sube de tier si le faltó capacidad.
3. **Diagnostica antes de rehacer:** el tier superior empieza explicando por qué falló el intento anterior; no recorre el mismo camino con un modelo mayor.
4. **Recuerda el tier que funcionó** para esa clase de tarea durante el resto de la sesión.
5. **Límite de bucle:** tras 2 ciclos de corrección fallidos sobre lo mismo, sube de tier; tras fallar en MAX, pasa a L5 (decisión humana) con lo aprendido.

## 7. Límites estructurales

- **FAST nunca orquesta** ni integra resultados de otros agentes: un modelo pequeño agrega mal y sus errores cuestan retrabajo.
- **Como máximo tres niveles.** Nivel 1 es el agente que recibe la tarea del humano; cada delegación suma uno, también un handoff entre plataformas. Ejemplo: Antigravity (1) → Claude Code headless (2) → subagente de Claude (3). El nivel 3 es siempre hoja.
- **Autoridad para delegar** (`routing.allow_delegation` del contrato): `none` = hoja, no delega; `down` = solo a tiers iguales o inferiores; `any` = también a tiers superiores para una porción concreta. Sin contrato (tarea directa del humano) equivale a `any`. Un agente sin autoridad suficiente que necesita más capacidad no se auto-escala: devuelve `ESCALATE` y el padre decide.
- **Delegar arriba no es ceder el mando:** un tier superior puede recibir *la porción más difícil* (un diagnóstico, un diseño), pero la coordinación, la integración y la verificación se quedan en quien tiene el contexto completo.
- **Descomposición e integración viven arriba:** el orquestador divide y une; los workers reciben porciones del tamaño de su tier.
- **Especifica siempre el tier al delegar.** Omitirlo hereda la configuración (a menudo la más cara) de la sesión.
- **El número de turnos pesa más que el precio por token:** un tier demasiado barato para trabajo descrito en prosa tarda tanto que sale más caro. Usa FAST solo cuando la especificación es completa.
