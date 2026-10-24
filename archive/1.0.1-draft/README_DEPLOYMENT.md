# README — Despliegue controlado del AI Workspace Protocol

**Paquete:** `1.0.1-draft` (base `1.0.0-draft` archivada en `archive/`) / **origen:** reconstrucción desde informe PDF, no artefactos originales.  
**Estado:** especificación validable; ninguna plataforma ni proyecto ha sido modificado o configurado por generar este ZIP.

## 1. Inventario (contrato fiel al PDF, p. 23)

```text
AI_WORKSPACE_PROTOCOL.md
README_DEPLOYMENT.md
schemas/handoff.schema.json
schemas/session-event.schema.json
skills/session-lifecycle/SKILL.md
skills/knowledge-promotion/SKILL.md
MANIFEST_SHA256.json
```

No se incluyen binarios `ai-session`, hooks instalados, archivos de proyecto ni servidores MCP.

## 2. Inspeccionar antes de desplegar (Windows / PowerShell 7)

1. Descargar el ZIP a una carpeta de confianza y **conservarlo como evidencia**, sin extraerlo encima de una carpeta existente del proyecto.
2. Extraer en una ubicación **nueva** y revisar el contenido. Ejemplo ilustrativo, adaptar las rutas realmente utilizadas:

```powershell
$Zip = Join-Path $HOME 'Downloads\AI_WORKSPACE_PROTOCOL_v1_DRAFT.zip'
$Dest = Join-Path $HOME 'Documents\AI_WORKSPACE_PROTOCOL_RECONSTRUIDO'
if (-not (Test-Path -LiteralPath $Zip -PathType Leaf)) { throw "No existe ZIP: $Zip" }
if (Test-Path -LiteralPath $Dest) { throw "El destino ya existe; elegir otra carpeta: $Dest" }
Expand-Archive -LiteralPath $Zip -DestinationPath $Dest
Get-ChildItem -LiteralPath $Dest -Recurse -File | Select-Object FullName, Length
Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $Dest 'AI_WORKSPACE_PROTOCOL.md')
```

3. Validar hashes con el manifiesto **sin escribir ni eliminar archivos**:

```powershell
$Manifest = Get-Content -Raw -LiteralPath (Join-Path $Dest 'MANIFEST_SHA256.json') | ConvertFrom-Json
foreach ($Entry in $Manifest.files) {
  $Path = Join-Path $Dest ($Entry.path.Replace('/', [IO.Path]::DirectorySeparatorChar))
  if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw "Ausente: $Path" }
  $Actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToLowerInvariant()
  if ($Actual -ne $Entry.sha256) { throw "Hash incorrecto: $Path" }
}
'Todos los hashes del manifiesto coinciden.'
```

## 3. Elegir una raíz transversal

Escoger y verificar `<AI_SHARED_ROOT>` separada de los proyectos (por ejemplo, una nueva carpeta bajo `Documents`). No reutilizar `<PROJECT_ROOT>` ni otra raíz de proyecto particular como instalación global.

Antes de conectar plataformas, inspeccionar `AGENTS.md`, `CLAUDE.md`, `START_HERE.md`, `PROJECT_BRAIN/` y protocolos ya existentes de **cada** proyecto. No sobrescribirlos. El protocolo transversal se incorpora como adaptador **mínimo** y se somete a prueba.

## 4. Adopción por plataforma: fases, no suposiciones

**ChatGPT Chat y Projects**: insertar un bootstrap compacto como Custom Instructions donde corresponda, pero recordar que Project Instructions son independientes. Adjuntar o vincular una fuente accesible al Project y probar desde un chat nuevo. Una ruta `D:\...` por sí sola no hace que el chat web acceda al disco. Reportar como `ADOPCION_TEMPORAL` si sólo se copió un prompt.

**Codex local**: después de identificar su ámbito de búsqueda real, generar una pequeña proyección a `AGENTS.md`. No reemplazar reglas existentes. Hooks sólo tras inspección de API y pruebas locales; el CLI `ai-session` aún no está disponible en este paquete.

**Claude Code**: identificar instrucciones globales y del proyecto (`CLAUDE.md` / `AGENTS.md`), instalar Skills en rutas soportadas sólo después de revisar la versión. Los hooks requieren una implementación de runtime probada antes de activarse. En Windows no depender de symlinks como mecanismo central.

**Antigravity**: verificar reglas workspace/global, `.agents/rules` y soporte real de Skills/hooks; no asumir hook `PreCompact`. Mantener reglas siempre cargadas cortas.

## 5. Validación JSON de ejemplo (Python 3.11+)

Se requiere `jsonschema` para validación contra los JSON Schemas; su uso es opcional hasta que se disponga de un entorno preparado:

```powershell
py -3.11 -m pip install jsonschema
py -3.11 -c "import json,pathlib; from jsonschema import Draft202012Validator; p=pathlib.Path(r'<RUTA_VERIFICADA_A_AI_SHARED_ROOT>'); [Draft202012Validator.check_schema(json.loads((p/'schemas'/name).read_text(encoding='utf-8'))) for name in ('handoff.schema.json','session-event.schema.json')]; print('Schemas OK')"
```

La sustitución de `<RUTA_VERIFICADA_A_AI_SHARED_ROOT>` debe efectuarse manualmente; no ejecutar un comando con un placeholder literal.

## 6. Secuencia recomendada de incorporación

1. Validar archivos y manifiesto.
2. Semántica formal de Nivel 7: hecha en 1.0.1-draft (`specs/NIVEL_7.md`).
3. Generar y comparar adaptadores mínimos por superficie.
4. Probar arranque en consulta general y proyecto (TEST A/B).
5. Transferir manualmente un handoff entre dos agentes (TEST C).
6. Construir `ai-session` y JSONL/SQLite local; sumar hooks con pruebas de regresión.
7. Evaluar MCP y router después de validar el runtime.

## 7. Seguridad y criterios de aceptación

- No sobrescribir archivos, bases de datos ni reglas de proyectos anteriores.
- No hacer force-push, reset destructivo, instalaciones silenciosas o cambios globales de hooks.
- No exportar secretos ni transcripciones completas por defecto.
- Separar `completed` de `validated` y exigir referencias reales en el segundo.
- No declarar `ACTIVO_Y_VERIFICADO` hasta verificar una sesión nueva y una continuación recuperable.

**Procedencia:** reconstrucción sustentada por las páginas 22–23 y demás secciones del PDF del usuario. No recuperar ni atribuir hashes originales al paquete reconstruido.
