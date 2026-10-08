# AgentForge

Metodología y tooling para que agentes de IA produzcan software correcto y verificable: cada trabajo recibe el proceso, la autoridad y la capacidad cognitiva justos.

## El problema

Los agentes delegan sin límites claros, amplían el alcance, declaran éxito sin evidencia y esconden errores tras otros agentes. AgentForge impone contratos explícitos, verificación determinista y reportes honestos.

## Arquitectura y Coordinación

```text
Human (Product / Intent)
  ↓
Orchestrator (Antigravity / Architect / Quality Owner)
  ↓
Contracts (.agentforge/contracts/<id>.yaml)
  ↓
Workers (Claude Code / Implementation)
  ↓
Verification (Deterministic Tools: scripts/af.py + tests)
  ↓
Review (Independent Reviewer: af-reviewer)
  ↓
Human Acceptance
```

- `SKILL.md` — punto de entrada de la skill.
- `methodology/` — principios, routing, roles, gobernanza, quality gates, conocimiento.
- `contracts/` — plantillas (`templates/`) y ejemplos (`examples/`) de contratos y reportes.
- `routing/profiles.yaml` — mapeo tier → modelo/esfuerzo por plataforma.
- `scripts/af.py` — comprobaciones deterministas (`tier`, `role`, `validate`, `check-scope`, `init`).
- `adapters/` — diferencias de plataforma (Claude Code, Antigravity).
- `install.sh` — instalación reversible por symlinks (una sola fuente de verdad).

## Ciclo de Vida y Niveles

```text
Intent → Discovery → Research → Architecture → Decomposition → Contract → Execution → Verification → Review → Report
```

| Nivel | Nombre | Uso |
|---|---|---|
| L0 | DIRECT | Pregunta o edición trivial, sin burocracia |
| L1 | LIGHT | Cambio pequeño: «qué cambió + cómo se verificó» |
| L2 | STANDARD | Contrato de tarea escrito con scope y acceptance criteria |
| L3 | ORCHESTRATED | Orquestación con contexto desacoplado y routing dinámico |
| L4 | MULTI-STREAM | Orquestación multi-agente en streams paralelos |
| L5 | CRITICAL | Trabajo crítico de alto riesgo con human gates obligatorios |

Tiers de capacidad cognitiva: `FAST`, `STANDARD`, `DEEP`, `MAX`.
Dimensiones de riesgo: `low`, `medium`, `high`, `critical`.
Detalle completo en `methodology/routing.md` y `methodology/quality-gates.md`.

## Flujo de Trabajo

1. **Clasificar**: nivel (L0–L5), tier cognitivo, riesgo y decisión de ejecutar o delegar.
2. **Contratar**: escribir el contrato (`.agentforge/contracts/<id>.yaml`) y validar con `af.py validate`.
3. **Ejecutar**: el ejecutor opera dentro del alcance (`allowed_files`), sin tocar `excluded_areas`.
4. **Verificar**: comprobar gates (G1…G8), incluyendo `af.py check-scope` (G5) e Interface Integrity (P7).
5. **Revisar**: revisión independiente de calidad y contrato (`af-reviewer`).
6. **Reportar**: generar `.agentforge/reports/<id>.yaml` con evidencia verificable (status: DONE, DONE_WITH_CONCERNS, NEEDS_CONTEXT, BLOCKED, ESCALATE, FAILED).

## Instalación

```bash
git clone <url-del-repo> AgentForge && cd AgentForge
bash install.sh --dry-run          # ver qué haría
bash install.sh                    # enlaza la skill en ~/.claude y ~/.gemini
bash install.sh --claude --agents  # solo Claude Code + subagentes af-*
bash install.sh --help
```

Nunca sobrescribe: si el destino existe y no es un enlace a este repositorio, lo omite.

## Quickstart

```bash
python3 scripts/af.py init /ruta/a/mi/proyecto      # crea .agentforge/{CONTEXT.md,contracts,reports}
python3 scripts/af.py tier DEEP --platform claude-code
python3 scripts/af.py validate .agentforge/contracts/mi-tarea.yaml
python3 scripts/af.py check-scope .agentforge/contracts/mi-tarea.yaml
```

## Reversibilidad

```bash
bash install.sh --uninstall --dry-run
bash install.sh --uninstall
```

Solo elimina enlaces simbólicos que apuntan a este repositorio; cualquier otro archivo se deja intacto. Instalar y desinstalar son idempotentes.

## Requisitos

- Python 3 y PyYAML (`pip install pyyaml`)
- bash, git
- Claude Code y/o Antigravity

## Tests

```bash
python3 -m unittest discover -s tests -v
```

## Limitaciones conocidas

- La instalación usa symlinks: requiere un sistema de archivos que los soporte (Linux/macOS).
- `check-scope` depende de git y de que el contrato esté commiteado.
- El Interface Integrity Gate valida declaraciones en contratos y reportes, no analiza código.
- Una skill no puede cambiar el modelo de la sesión en curso; se delega mediante subagentes.

## Acknowledgements & Technical References

AgentForge fue diseñado e implementado de forma independiente, inspirándose en patrones conceptuales y arquitecturas de proyectos pioneros del ecosistema open-source:

### Metodología y Calidad de Ingeniería
- [obra/superpowers](https://github.com/obra/superpowers) (por Jesse Vincent — MIT): inspiración en el estándar de evidencia fresca antes de declarar éxito, revisión independiente en dos ejes (contrato vs calidad) y gobierno de tareas.
- [mattpocock/skills](https://github.com/mattpocock/skills) (por Matt Pocock — MIT): inspiración en el feedback loop temprano con comandos red-capable, debugging sistemático por hipótesis y restricciones de vocabulario en glosario.
- [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) (por Multica AI — MIT): inspiración en los principios fundamentales de simplicidad, cambios quirúrgicos y rigor proporcional a la tarea.

### Enrutamiento de Modelos y Delegación
- [nobodyohm-web/claude-code-model-router](https://github.com/nobodyohm-web/claude-code-model-router) (por nobodyohm-web — MIT): inspiración en la jerarquía abstracta de tiers cognitivos (`FAST`, `STANDARD`, `DEEP`, `MAX`), esfuerzo como palanca independiente y perfiles de postura.
- [BearGare/claude-skills](https://github.com/BearGare/claude-skills) (por BearGare): estudio conceptual de límites de profundidad de delegación, contención de desvío de alcance y reporte honesto de estados no verificados.
- [shaaz1000/claude-router](https://github.com/shaaz1000/claude-router) (por shaaz1000 — MIT): inspiración en la distinción entre complejidad real de la tarea y volumen de texto pegado, y vías de escalamiento explícito (`ESCALATE`).

*Nota: Todo el código fuente, scripts, plantillas de contratos y documentación de AgentForge fueron redactados e implementados originalmente. La mención de estos proyectos constituye reconocimiento técnico e intelectual, y no implica patrocinio, respaldo, afiliación ni autoría compartida.*

## Licencia

Distribuido bajo los términos de la [Licencia MIT](LICENSE).  
Copyright (c) 2026 Admes.

