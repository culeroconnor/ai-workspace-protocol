# AI Workspace Protocol — Protocolo universal de continuidad entre IAs

> **Estado:** reconstrucción documental · **Versión de especificación:** `1.0.1-draft`  
> **ID:** `ai-workspace-protocol` · **Fecha de reconstrucción:** `2026-10-23`  
> **Base:** `1.0.0-draft` (SHA-256 `fe7ab25f…a46de843`), archivada sin cambios en `archive/1.0.0-draft/`. Cambios en §16.  
> **Procedencia:** reconstruido desde *Protocolo unificado para continuidad, handoff, cierre y aprendizaje entre ChatGPT, Claude y Antigravity* (PDF, pp. 1–25). **No es una recuperación de los bytes originales.**  
> **Implantación:** instalado como archivo en `~/.agents/protocol\`; adaptadores por plataforma pendientes (§11). Este documento no instala hooks, modifica proyectos, ejecuta scripts ni conecta plataformas por sí solo.

## 0. Propósito y alcance

Definir un contrato verificable para que ChatGPT (incluidos Projects y, cuando proceda, Codex local), Claude Code y Google Antigravity puedan iniciar, ejecutar, interrumpir, transferir y retomar sesiones sin depender exclusivamente del historial conversacional del proveedor. El protocolo se aplica a proyectos y consultas generales. Establece política de sesión, formato de handoff, trazabilidad de evidencias, criterios de cierre, privacidad, autoridad de archivos y promoción de aprendizaje. No supone que todas las plataformas comparten disco, APIs, permisos o métricas de cuota.

La regla central es **una sola fuente editable de verdad, múltiples adaptadores de carga y un estado durable externo al chat**. «Documento único» significa fuente canónica lógica, no un archivo físico directamente legible por todas las superficies.

### 0.1 Tres capas

| Capa | Responsable | Contrato |
|---|---|---|
| Política | Este `AI_WORKSPACE_PROTOCOL.md` y reglas mínimas de carga | Qué está permitido, qué fuentes prevalecen, qué conservar |
| Procedimientos | `skills/session-lifecycle/SKILL.md`, `skills/knowledge-promotion/SKILL.md` | Cómo operar el ciclo de vida y revisar lecciones |
| Estado | Runtime local futuro (JSONL + SQLite + CLI; MCP opcional) o artefactos portables explícitos | Qué cambió, qué se verificó, qué debe hacer la siguiente sesión |

**No confundir diseño con implementación.** Hasta desplegar y probar el runtime, se aplican las reglas manualmente y el nivel de activación se informa como temporal o no verificado.

## 1. Autoridad, precedencia y límites

1. Respetar primero políticas, permisos, instrucciones del usuario y controles del entorno, según su jerarquía real.
2. Respetar la autoridad propia del proyecto: `AGENTS.md`, `CLAUDE.md`, archivos `START_HERE.md`, protocolos de proyecto, especificaciones, bases de datos y políticas vigentes. La política transversal **no reemplaza** ni modifica de forma unilateral estas fuentes.
3. Cuando una regla de proyecto sea más específica, **no asumir** que este archivo la anula. Señalar contradicciones materiales y pedir decisión cuando sea necesario; no ejecutar cambios de configuración que puedan romper el proyecto.
4. Considerar los archivos de instrucciones como **orientaciones**; el bloqueo real de acciones requiere permisos del agente, sandbox, hooks de control o políticas efectivamente configurados.
5. Ningún agente debe afirmar que accedió a disco local, archivos, otros chats, histórico, métricas de tokens o cuotas cuando no hay acceso verificable.
6. En los proyectos existentes que ya tienen `PROJECT_BRAIN` y protocolos particulares, inventariar y preservarlos. No sobrescribir `AGENTS.md`, no alterar sus SQLite ni crear un segundo sistema competidor sin una migración aprobada.
7. Las herramientas y los conectores disponibles varían por cuenta, producto, plataforma y sesión. Las capacidades se detectan, no se presuponen.

### 1.1 Semántica del Nivel 7

```yaml
protocol_id: ai-workspace-protocol
protocol_version: 1.0.1-draft
default_operating_level: 7
operating_level_7_semantics: defined
operating_level_7_spec: specs/NIVEL_7.md
```

`operating_level = 7` es **un identificador de política del propietario** y no define por sí solo intensidad de razonamiento, autonomía, permisos, gasto ni acceso a herramientas. Su semántica está definida en `specs/NIVEL_7.md`, aprobada por el propietario el 2026-10-23: formato de prompt de tarea de 11 puntos, instrucciones incrementales Δ y aviso de cierre con resumen de relevo. Ninguna plataforma la amplía ni la reinterpreta. Si una superficie no puede leer la especificación, reporta `semantics: defined_not_accessible` y no improvisa. Las autorizaciones efectivas siguen intactas.

## 2. Componentes y fuentes de verdad

### 2.1 Estructura lógica recomendada

```text
<AI_SHARED_ROOT>/
├── AI_WORKSPACE_PROTOCOL.md          # único canónico editable
├── specs/NIVEL_7.md                  # semántica del Nivel 7
├── archive/                          # versiones anteriores, sólo lectura
├── schemas/
│   ├── handoff.schema.json
│   └── session-event.schema.json
├── skills/
│   ├── session-lifecycle/SKILL.md
│   └── knowledge-promotion/SKILL.md
├── adapters/                         # futuro: archivos generados, no segunda fuente
│   ├── chatgpt/
│   ├── codex/
│   ├── claude/
│   └── antigravity/
├── runtime/                          # futuro: estado no versionado públicamente
│   ├── sessions/
│   ├── handoffs/
│   └── events/
├── knowledge/
│   ├── candidates/
│   └── promoted/
├── registry/projects.json            # futuro: mapa verificado de proyectos
└── session_brain.db                  # futuro: índice derivado
```

`<AI_SHARED_ROOT>` = `~/.agents/protocol\` (decidido el 2026-10-23). Está fuera de toda raíz de proyecto y junto a `.agents/antigravity-router/`, que ya leen los agentes locales. Las proyecciones referencian esta ruta; ChatGPT cloud no la lee y recibe el contenido por copia o adjunto.

### 2.2 Artefactos portables

- **`handoff.md`:** lectura inmediata por persona o modelo.
- **`handoff.json`:** estado estructurado interoperable; validar contra `schemas/handoff.schema.json`.
- **`events.jsonl`:** journal append-only con un objeto JSON válido por línea, conforme a `schemas/session-event.schema.json`.
- **`session_brain.db`:** índice relacional/búsqueda potencialmente reconstruible desde el journal; no confundir índice con fuente exclusiva.
- **Candidatos de lección:** propuestas separadas de memorias/decisiones publicadas.

El ZIP de esta versión sólo contiene la **especificación y sus esquemas/Skills**, no la implementación de `ai-session`, bases de datos ni servidor MCP.

## 3. Bootstrap de sesión

### 3.1 Entrada obligatoria (conceptual)

1. Identificar `platform` y `surface` reales: p. ej. `chatgpt`/`chatgpt-web`, `openai`/`codex-local`, `claude`/`claude-code`, `google`/`antigravity`.
2. Registrar el nivel operativo `7` y aplicar `specs/NIVEL_7.md`.
3. Determinar `context_mode`:
   - `project`: existe un contexto de proyecto realmente identificable.
   - `general`: consulta sin raíz de proyecto; asignar `topic_id` cuando vaya a persistirse.
4. Para modo proyecto: verificar la raíz real y las fuentes de autoridad, sin inferir rutas a partir de un título; comprobar estado Git/DB/archivos cuando las herramientas estén disponibles.
5. Leer versión y hash canónico si son accesibles; si sólo hay una proyección, reportarla como tal y detectar posibles desfases.
6. Buscar **el último handoff accesible pertinente**, no un handoff imaginario.
7. Comparar objetivos, referencias y afirmaciones del handoff con el estado real. Marcar cada dato como `verified_current`, `inherited_unverified` o `not_accessible`.
8. Iniciar o registrar la sesión mediante runtime **si existe y está probado**; de lo contrario declarar `manual_or_chat_only`.
9. Comunicar brevemente estado de activación, raíz observada, handoff, limitaciones y próxima acción.

Nunca alterar un proyecto sólo para cumplir este bootstrap.

### 3.2 Diagnóstico de capacidad de inicio

```text
platform / surface                = observado, o desconocido
protocol_version / canonical_hash = observado / sin acceso
context_mode                     = project | general
project_root                     = ruta verificada o null
operating_level                  = 7 (semantics: specs/NIVEL_7.md)
last_handoff                     = ID verificado o none/unavailable
persistence                      = local-runtime | portable-files | chat-only
activation_status                = ver §11
```

## 4. Máquina de estados y deuda de continuidad

```text
BOOTSTRAP → ACTIVE ↔ WATCH → HANDOFF_READY → CLOSE_RECOMMENDED → CLOSED
```

- `BOOTSTRAP`: contexto, autoridad y handoff examinados.
- `ACTIVE`: trabajo normal, eventos y decisiones relevantes.
- `WATCH`: crece el riesgo de pérdida de contexto o discontinuidad.
- `HANDOFF_READY`: se escribieron y validaron los dos artefactos de handoff (o se identificaron explícitamente los límites de persistencia).
- `CLOSE_RECOMMENDED`: hay transferencia recuperable y razones para nueva sesión/plataforma.
- `CLOSED`: cierre observado; nunca inventar que una plataforma cerró automáticamente.

### 4.1 Señales fuertes para preparar handoff / recomendar cierre

- Solicitud del usuario de cerrar, cambiar plataforma o continuar en otro chat.
- Precompactación observada cuando la superficie exponga tal evento; degradación importante del contexto.
- Riesgo real de cuota o límite **observado**; no inferido.
- Unidad de trabajo terminada, resultado persistido y siguiente fase separable.
- Misma firma normalizada de error ≥ 3 veces sin progreso demostrable.
- Tarea siguiente exige capacidades no accesibles en la superficie actual.

### 4.2 Señales blandas / deuda de continuidad

Conversación extensa, archivos numerosos, decisiones aún dispersas, cambios de objetivo, temas mezclados o alto costo de reconstrucción. Evitar un disparador arbitrario por cantidad de mensajes.

**Parámetros sugeridos, no medidos por defecto:** si la plataforma ofrece porcentaje fiable de contexto, al ~70 % preparar/actualizar handoff y al ~85 % sugerir nueva sesión; segunda compactación puede justificar cambio. Si no hay telemetría fiable, **no fabricar porcentajes**. Priorizar hooks/eventos concretos.

### 4.3 Orden invariable del cierre

```text
detectar riesgo → guardar eventos → checkpoint autorizado si corresponde
→ generar handoff.json + handoff.md → validar contenido/evidencia/privacidad
→ informar ubicación real → recomendar nueva sesión → CLOSED (si aplica)
```

**Principio:** una sesión está lista para terminar cuando la siguiente puede continuar sin depender de la memoria conversacional previa. Si no puede escribir archivos, entregar el handoff en el chat como texto exportable e indicar que **no está persistido**.

## 5. Handoff interoperable

### 5.1 Campos requeridos del contrato

`schema_version`, `handoff_id`, `created_at`, `protocol_version`, `operating_level`, `source`, `scope`, `objective`, `status`, `completed`, `validated`, `decisions`, `files_changed`, `errors`, `risks`, `unresolved`, `next_actions`, `authority_sources`, `checkpoints`, `log_refs`, `knowledge_candidates`, `privacy`.

- `source`: plataforma, superficie, modelo y sesión de origen (datos no disponibles como `null`, no inventados).
- `scope`: `context_mode`, `project_id`, `project_root`, `git_branch`, `topic_id`; modo general nunca inventa raíz.
- `completed`: acciones realizadas, no necesariamente comprobadas.
- `validated`: **sólo afirmaciones con método y referencia a evidencia observable**.
- `decisions`: qué se decidió y por qué; distinguir decisiones del usuario de propuestas de la IA.
- `files_changed`: rutas relativas pertinentes y descripción; rutas absolutas sólo cuando son necesarias y apropiadas.
- `errors`: firma normalizada y estado de resolución, sin secretos.
- `risks` / `unresolved`: incertidumbres, bloqueos y aspectos no validados.
- `next_actions`: instrucciones ejecutables y ordenadas para retomar.
- `authority_sources` / `checkpoints` / `log_refs`: trazabilidad reproducible.
- `knowledge_candidates`: **candidatos** para revisión, no promociones automáticas.
- `privacy`: clasificación de sensibilidad, confirmación de secretos excluidos y redacciones.

### 5.2 Distinguir realizado de validado

No escribir «el firmware compila» sólo porque un agente lo dijo. Si efectivamente se ejecutó la prueba, registrar:

```json
{
  "claim": "El firmware compila",
  "method": "pio run",
  "evidence_ref": "events.jsonl#evt-204"
}
```

Ante una validación fallida, registrar en `errors` o `unresolved`; **no** convertirla en `validated`. Si la prueba era de otra sesión, comprobar su evidencia y vigencia. Cuando no haya acceso, usar `inherited_unverified` en el informe de reanudación.

### 5.3 Reanudación

- En la misma plataforma: sesión nativa recuperable **más** handoff portable **más** verificación de workspace real.
- Entre plataformas: entregar el mismo `handoff.json` y `handoff.md`; la receptora verifica estado actual y continúa desde `next_actions`.
- No aceptar ciegamente hash, rama, última prueba o credenciales heredadas.
- Si `handoff.json` está incompleto: retener lo útil, anotar campos ausentes y solicitar o reconstruir únicamente lo que la evidencia permita.

### 5.4 Integración con el checkpoint existente

`.agents/antigravity-router/session-state.json` (esquema PROJECT_BRAIN) sigue siendo el **puntero de relevo** que leen Claude Code, Codex y Antigravity. No se crea un segundo canal de relevo. Al escribir un handoff:

1. Escribir `runtime/handoffs/<handoff_id>/handoff.json` y `handoff.md` dentro de `<AI_SHARED_ROOT>`; validar el JSON contra `schemas/handoff.schema.json`.
2. Actualizar `session-state.json` por merge: leerlo antes, conservar `telemetry` y toda clave desconocida, escribir en UTF-8 y validar el JSON después. Agregar o reemplazar sólo la clave:

```json
"handoff": {
  "handoff_id": "<id>",
  "path": "runtime/handoffs/<id>/handoff.json",
  "sha256": "<hash de handoff.json>",
  "status": "ready",
  "protocol_version": "1.0.1-draft"
}
```

3. `checkpoint` (PROJECT_BRAIN) y `checkpoints` (handoff) no se fusionan: el primero es el puntero de reanudación del router; el segundo, la lista de puntos de restauración reales (commits, backups, snapshots).
4. La sesión receptora lee `session-state.json`, sigue `handoff.path` relativo a `<AI_SHARED_ROOT>`, verifica el `sha256` y recién entonces contrasta el estado real.
5. En proyectos con PROJECT_BRAIN propio, su cierre (`project_brain.py finish-task` / `close-session`) se ejecuta además del handoff, nunca en su lugar.

## 6. Logging, errores y privacidad

### 6.1 Política de eventos

Registrar hechos operativos de utilidad futura: `session_started`, `decision`, `validation`, `tool_error`, `checkpoint`, `handoff_written`, `session_closed`, `learning_candidate`, `learning_promoted` y eventos de despliegue. Emplear el esquema de evento del paquete. Añadir registros a `events.jsonl`; preservar orden temporal e identidad estable por `event_id` para deduplicación.

No grabar por defecto transcripciones completas ni contenido de prompts, tokens sensibles, API keys, contraseñas o datos privados. Conservar resúmenes, firmas de fallo, referencias y metadatos suficientes; contenido detallado sólo cuando el usuario autorice y existan controles efectivos. No copiar rutas confidenciales completas a destinos globales cuando una ruta relativa alcance.

### 6.2 Normalización de error

```text
Crudo: D:\Proyecto\src\main.cpp:381: fatal error: foo.h: No such file or directory
Firma: compiler.header_not_found:foo.h
```

El normalizador deberá eliminar partes de ruta, números de línea, timestamps y valores volátiles. Asociar intentos, solución, regresión y evidencia. La misma firma en varios proyectos sólo genera una **hipótesis de patrón**, nunca una corrección automática.

### 6.3 Concurrencia y fallos del runtime

- Registro append-only con escritura atómica o mecanismo de bloqueo cuando haya varias sesiones.
- IDs de eventos únicos e idempotencia al reintentar.
- Si SQLite falla, conservar journal y marcar inconsistencia hasta reconstrucción validada.
- El agente nunca debe declarar handoff persistido si falló la escritura o lectura de verificación.
- Backup, rotación, retención y permisos se definirán antes de procesar datos sensibles reales.

## 7. Aprendizaje: candidatos, revisión y promoción

```text
RAW EVENT → CANDIDATE LESSON → normalización y evidencia → REVIEWED LESSON
  ├─ IA Conociendome
  ├─ Project_Brain_Generic
  └─ Brain del proyecto
