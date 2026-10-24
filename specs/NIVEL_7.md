# Nivel 7 — Especificación canónica

> **protocol_id:** `ai-workspace-protocol` · **versión:** `1.0.2-draft` · **aprobada:** 2026-10-23 por el propietario  
> **Revisión de la especificación:** 3 (2026-10-23) — relevo alineado con §5.4 de 1.0.2 (índice global). Rev. 2: escalas de ejecución incorporadas desde el router. Rev. 1: versión inicial. El canónico no cambia entre revisiones de esta especificación.
> **Fuente:** `~/.claude/skills/brief-n7/SKILL.md` (SHA-256 `d80cc4cf7dbef152363e7fb6b05ade1cf7b90a86744adaea3b9b76757e28e5b4`), neutralizada por plataforma.
> **Proyecciones existentes, aún no sincronizadas con esta especificación:** `~/.claude/N7_SESION.md` y `~/.claude/skills/brief-n7/`; `~/.agents/skills/brief-n7/` (esquema de relevo obsoleto, con claves en español); `~/.gemini/config/rules/sesion_nivel7.md`; bloque N7 de `~/.codex/AGENTS.md`.

Nivel 7 no es un nivel de razonamiento, autonomía ni permisos. Es un **formato de trabajo** con tres modos:

| Modo | Cuándo | Qué se produce | Gate |
|---|---|---|---|
| Inicio | Primera tarea de una sesión nueva | Prompt de tarea N7 completo (11 puntos) | `OK N7`; hasta entonces, autonomía A0 |
| Incremental | Sesión con prompt N7 aprobado | Instrucción Δ<n> | `OK Δ<n>` sólo si cambia objetivo, autonomía, gate, arquitectura, seguridad o datos |
| Cierre | Disparador de la sección siguiente | `⚠️ CIERRE DE SESIÓN RECOMENDADO` + resumen de relevo + handoff (§5.4 del canónico) | — |

Excepción: un mensaje que empieza con `!directo`, o una pregunta puntual sin entregable ni cambios, se responde sin redactar.

## Disparadores de cierre

- Objetivo de la sesión VERIFICADO o ACCEPTED.
- Deriva: 2+ señales → consolidar; 3+ → reset. Señales: corrección repetida del mismo tipo, parche sobre parche, contradicción con una decisión tomada, error que reaparece, alcance que crece sin Δ aprobado.
- Contexto largo con degradación: por porcentaje sólo con telemetría real (hoy, únicamente el hook `session_guard.py` de Claude Code); sin telemetría, por señales observables.
- Cambio sustancial de proyecto, fase o autoridad.

No repetir el aviso por el mismo disparador; si el usuario decide seguir, continuar.

## Adaptación por superficie

| Superficie | Detección de modo | Relevo |
|---|---|---|
| Claude Code | Línea `[SESION: …]` del hook | `session-state.json` del workspace + `INDEX.json` + handoff |
| Codex, Antigravity | Historial y reglas cargadas | `session-state.json` del workspace + `INDEX.json` + handoff |
| Claude.ai | Historial; lectura y escritura por Desktop Commander cuando está disponible | `INDEX.json` + handoff; sin acceso, handoff como texto `not_persisted` |
| ChatGPT cloud | Historial | Handoff como texto o adjunto; nunca afirma persistencia |

## Escalas de configuración de ejecución (punto 5 del prompt)

Copiadas del router de Antigravity para que sean legibles desde todas las superficies. **Fuente:** `~/.gemini/config/plugins/antigravity-router-plugin-v2/skills/antigravity-router/SKILL.md`, SHA-256 `cf90a57bde7bc5e3931f0acf146054d3d0ae4fbc0090816e22038b8c048db0bc`. Si la fuente cambia, esta sección queda desactualizada hasta una nueva revisión.

**Scores de riesgo (1–5):** C = complejidad · A = ambigüedad · I = impacto · S = alcance · R = irreversibilidad. Precedencia: I > R > A > arquitectura/causa raíz > C > S > velocidad. La fuente no define descriptores por nivel: cada score se asigna por juicio y se justifica en una línea; no inventar umbrales intermedios.

| Razonamiento | Condición |
|---|---|
| LOW | Todos los scores ≤ 2 y ninguna decisión arquitectónica |
| MEDIUM | Implementación definida con riesgo bajo o moderado |
| HIGH | A ≥ 4, I ≥ 4, R ≥ 4, decisión arquitectónica o causa raíz difícil |
| DEEP | I = 5, R = 5, A = 5, decisión de producción, datos, seguridad o irreversible, o caminos de solución materialmente distintos |

| Autonomía | Alcance |
|---|---|
| A0 OBSERVE | Sólo leer y analizar |
| A1 SUGGEST | Investigar y planificar |
| A2 EDIT | Editar código o archivos locales |
| A3 EXECUTE | Comandos normales de desarrollo, tests y builds |
| A4 AUTONOMOUS | Trabajo encadenado de riesgo bajo o moderado |
| A5 HIGH-IMPACT | Acciones externas, destructivas, irreversibles, de producción, seguridad, datos o financieras. Siempre con gate, salvo política explícita del proyecto |

| Gate | Significado |
|---|---|
| OPEN | Ejecutar |
| CONDITIONAL | Ejecutar sólo dentro de límites explícitos |
| GATED | Detenerse antes de la acción con consecuencias |
| BLOCKED | No ejecutar hasta resolver el bloqueo |

