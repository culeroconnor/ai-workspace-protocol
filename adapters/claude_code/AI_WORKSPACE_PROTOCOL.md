---
protocol_id: ai-workspace-protocol
protocol_version: 1.0.2-draft
canonical_sha256: 3e7fe57d2d40848c9d96c0824efa703c72e470624dea81fc2fa961e0cc85778f
generated_at: 2026-10-23T17:19:39-03:00
target: claude-code
---

# AI Workspace Protocol: adaptador de Claude Code

Proyección del canónico; complementa Nivel 7 sin sustituirlo. No concede permisos.

## Fuentes y descubrimiento
- Raíz compartida fija: `~/.agents/protocol/`.
- Canónico: `~/.agents/protocol/AI_WORKSPACE_PROTOCOL.md`.
- Nivel 7: `~/.agents/protocol/specs/NIVEL_7.md`; prevalece ante divergencias con la proyección local, que deben reportarse.
- Índice global: `~/.agents/protocol/runtime/handoffs/INDEX.json`.
- Esquemas: `schemas/handoff.schema.json` y `schemas/handoff-index.schema.json`, relativos a la raíz compartida.

## Aplicación
- Bootstrap: identificar plataforma/superficie reales, context_mode y raíz; contrastar reglas y Git. Leer canónico y comprobar su hash contra el encabezado. Ante deriva, informar y detener cambios hasta aclararla.
- Reanudación: descubrir INDEX.json desde este adaptador sin exigir al usuario la ruta. Elegir la única entrada ready del alcance: project_id en proyecto o topic_id en modo general. Seguir path bajo runtime/handoffs, verificar SHA-256, validar JSON contra esquema y contrastar archivos/Git antes de next_actions. Si falta acceso global, usar el puntero local `.agents/antigravity-router/session-state.json`.
- Si los punteros discrepan, prevalece el que coincide con el hash real; reportar divergencia. No reutilizar silenciosamente entradas consumed.
- Respetar el gate Nivel 7 antes de acciones con efectos. Al consumir con éxito, actualizar por merge status=consumed, consumed_by=claude-code y consumed_at real en la entrada del índice y la clave handoff local; releer y verificar. Preservar telemetry, claves ajenas y handoff.json (su hash permanece estable).
- Cierre: eventos y checkpoint cuando correspondan, handoff.json + handoff.md, validación, actualización de índice/puntero por merge, relectura e informe. Ejecutar además el cierre PROJECT_BRAIN si el proyecto lo define. Sin permisos, reportar not_persisted.
- Conservar el esquema local existente (§5.5); no migrar ni normalizar scores/gates en silencio. completed no equivale a validated; cada validación requiere método y evidencia.
- Informar adopción NO_CONFIGURADO, ADOPCION_TEMPORAL, CONFIGURADO_SIN_VERIFICAR o ACTIVO_Y_VERIFICADO exclusivamente para el alcance probado.
- No cambiar hooks, permisos, sandbox, canónico o memorias por cumplir el bootstrap. No asumir PreCompact ni runtime ai-session instalado. No registrar secretos. Promoción de conocimiento sólo con revisión y autorización explícita.
