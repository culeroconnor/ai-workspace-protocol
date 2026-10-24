<!-- AIWP:INICIO — bloque gestionado; no editar entre marcadores -->
## AI Workspace Protocol: adaptador de Codex (proyección, no fuente)

```yaml
protocol_id: ai-workspace-protocol
protocol_version: 1.0.2-draft
canonical_sha256: 3e7fe57d2d40848c9d96c0824efa703c72e470624dea81fc2fa961e0cc85778f
generated_at: 2026-10-23T14:27:59-03:00
target: codex
```

Complementa (no reemplaza) las demás reglas globales y el bloque N7. **No concede permisos, autonomía, sandbox ni accesos nuevos** (no cambiar `approval_policy` ni `sandbox_mode`). Si esta proyección contradice al canónico, prevalece el canónico; si un proyecto tiene reglas propias más específicas, se respetan y se reporta el conflicto (§1). El bloque N7 sigue gobernando la redacción de tareas y la espera de `OK N7`; este bloque agrega el relevo global.

### Fuentes (solo lectura desde este adaptador)
- Canónico: `<AI_SHARED_ROOT>/AI_WORKSPACE_PROTOCOL.md` (`<AI_SHARED_ROOT>` = `~/.agents/protocol/` o `%USERPROFILE%\.agents\protocol\`).
- Nivel 7: `<AI_SHARED_ROOT>/specs/NIVEL_7.md`; ante conflicto con el bloque N7, prevalece `specs/NIVEL_7.md` y se reporta.
- Esquemas: `schemas/handoff.schema.json` y `schemas/handoff-index.schema.json`.
- No escribir en `<AI_SHARED_ROOT>` salvo `runtime/` cuando una tarea lo autorice.

### Qué aplicar
- **§3 Bootstrap:** al iniciar o retomar, identificar plataforma y superficie reales (`codex` CLI/IDE/app, o tarea de ChatGPT ejecutada localmente sobre Codex), `context_mode`, raíz verificada, último handoff accesible y su vigencia, y estado de adopción.
- **Reanudación (§5.4.5):** leer `runtime/handoffs/INDEX.json`; tomar la entrada `ready` del alcance (`project_id` en modo project, `topic_id` en modo general); seguir `path`; verificar `sha256`; validar contra el esquema; contrastar Git/archivos reales; recién entonces ejecutar `next_actions`. Sin acceso a la raíz, usar el `session-state.json` del workspace. Si los niveles discrepan, prevalece el que coincide con el hash de `handoff.json`, y se reporta.
- **§4.3 Cierre:** detectar riesgo → guardar eventos → checkpoint autorizado → `handoff.json` + `handoff.md` en `runtime/handoffs/<id>/` → validar → actualizar `INDEX.json` (merge; la entrada `ready` anterior del mismo alcance pasa a `superseded`) y la clave `handoff` del `session-state.json` del workspace (merge; conservar `telemetry` y claves ajenas) → releer → informar ubicación real → recomendar sesión nueva. Sin escritura posible, entregar el handoff como texto `not_persisted`.
- **Consumo:** tras reanudar con éxito, marcar `consumed` en ambos niveles (`consumed_by: codex`, `consumed_at`).
- **§5 Handoff:** `completed` ≠ `validated` (método + evidencia). Datos no disponibles: `null`, nunca inventados.
- **§11 Estados:** `NO_CONFIGURADO | ADOPCION_TEMPORAL | CONFIGURADO_SIN_VERIFICAR | ACTIVO_Y_VERIFICADO`, siempre con el alcance verificado; no extender una verificación parcial a todo el protocolo.

### Límites explícitos
- Los hooks presentes en `config.toml` pertenecen a plugins; **ninguno es del protocolo**. No asumir `PreCompact` ni hooks propios hasta que existan y se prueben (§9).
- No fabricar porcentajes de contexto, créditos ni cuotas.
- No editar los `AGENTS.md` de `~\.codex\.chatgpt-projects\` (espejos autogenerados).
- No registrar secretos. No promover aprendizajes al perfil global ni a plantillas de gobernanza sin revisión y autorización.
- Si el hash del canónico instalado difiere de `canonical_sha256`, esta proyección está obsoleta: reportar la deriva y no actuar como si estuviera vigente.
<!-- AIWP:FIN -->