Ejemplos de mapeo de la fuente: `git status` → A0 · tests/build → A3 · `git commit` → A3/CONDITIONAL · `git push` → A4 o GATED · deploy, migración o borrado destructivo → A5/GATED · navegador: leer A0/A1, probar A2/A3, acción externa A5 + GATED. Principio: a mayor consecuencia e irreversibilidad, menor ejecución autónoma. La capacidad no es autorización.

Ciclo de tarea: PLANNED → IMPLEMENTED → EXECUTED → VERIFIED → ACCEPTED. Implementado no es verificado; verificado no es automáticamente aceptado.

---

# Prompt de tarea Nivel 7 — plantilla

Reglas de redacción: español, imperativo, sin relleno. Ningún punto se omite; si no aplica, `N/A — motivo`.
No inventar rutas, archivos, APIs, valores ni resultados: lo no comprobado se marca `[HIPÓTESIS]` o se pregunta.

```markdown
# PROMPT N7 — <título corto>
Fecha: <AAAA-MM-DD> · Relevo de: <checkpoint previo | ninguno>

## 1. Identidad y proyecto
- Raíz verificada: <ruta absoluta> [VERIFICADO: cómo]
- Reglas locales: <START_HERE.md, CLAUDE.md/AGENTS.md del proyecto, otras> — leídas: sí/no
- Autoridad: <quién decide; qué decisiones quedan reservadas al usuario>
- Fase: <fase del proyecto>
- Actor propio: <plataforma/superficie: Claude Code | Claude.ai | Codex | ChatGPT | Antigravity> y su rol en esta sesión

## 2. Objetivo y alcance
- Objetivo: <una oración verificable>
- Sí incluye: …
- NO incluye (restricciones negativas): No <…>. No <…>.

## 3. Precondiciones duras
| Precondición | Cómo se comprueba | Si falla |
|---|---|---|
| <archivo/DB/estado> | <comando o lectura> | Detenerse y reportar |

## 4. Datos cerrados
Insumos permitidos (únicos): <lista de rutas/fuentes>.
Prohibido inventar rutas, APIs, valores o resultados. Lo que falte → PENDIENTE y pregunta.

## 5. Configuración de ejecución
- Fase: …
- Scores C/A/I/S/R: C=<n> A=<n> I=<n> S=<n> R=<n> (escala según reglas globales)
- Razonamiento: <DEEP | estándar> — cada superficie lo traduce a su configuración disponible (en Claude Code: Opus + razonamiento extendido alto); no inventar opciones
- Autonomía: <A0–A5>
- Gate: <OPEN | CONDITIONAL | GATED | BLOCKED> + condición de paso
- Sandbox: permisos actuales sin ampliar; modo de permisos sugerido: <plan | normal>

## 6. Taxonomía epistémica obligatoria
Toda afirmación lleva `[VERIFICADO]` (comprobado en esta sesión, con evidencia), `[DOCUMENTADO]` (consta en fuente citada), `[INFERIDO]` (deducido, con premisas) o `[HIPÓTESIS]` (supuesto a validar).
Las hipótesis nunca se persisten como estado verificado.

## 7. Sesgos propios del modelo a vigilar
Complacencia · cerrar antes de verificar · sobrealcance · confundir implementado con verificado · fabricar evidencia. Ante cualquiera, detenerse y declararlo.

## 8. Criterios de aceptación y pruebas oráculo
| Criterio | Oráculo (test / diff / log / build / medida) | Resultado esperado |
|---|---|---|

## 9. Contrato de relevo inter-agente
Al cerrar, ACTUALIZAR (merge, nunca reemplazar) `.agents/antigravity-router/session-state.json` con el esquema vigente de los proyectos PROJECT_BRAIN:
objective, phase, reasoning, scores{C,A,I,S,R}, autonomy, gate, verification{status,detail,last_error}, drift, open_decisions[], approved_plan, last_verified_state, next_step, checkpoint.
Reglas: leer el archivo antes; conservar `telemetry` (lo escriben los hooks del router) y toda clave desconocida; no poner verification.status=PASSED sin la evidencia del punto 8; UTF-8 y validar el JSON después. Si el proyecto define su cierre (project_brain.py finish-task / close-session), ejecutarlo además. Escribir también el handoff portable según §5.4 del canónico.

## 10. Autoauditoría final
Antes de cerrar, auditar el entregable contra los puntos 2, 3, 4 y 8 y reportar desvíos (o "sin desvíos" con evidencia).

## 11. Formato de salida
Español, conciso. Tabla de verificación (criterio · evidencia · etiqueta) + lista de pendientes.
```

## Instrucción incremental (sesión en curso)
```
Δ<n> · Objetivo puntual: …
Delta de alcance: + … / − … (o "sin cambio")
Etiquetado: supuestos del Δ con su etiqueta
Aceptación: evidencia que cierra el Δ
Reevaluación: no requerida | requerida (cambia objetivo/autonomía/arquitectura/seguridad/datos) → esperar OK Δ<n>
```

## Resumen de relevo (cierre)
```
⚠️ CIERRE DE SESIÓN RECOMENDADO — motivo: …
Estado verificado: …
Pendientes: …
Decisiones abiertas: …
Próximo paso: …
```
Luego escribir el checkpoint del punto 9 y, si se pide, el PROMPT N7 de la próxima sesión con "Relevo de: <ruta del checkpoint>".
