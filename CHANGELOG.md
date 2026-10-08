# Changelog

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/); versionado semántico.

## [0.1.0] - 2026-10-07

### Added
- Metodología AgentForge: principios, routing L0-L5, roles, gobernanza, quality gates y gestión de conocimiento.
- Contratos de tarea y reportes YAML con plantillas y ejemplos.
- `scripts/af.py`: `tier`, `role`, `validate`, `check-scope` (G5) e `init` (crea `.agentforge/` con `CONTEXT.md`, `contracts/` y `reports/`).
- Interface Integrity Gate (I1-I9).
- Adaptadores para Claude Code y Antigravity.
- `install.sh` por symlinks (SSOT) con `--dry-run`, `--uninstall` y `--help`, idempotente.
- Suite de tests (`python3 -m unittest discover -s tests -v`).
- Licencia MIT (`LICENSE`) y sección de referencias técnicas y agradecimientos en `README.md`.
