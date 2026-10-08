# Quality Gates

Comprobaciones que deciden si un resultado se acepta. No todas aplican siempre: se seleccionan por level y risk. Una gate superada se reporta con su evidencia (P6).

## Catálogo

| Gate | Pregunta | Evidencia aceptable |
|---|---|---|
| **G1 Acceptance** | ¿Se cumple cada criterio de aceptación, uno por uno? | Cada criterio con el comando/observación que lo demuestra. Los tests en verde no sustituyen comprobar los requisitos. |
| **G2 Functional** | ¿Funciona el flujo afectado, de punta a punta? | Ejecución real del flujo (CLI, request, UI, script) y lo observado. |
| **G3 Tests** | ¿Hay un test que falla sin el cambio y pasa con él? ¿Pasa la suite relevante? | Salida de los tests; para bugs, fail → pass del mismo repro. |
| **G4 Regression** | ¿Puede romper algo fuera de lo tocado? | Suite completa o la de los módulos que dependen de lo cambiado; búsqueda de usos de interfaces modificadas. |
| **G5 Scope** | ¿El diff contiene solo lo autorizado? | Salida de `af.py check-scope <contrato>` (en repos git); si no hay git, la lista real de archivos modificados contra `scope`. "Solo toqué X" sin esa salida no es evidencia. Artefactos generados (cachés, builds) que aparezcan se declaran, no se ignoran. |
| **G6 Contract** | ¿Se respetaron permisos, restricciones y human gates? ¿Están declaradas las desviaciones? | Rulings y deviations del reporte coherentes con el diff. |
| **G7 Architecture** | ¿Respeta las decisiones y restricciones del proyecto (`.agentforge/` y ADRs)? | Referencia a la decisión/restricción comprobada. |
| **G8 Diff review** | ¿Lo aprobaría un revisor escéptico? | Revisión independiente (ver abajo). |

## Selección

| | low | medium | high | critical |
|---|---|---|---|---|
| **L0** | G1 | G1 G3 | G1 G3 G4 G8 | G1 G3 G4 G8 + human gate |
| **L1** | G1 G5 | G1 G3 G5 | G1 G3 G4 G5 G8 | + human gate |
| **L2** | G1 G3 G5 G8 | + G4 | + G6 G7 | + human gate |
| **L3–L4** | G1 G3 G4 G5 G6 G8 | + G7 | todas | todas + human gate |

Cada celda acumula las de su izquierda en la misma fila ("+"). G3 aplica cuando hay código con comportamiento y un harness de tests; si no existe, se sustituye por la verificación red-capable más barata disponible y se dice.

G2 se añade siempre que exista un flujo ejecutable afectado y sea razonable ejercitarlo. Si una gate no se puede ejecutar (falta entorno, credenciales, runtime), se marca `not_run` con el motivo y lo que haría falta para ejecutarla; el resultado global pasa a `unverified` en ese aspecto, nunca a `pass`.

## Estándar de evidencia

- **Fresca:** ejecutada después del último cambio, no recordada.
- **Completa:** el comando entero, leyendo la salida y el código de salida, no solo la última línea.
- **Observada, no inferida:** "debería funcionar porque la lógica es correcta" no es evidencia.
- **Red-capable:** un test o comando de verificación debe ser capaz de fallar ante el defecto concreto; "se ejecuta sin errores" no basta. Los valores esperados vienen de una fuente independiente (literal, ejemplo resuelto, spec), no recalculados como lo hace el código.

## Revisión independiente (G8)

- **Revisor independiente:** un agente distinto del implementador, preferentemente tier DEEP, de solo lectura. Para L0–L1 con riesgo bajo, la autorrevisión del diff basta.
- **El revisor recibe contexto preparado**, no la historia: objetivo, contrato, criterios, y el diff (o un archivo con él). Trata el informe del implementador como afirmaciones sin verificar; las justificaciones no rebajan la severidad.
- **Dos ejes, reportados por separado** para que uno no tape al otro:
  - *Contrato:* requisitos que faltan, implementados mal, o alcance añadido.
  - *Calidad:* defectos de corrección, casos límite, seguridad, complejidad innecesaria (P3), estándares del proyecto.
- **Severidad:** `critical` (bloquea) · `important` (se corrige antes de aceptar) · `minor` (se anota en el reporte).
- **"No verificable desde el diff":** el revisor lo lista; el orquestador lo resuelve con su contexto.
- **Corrección:** el implementador corrige, no el orquestador (corregir uno mismo se salta la revisión). La re-revisión se limita al diff de la corrección y responde por hallazgo `addressed / not addressed`. Tras 2 rondas sin converger, se aplica el protocolo de escalamiento ([routing.md §6](routing.md#6-protocolo-de-escalamiento)).
- **Recepción de revisiones:** verifica cada hallazgo contra el código antes de aplicarlo; discrepa con evidencia cuando el hallazgo es incorrecto. Nada de conformidad performativa.
