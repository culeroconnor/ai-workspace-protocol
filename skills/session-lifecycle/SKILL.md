---
name: session-lifecycle
description: Gestionar de forma verificable el inicio, vigilancia, handoff, reanudación y cierre de sesiones de IA entre ChatGPT, Codex, Claude y Antigravity.
---

# Session lifecycle — Procedimiento interoperable

> Reconstrucción desde informe PDF. Esta Skill describe un procedimiento, **no instala hooks ni ejecuta una CLI**.

## Cuándo usar

Al comenzar una sesión, recibir un handoff, cambiar de plataforma, aproximarse a compactación/límite real, sufrir errores recurrentes o terminar una unidad lógica.

## Antes de comenzar

1. Leer el canónico `AI_WORKSPACE_PROTOCOL.md` accesible y declarar su versión y hash, si se puede calcular.
2. Determinar la superficie y permisos reales. `operating_level = 7`; semántica en `specs/NIVEL_7.md` del canónico.
3. Determinar `context_mode=project|general`, raíz verificada o `null`, autoridades y límites de acceso.
4. Buscar handoff accesible sin inventar acceso a otras conversaciones o a disco: primero `runtime/handoffs/INDEX.json` de la raíz compartida, luego el `session-state.json` del workspace (§5.4).
5. Si se recupera handoff, contrastar cada resultado con los archivos, Git, base o test actuales; separar `verified_current` de `inherited_unverified`.

## Sesión activa

1. Mantener un registro selectivo de decisiones, pruebas, errores normalizados y checkpoints; no transcribir todo.
2. No escribir secretos, tokens ni datos personales innecesarios a journals o prompts.
3. Observar señales fuertes (solicitud usuario, error tres veces, PreCompact real, cuotas reales, cambio de capacidad, tarea finalizada) y deuda blanda (cambios de objetivo, complejidad, decisiones dispersas).
4. Si hay telemetría real de contexto, los umbrales sugeridos del canónico son ~70 % para preparar handoff y ~85 % para recomendar nueva sesión; no inventar esa telemetría.

## Preparar handoff

1. Guardar los eventos relevantes de modo durable **sólo si existe runtime configurado**.
2. Efectuar checkpoint de proyecto únicamente si corresponde, la raíz está verificada y el alcance está autorizado; nunca descartar trabajo.
3. Crear `handoff.json` según `schemas/handoff.schema.json` con `completed`, `validated`, decisiones, archivos, errores, riesgos, pendientes, próximos pasos, autoridades, logs, candidatos y privacidad.
4. Crear `handoff.md` **coherente** con el JSON, encabezando con objetivo, estado y una acción inmediata.
5. Comprobar que cada ítem de `validated` incluye `claim`, `method`, `evidence_ref`; bajar a `unresolved` lo no comprobado.
6. Validar esquema, vínculos a evidencia, consistencia de fechas y ausencia de secretos.
7. Reportar la ubicación real y si se verificó escritura/lectura; si no se pudo persistir, entregar texto exportable con estado `not_persisted`.
8. Sólo entonces recomendar cambiar de chat, modelo o plataforma.

## Retomar handoff

1. Leer versión/esquema; comprobar integridad y relevancia.
2. Consultar la autoridad propia del proyecto o ausencia de ella en modo general.
3. Comparar estado actual de filesystem/Git/DB/tests; nunca tratar un resumen heredado como prueba.
4. Tomar la primera acción de `next_actions` que permanezca viable.
5. Registrar divergencias observadas y preservar contenido válido de la sesión anterior.

## Salida obligatoria

`activation_status`, `platform/surface`, `operating_level=7`, `semantics`, `context_mode`, `project_root` verificada o null, fuentes, `handoff_id` o none, grado de persistencia, logros comprobados, pendientes y siguiente acción.

## Excepciones

- ChatGPT cloud no tiene necesariamente acceso al disco ni hooks; ofrecer handoff copiable o archivo adjunto generado cuando sea posible.
- Antigravity: no asumir un hook `PreCompact` si no está disponible en la instalación.
- Conflicto entre reglas o raíz insegura: detener modificaciones y describir bloqueo, sin sobrescribir instrucciones.
- No declarar `ACTIVO_Y_VERIFICADO` sin prueba end-to-end desde una nueva sesión.
