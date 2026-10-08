# Uso

## Instalar

```bash
./install.sh --dry-run          # ver qué haría
./install.sh                    # enlaza la skill en Claude Code y Antigravity
./install.sh --claude --agents  # solo Claude Code + subagentes af-* (si no tienes scout/worker/reviewer)
```

Requiere Python 3 con PyYAML para `scripts/af.py`. En un proyecto nuevo: `python3 <AgentForge>/scripts/af.py init` crea `.agentforge/CONTEXT.md`.

## Escenarios

### 1. Tarea pequeña directa (L0)

> "Cambia el texto del botón 'Enviar' por 'Guardar' en el formulario de perfil."

El agente no escribe contrato ni línea `Route:` visible. Busca el texto, cambia una línea, comprueba que no hay otros usos que deban cambiar o tests que lo fijen, y responde: qué cambió y cómo lo verificó. Nada más.

### 2. Bug con riesgo medio, trabajando solo con Claude Code (L2)

> "Hay facturas con descuento que salen con un céntimo de diferencia."

```
Route: L2 · STANDARD · risk medium · direct + review(DEEP) — bug de cálculo, hay tests
```

Claude (sesión principal) delega a `af-scout`/FAST la búsqueda de usos de la función de redondeo, construye primero un test que reproduce el caso, corrige, ejecuta la suite y pide revisión a `af-reviewer`/DEEP sobre el diff. Reporta en el formato de [`report-l2-bugfix.yaml`](../contracts/examples/report-l2-bugfix.yaml), con el hallazgo de IVA fuera de alcance como `unexpected_findings`.

### 3. Feature con Antigravity orquestando y Claude ejecutando (L4)

> "Quiero exportar facturas a CSV desde informes, solo para administradores."

1. Antigravity pregunta solo lo que bloquea (¿qué columnas?, con su recomendación), investiga con subagentes `research`, consulta `.agentforge/decisions.md` (streaming obligatorio) y clasifica `L4 · DEEP · risk high`.
2. Escribe el contrato padre y uno por stream ([`l4-parent.yaml`](../contracts/examples/l4-parent.yaml), [`l4-stream-api.yaml`](../contracts/examples/l4-stream-api.yaml)) y los valida con `af.py validate`.
3. Lanza los streams API y UI en paralelo, cada uno en su worktree (alcances disjuntos), con `ask-claude.sh --write` y el tier de cada contrato; anota el commit de partida de cada uno.
4. Para cada resultado: lee el reporte, `git diff`, ejecuta la verificación y `af.py check-scope <contrato> --base <commit de partida>`. Rechaza o reintenta con corrección concreta si algo no cuadra.
5. Lanza el stream e2e cuando sus dependencias están DONE, pide revisión DEEP del conjunto y se detiene en el human gate antes de exponerlo en producción.

### 4. Claude recibe una tarea más difícil que su configuración

Claude corre en headless con el tier STANDARD; el contrato (con `allow_delegation: any`) pide encontrar una condición de carrera que ya resistió un intento:

```
Route: L2 · MAX · risk high · delegate(diagnóstico) — fallo previo + concurrencia
```

Claude no puede cambiar su propio modelo: lanza un subagente `general-purpose` (nivel 3, hoja) con `model`/`effort` de MAX y un brief autocontenido que incluye por qué falló el intento anterior. Recibe la hipótesis y el repro, **lo verifica él mismo** ejecutando el repro, implementa dentro del contrato y reporta la delegación en `delegations`.

### 5. Escalamiento por alcance

Durante el escenario 2, la causa resulta estar en `src/billing/tax/` (área excluida). El executor se detiene, devuelve `ESCALATE` con el repro y dos opciones con recomendación. El orchestrator decide: nuevo contrato para el equipo de impuestos o ampliar el alcance con autorización humana. Igual ocurre si un contrato con `allow_delegation: down` resulta necesitar MAX: el executor devuelve `ESCALATE` en vez de delegar hacia arriba.

## Evolucionar AgentForge

- **Nuevos modelos:** edita solo `routing/profiles.yaml` y actualiza `verified_on`.
- **Nueva plataforma:** añade `platforms.<nombre>` en `profiles.yaml` y `adapters/<nombre>/README.md` con su tabla de capacidades reales. No toques `methodology/`.
- **Nueva regla:** propónla en `docs/decisions.md` con la evidencia (reportes, fallos) y la respuesta al principio rector. Si es global, va en un solo archivo de `methodology/` y los demás la referencian.
