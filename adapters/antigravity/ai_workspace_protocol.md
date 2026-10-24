---
protocol_id: ai-workspace-protocol
protocol_version: 1.0.2-draft
canonical_sha256: 3e7fe57d2d40848c9d96c0824efa703c72e470624dea81fc2fa961e0cc85778f
generated_at: 2026-10-23T14:09:00-03:00
target: antigravity
trigger: always_on
description: "Adaptador del AI Workspace Protocol 1.0.2-draft: bootstrap, Nivel 7, handoff y estados"
---

# AI Workspace Protocol: adaptador de Antigravity (proyección, no fuente)

Complementa (no reemplaza) las demás reglas globales. **No concede permisos, autonomía ni accesos nuevos.**
Si esta proyección contradice al canónico, prevalece el canónico; si un proyecto tiene reglas propias más específicas, se respetan y se reporta el conflicto (§1 del canónico).

## Fuentes (solo lectura desde este adaptador)
- Canónico: `<AI_SHARED_ROOT>/AI_WORKSPACE_PROTOCOL.md` (`<AI_SHARED_ROOT>` = `~/.agents/protocol/` o `%USERPROFILE%\.agents\protocol\`).
- Nivel 7: `<AI_SHARED_ROOT>/specs/NIVEL_7.md`. En caso de conflicto con `sesion_nivel7.md`, prevalece `specs/NIVEL_7.md`.
- No escribir en `<AI_SHARED_ROOT>` salvo `runtime/` cuando una tarea lo autorice. El canónico solo cambia por versión, con un único editor.

## Qué aplicar
- **§3 Bootstrap:** al iniciar o retomar, identificar plataforma y superficie reales, contexto `project|general`, raíz verificada, último handoff accesible y su vigencia, y reportar el estado de adopción. No alterar un proyecto solo para cumplir el bootstrap.
- **§4.3 Cierre:** detectar riesgo → guardar eventos → checkpoint autorizado → generar `handoff.json` + `handoff.md` → validar → informar ubicación real → recomendar nueva sesión. Sin acceso de escritura, entregar el handoff como texto marcado «no persistido».
- **§5 Handoff:** distinguir `completed` de `validated` (método + evidencia). Datos no disponibles son `null`, nunca inventados.
- **§5.4 Relevo:** `.agents/antigravity-router/session-state.json` sigue siendo el puntero de relevo local junto al índice global `runtime/handoffs/INDEX.json`. Se actualiza por merge, conservando `telemetry` y las claves desconocidas, y solo agrega o reemplaza la clave `handoff`. `checkpoint` (router) y `checkpoints` (handoff) no se fusionan. Si el proyecto tiene su propio cierre (PROJECT_BRAIN), se ejecuta además del handoff.
- **§11 Estados:** informar `NO_CONFIGURADO | ADOPCION_TEMPORAL | CONFIGURADO_SIN_VERIFICAR | ACTIVO_Y_VERIFICADO`. No declarar `ACTIVO_Y_VERIFICADO` sin prueba desde una sesión nueva (pruebas A, B y F de §12).
- **Nivel 7:** se aplica según `specs/NIVEL_7.md`. Si no se puede leer, reportar `semantics: defined_not_accessible` y no improvisar.

## Límites explícitos
- **No se asume `PreCompact`** en Antigravity. Usar solo eventos reales de la superficie y señales observables de continuidad.
- No fabricar porcentajes de contexto, créditos ni cuotas. Sin telemetría fiable, usar señales observables.
- No instalar hooks, skills, MCP ni scripts sin inspección y autorización. Los archivos de reglas orientan; el bloqueo real depende de permisos y hooks efectivamente configurados.
- No registrar secretos ni credenciales. No promover aprendizajes a `IA Conociendome` ni a `Project_Brain_Generic` sin revisión y autorización.
- Si el hash del canónico instalado difiere de `canonical_sha256`, esta proyección está obsoleta: reportar la deriva y no actuar como si estuviera vigente.
