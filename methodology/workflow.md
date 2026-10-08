# Workflow

De intención humana a trabajo verificado. Cada fase tiene un producto y un criterio de salida; las fases que no aportan al level de la tarea se saltan (las tareas simples siguen siendo simples).

## Fases y escalado

| # | Fase | Producto | L0 | L1 | L2 | L3 | L4 |
|---|---|---|---|---|---|---|---|
| 1 | Product intent | Objetivo, resultado esperado, fuera de alcance | · | · | ✓ | ✓ | ✓ |
| 2 | Discovery | Suposiciones explícitas; ambigüedades resueltas o escaladas | · | · | ✓ | ✓ | ✓ |
| 3 | Research | Hechos con fuente (`archivo:línea`, doc, URL) | · | ✓ | · | ✓ | ✓ |
| 4 | Architecture | Diseño mínimo + decisiones (ADR solo si cumple las 3 condiciones de [knowledge.md](knowledge.md)) | · | · | · | ✓ | ✓ |
| 5 | Decomposition | Unidades verificables con dependencias | · | · | · | ✓ | ✓ |
| 6 | Task routing | Línea `Route:` por unidad | ✓¹ | ✓ | ✓ | ✓ | ✓ |
| 7 | Contracts | Brief o contrato (ver [governance.md](governance.md#cuándo-hace-falta-un-contrato-escrito)) | · | brief | ligero | ✓ | ✓ |
| 8 | Execution | Cambios + evidencia | ✓ | ✓ | ✓ | ✓ | ✓ |
| 9 | Verification | Gates superadas ([quality-gates.md](quality-gates.md)) | ✓ | ✓ | ✓ | ✓ | ✓ |
| 10 | Review | Revisión independiente | ²  | ² | ✓ | ✓ | ✓ |
| 11 | Report | Reporte final ([`report.yaml`](../contracts/templates/report.yaml)) | breve | breve | ✓ | ✓ | ✓ |
| 12 | Learning | Aprendizajes registrados, solo si hay señal | · | · | ? | ? | ? |

¹ En L0 la línea `Route:` es mental salvo que el riesgo sea ≥ high. ² Solo si la [matriz de gates](quality-gates.md#selección) exige G8 por el riesgo. "Breve" = qué cambió + cómo se verificó, en el mensaje final.

## Procedimiento del Orchestrator

1. **Entender.** Reformula el objetivo en una frase verificable. Lista suposiciones; investiga los hechos tú (o delega la búsqueda); pregunta al humano solo las decisiones que bloquean, en una ronda, cada una con tu recomendación.
2. **Clasificar.** Emite `Route:` para la tarea completa ([routing.md §2](routing.md#2-clasifica-en-voz-alta-una-línea)).
3. **Diseñar** (L3+). La solución más simple que cumple (P3). Registra solo las decisiones difíciles de revertir.
4. **Descomponer** (L3+). Unidades que un ejecutor puede completar en un contexto fresco, cada una verificable por sí misma y preferiblemente vertical (atraviesa las capas necesarias y se puede demostrar sola). Prepara primero lo que haga fácil el cambio. Declara dependencias (`dependencies`); la *frontera* son las unidades sin dependencias pendientes. Para cambios mecánicos de gran radio, usa expand → migrate → contract en vez de cortes verticales.
5. **Enrutar.** Una línea `Route:` por unidad: tier del ejecutor, si se paraleliza, quién revisa.
6. **Contratar.** Un contrato por unidad. El contrato contiene las decisiones que el ejecutor no puede tomar solo (interfaces que consume y produce —incluido cualquier cambio de firma o de forma de datos—, restricciones globales copiadas literalmente, seams de test, criterios de aceptación), no el código. Un contrato más largo que el código que describe ya ha escrito el código. Comprueba contra el repo lo que escribes (P2): los comandos de verificación existen y se ejecutan, las rutas de `scope` son concretas y las zonas sensibles cercanas están en `excluded_areas`, el `id` es el siguiente libre en `.agentforge/contracts/`. Valida con `af.py validate`.
7. **Delegar** la frontera; en paralelo solo unidades con alcances disjuntos, cada una con escritura en su propio worktree. Anota el commit de partida de cada unidad: es el `--base` de su `check-scope`.
8. **Verificar e integrar** cada resultado (P9, [routing.md §5](routing.md#5-verificar-lo-delegado-p9)); al desbloquearse unidades, la frontera avanza.
9. **Revisar** el conjunto integrado (G8) cuando hay más de una unidad.
10. **Reportar** y, si hubo señal, **aprender** ([knowledge.md](knowledge.md#learning-loop)).

## Procedimiento del Executor

### Antes

1. Lee el contrato completo y la memoria del proyecto que referencia (`.agentforge/CONTEXT.md`, decisiones). Respeta su vocabulario.
2. Inspecciona el código afectado antes de editar. Comprueba que el contrato es coherente con lo que ves.
3. Si falta información que bloquea o el contrato se contradice con el código: `NEEDS_CONTEXT` / escala antes de empezar, no a mitad.
4. Emite tu `Route:` (puedes tener subtareas para otros tiers) y, si hay más de 2 pasos, un plan `paso → verificación`.

### Durante

- **Primero el feedback loop.** Antes de cambiar comportamiento, consigue un comando que demuestre el estado actual y pueda fallar ante el defecto o la ausencia de la funcionalidad (test, curl, CLI con fixture, script). Para bugs es obligatorio: sin un repro ejecutado al menos una vez no hay hipótesis; si no se puede construir, detente y pide acceso, artefactos o permiso para instrumentar.
- **TDD cuando aplica** (cambio de comportamiento + harness de tests): rojo → verde, un test por ciclo, en los seams que nombra el contrato (o el seam existente más alto que lo cubra). Tests por la interfaz pública; nada de tests que recalculan el resultado como el código.
- **Debugging:** reproduce → minimiza → 3–5 hipótesis falsables ordenadas ("si X es la causa, cambiar Y hará que…") → una variable por sonda → fix con test de regresión. Marca los logs temporales con un prefijo único (`[AF-DEBUG]`) para eliminarlos con una búsqueda. Si no existe un seam correcto para el test de regresión, eso es un hallazgo de arquitectura que se reporta.
- **Pasos pequeños:** typecheck/tests de archivo a menudo; suite relevante al final.
- **Alcance:** cada línea trazable al contrato (P4, P7). Decisiones menores → ruling; lo demás → [desviaciones](governance.md#desviaciones).

### Después

1. Autorrevisa el diff: ¿completo según criterios?, ¿sobra algo (P3, P4)?, ¿huérfanos que creaste?, ¿logs temporales?
2. Ejecuta las gates que tocan ([quality-gates.md](quality-gates.md#selección)) con evidencia fresca: cada `pass` del reporte cita la salida de un comando ejecutado, no tu recuerdo de lo que hiciste.
3. Entrega el reporte con `STATUS` honesto. Nunca `DONE` sin evidencia.

### Como sub-orquestador

Si el contrato lo permite (`routing.allow_delegation`) y la tarea lo justifica, el executor aplica el mismo procedimiento del orchestrator a escala local: descompone, delega a tiers adecuados, verifica e integra. Los límites estructurales de [routing.md §7](routing.md#7-límites-estructurales) se aplican igual: profundidad total, supervisión hacia abajo y propiedad del resultado.

## Handoff entre agentes

Lo que pasa de un agente a otro viaja como **punteros a archivos** (contrato, spec, reporte, diff), no como texto copiado: el receptor lee lo que necesita y el emisor no infla su contexto. El receptor devuelve `STATUS` + resumen corto + ruta del reporte.