```

- **IA Conociendome:** preferencias de trabajo explícitas del usuario, o inferencias estables corroboradas en múltiples sesiones. No promover una preferencia inferida una sola vez.
- **Project_Brain_Generic:** patrones técnicos reproducibles y validados, errores recurrentes, fixes demostrados, scripts genéricos, anti-patrones, metodologías y arquitectura de agentes.
- **Brain del proyecto:** decisiones, rutas, datos, restricciones y pendientes propios de cada proyecto. No trasladarlos a otros proyectos de forma automática.

### 7.1 Conocimiento negativo

```yaml
lesson_type: failed_approach
problem: ...
attempt: ...
why_it_failed: ...
evidence: ...
better_approach: ...
do_not_apply_when: []
```

Toda lección tiene estado `candidate`, `reviewed`, `approved` o `rejected`, referencia de evidencia, alcance y autor de autorización. Una promoción real requiere revisión, deduplicación, control de privacidad y destino correctamente identificado. La mera redacción de este protocolo **no concede capacidad de escritura** en IA Conociendome o Project_Brain_Generic.

## 8. Git, raíces locales y seguridad operacional

Por defecto en el flujo individual de desarrollo, el **checkout local verificado** es autoridad de trabajo; un remoto de GitHub puede ser respaldo **si se ha verificado identidad y política del proyecto**. No imponer ceremonias de PR/merge ni crear ramas innecesarias. Usar commits locales breves cuando aporten recuperación, bajo las reglas propias del proyecto.

**Antes de pull/merge/reset/push**: verificar raíz con `git rev-parse --show-toplevel`, rama y HEAD, `git status`, remotos, historial y diferencias. No ejecutar `git reset --hard`, `git clean -fd`, `push --force` ni sobrescrituras destructivas como procedimiento ordinario. No realizar push, migraciones de base o modificaciones de hooks sin autorización y controles acordes con el impacto.

Los hooks/Skills/scripts descargados son código/instrucciones de terceros: inspeccionar antes de habilitar, verificar rutas, permisos, contenido y capacidad de escritura. No confiar en un aviso de un modelo como prueba de enforcement real.

## 9. Adaptadores por plataforma (proyecciones futuras)

**Contrato mínimo de cualquier adaptador generado:**

```yaml
protocol_id: ai-workspace-protocol
protocol_version: 1.0.1-draft
canonical_sha256: <SHA256_DEL_CANONICO_EN_EL_MOMENTO_DE_DESPLIEGUE>
generated_at: <ISO8601>
target: <chatgpt|codex|claude|antigravity>
```

- **ChatGPT web/cloud:** instrucciones globales mínimas + instrucciones de cada Project cuando corresponda; sin presuponer lectura de `D:\...`, hooks locales o acceso a otras conversaciones. Proyecciones actualizables manualmente y acompañadas del protocolo como fuente accesible.
- **Codex local:** `AGENTS.md` global/de proyecto según descubrimiento de la instalación; invocar CLI en hooks **sólo cuando existan y se prueben**.
- **Claude Code:** `CLAUDE.md` / `AGENTS.md` conforme a comportamiento observado; Skills para procesos; hooks de eventos compatibles tras auditoría. En Windows preferir referencias explícitas frente a symlinks como base del sistema.
- **Google Antigravity:** reglas globales/workspace/por directorio (`AGENTS.md`, `GEMINI.md`, `.agents/rules/` cuando el producto lo soporte); Skills y hooks documentados. **No asumir `PreCompact`**; usar los eventos reales (`PostInvocation`/`Stop`, según superficie) y señales de continuidad.

Una proyección puede ser obsoleta: comparar hash canónico, informar `stale_adapter_count` y generar una versión nueva sólo mediante una operación de despliegue controlada.

### 9.1 `protocol deploy` (diseño, no comando instalado)

```text
leer canónico → validar esquemas → calcular SHA-256 → generar proyecciones
→ comparar con versiones instaladas → mostrar diff → autorizar cambios
→ actualizar destinos permitidos → prueba desde sesión nueva → registrar despliegue
```

`ai-session` y `protocol deploy` son **interfaces propuestas**. No figuran como ejecutables incluidos en este ZIP. No afirmar que una IA tiene un hook activado sin evidencia de configuración y ejecución.

## 10. Runtime y MCP (hoja de ruta)

Etapas incrementales:

1. Fuente canónica + esquema + manifiesto.
2. Adaptadores locales de bajo impacto y verificación de carga.
3. Runtime compartido `ai-session` con `start`, `status`, `event`, `error`, `checkpoint`, `handoff`, `close`, `learning` y `deploy-protocol`.
4. Hooks para inicio/error/compactación/cierre **según capacidades reales de cada superficie**.
5. Proyecciones ChatGPT web/Projects.
6. Canal de candidatos y aprobación de aprendizaje.
7. Skills reutilizables instaladas mediante rutas verificadas.
8. MCP sobre el runtime ya probado, con recursos/herramientas y permisos específicos.
9. Router opcional por disponibilidad/capacidad sin depender de métricas universales de créditos.

El handoff manual debe funcionar aunque no exista MCP ni ningún router.

## 11. Estados observables de adopción

| Estado | Condición mínima |
|---|---|
| `NO_CONFIGURADO` | No se identificó fuente accesible ni proyección aplicable |
| `ADOPCION_TEMPORAL` | Se aplican instrucciones en la conversación, sin persistencia/configuración comprobada |
| `CONFIGURADO_SIN_VERIFICAR` | Existen archivos/reglas, pero aún no se probó un inicio nuevo y la recuperación |
| `ACTIVO_Y_VERIFICADO` | Sesión nueva confirmó carga/versionado; pruebas de handoff, lectura y persistencia superadas en el alcance reportado |

Un archivo creado en la sandbox de ChatGPT no prueba que esté instalado en la computadora del usuario. Registrar `verified_at`, `verified_by`, `platform` y pruebas por separado. No llamar «global» a una configuración instalada sólo en un Project.

## 12. Pruebas de aceptación mínimas

| ID | Prueba | Resultado esperado |
|---|---|---|
| A | Nueva sesión en proyecto | Detecta raíz verdadera, autoridades y Nivel 7, sin invadir archivos |
| B | Nueva consulta sin proyecto | `context_mode=general`, `topic_id` opcional, `project_root=null` |
| C | Claude → handoff → Antigravity | Receptora valida JSON, archivos/Git/DB y retoma acción siguiente |
| D | Fallo de herramienta | Evento con firma normalizada y sin secretos |
| E | PreCompact donde existe | Handoff actualizado antes de recomendar fin |
| F | Cambio del canónico | Hash/versión distintos detectan adaptador obsoleto; deploy idempotente |
| G | Dato específico de proyecto | Permanece dentro del proyecto |
| H | Patrón técnico validado | Se propone, revisa y, tras aprobación, promueve al Brain genérico |
| I | Preferencia personal aislada | No se globaliza automáticamente |

**Métricas futuras:** `handoff_success_rate`, `failed_resume_rate`, `sessions_closed_without_handoff`, `stale_adapter_count`, `recurring_error_rate`, `validated_fix_rate`, `knowledge_promotion_rate`, `false_globalization_rate`, `mean_context_at_handoff`. No emitir números sin recolección real.

## 13. Contrato mínimo de salida al cerrar una sesión

Una respuesta de cierre debe incluir:

1. Identificador de sesión/handoff realmente disponible y su ubicación (o advertencia no persistido).
2. Objetivo inicial y situación alcanzada.
3. Logros separados de pruebas y validaciones concretas.
4. Cambios de archivos y checkpoints reales, sin inventar commits.
5. Decisiones de autoridad, riesgos, errores pendientes y conflictos.
6. **Próxima acción exacta** para el siguiente agente.
7. Información necesaria para reanudar, sin secretos.
8. Candidatos de conocimiento que precisan revisión.
9. Estado del protocolo/adaptador y restricciones de la sesión receptora.

## 14. Integridad y cambios

El hash SHA-256 del archivo canónico debe calcularse **desde sus bytes reales** al desplegar, y registrarse en las proyecciones. `MANIFEST_SHA256.json` contiene los hashes de los archivos del paquete reconstruido; su propio hash se omite por autorreferencia. El hash de este documento varía si se edita una sola línea. Conservar historial de versiones, justificación de cambios y resultados de pruebas de regresión.

## 15. Referencias y alcance de evidencia

**Fuente primaria de reconstrucción:** PDF adjunto «Protocolo unificado para continuidad, handoff, cierre y aprendizaje entre ChatGPT, Claude y Antigravity», páginas 1–25; especialmente pp. 4–10 (arquitectura y estados), pp. 10–17 (handoff, journal y aprendizaje), pp. 17–22 (runtime, seguridad, implantación y pruebas), pp. 22–23 (inventario del paquete). Su descripción no contiene el texto íntegro del antiguo `AI_WORKSPACE_PROTOCOL.md` ni los bytes/hashes originales. Esta versión reconstituye **contratos y decisiones visibles**, no una identidad textual imposible de comprobar.

Fuentes de capacidades a consultar antes del despliegue real: documentación oficial de Codex `AGENTS.md`/hooks, Claude Code memoria/Skills/hooks, Google Antigravity reglas/Skills/hooks y especificación Agent Skills: <https://agentskills.io/specification>. Las capacidades, rutas y límites pueden cambiar: revalidar en la versión instalada.

## 16. Historial de cambios

| Versión | Fecha | Cambios |
|---|---|---|
| 1.0.1-draft | 2026-10-23 | Nivel 7 definido en `specs/NIVEL_7.md`; `<AI_SHARED_ROOT>` fijado en `~/.agents/protocol\`; `Proyect_Brain_Generic` corregido a `Project_Brain_Generic` (esquema de handoff 1.0 → 1.1); §5.4 integra `session-state.json` como puntero de relevo. Aprobado por el propietario. |
| 1.0.0-draft | 2026-10-23 | Reconstrucción desde el informe PDF, generada por ChatGPT. Archivada sin cambios en `archive/1.0.0-draft/`. |
