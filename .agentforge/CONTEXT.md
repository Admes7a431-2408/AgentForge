# AgentForge — Context

Fuente única de verdad del lenguaje y las restricciones del proyecto AgentForge. Lo mantienen el orchestrator y el humano; los demás agentes proponen cambios en sus reportes. Formato: AgentForge `methodology/knowledge.md`.

## Glossary

**Task Contract**: Especificación declarativa en YAML (.agentforge/contracts/<id>.yaml) que define la autoridad, alcance, permisos y criterios de verificación de un trabajo.
_Evitar_: prompt, issue, ticket libre.

**Interface Integrity Gate**: Mecanismo de control que garantiza que ninguna firma pública o data shape compartido sea alterado sin estar explícitamente autorizado en el contrato.
_Evitar_: AST parser universal, compilador.

**Scope (G5)**: Delimitación física de archivos permitidos y excluidos comprobada deterministamente mediante git diff.
_Evitar_: scope semántico sin verificación de diff.

**Gate Result**: Estado de evaluación de una quality gate: pass, fail, not_run.
_Evitar_: success, ok, pending.

## Constraints

- Ningún cambio puede romper la compatibilidad de AgentForge entre Claude Code y Antigravity.
- Ninguna regla global debe duplicarse entre archivos de metodología; solo en principles.md.
- La instalación real de AgentForge está estrictamente prohibida hasta que la misión concluya con auditoría favorable.
- Las tareas L0 y L1 deben permanecer ligeras sin burocracia obligatoria.

## Pointers

- Metodología: `methodology/`
- Contratos: `contracts/`
- Tooling determinista: `scripts/af.py`
- Decisiones arquitectónicas: `docs/decisions.md`
