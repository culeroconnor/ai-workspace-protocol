# AI Workspace Protocol — Runtime CLI (`tools/`)

Herramienta de referencia para la operación estandarizada del **AI Workspace Protocol (AIWP)**.  
Permite a cualquier asistente (Google Antigravity, Anthropic Claude Code, OpenAI Codex, ChatGPT) o usuario operar el ciclo de vida del protocolo en una sola línea de comando sin recurrir a scripts ad-hoc.

---

## 1. Archivos Disponibles

- **`ai_protocol.py`**: Motor CLI en Python 3.10+ (utiliza la librería estándar y `jsonschema`).
- **`ai-protocol.ps1`**: Wrapper para PowerShell 7 / Windows PowerShell.

---

## 2. Comandos Principales

### 2.1 Diagnóstico de Inicio (§3)
Examina plataforma, modo de contexto, rama/HEAD de Git, versión y hash canónico, estado de adaptadores y último handoff:
```powershell
python python tools/ai_protocol.py status
# O con salida estructurada JSON:
python python tools/ai_protocol.py status --json
```

### 2.2 Verificación de Integridad (§14)
Contrasta los archivos canónicos contra `MANIFEST_SHA256.json` y valida que los esquemas JSON y el índice global cumplan el estándar Draft 2020-12:
```powershell
python python tools/ai_protocol.py verify
```

### 2.3 Gestión de Adaptadores (§9)
Verifica el estado y calcula posibles derivas de hash en los adaptadores instalados en la máquina:
```powershell
python python tools/ai_protocol.py adapters check
```
Actualiza o despliega un adaptador desde su plantilla maestra centralizada:
```powershell
python python tools/ai_protocol.py adapters deploy --target antigravity
```

### 2.4 Listar Handoffs Registrados
```powershell
python python tools/ai_protocol.py handoff list
# Filtrar por estado:
python python tools/ai_protocol.py handoff list --status ready
```

### 2.5 Inspeccionar y Validar un Handoff
Descubre automáticamente el handoff activo para el alcance actual (o recibe `--id` / `--path`), valida su esquema JSON, contrasta su SHA-256 contra `INDEX.json` y el puntero local del router, y evalúa las evidencias y estado Git:
```powershell
python python tools/ai_protocol.py handoff inspect
```

### 2.6 Consumir un Handoff (Relevo Exitoso)
Marca el handoff como `consumed` en ambos niveles (`INDEX.json` y `session-state.json`), registrando `consumed_by` y `consumed_at`, preservando telemetría y claves ajenas por merge no destructivo:
```powershell
python python tools/ai_protocol.py handoff consume --by antigravity
```

### 2.7 Crear un Handoff Interoperable
Genera `handoff.json` + `handoff.md`, calcula el SHA-256, actualiza `INDEX.json` (marcando cualquier entrada `ready` previa como `superseded`) y el `session-state.json` local:
```powershell
python python tools/ai_protocol.py handoff create `
  --id "mi-proyecto-20261023-cierre" `
  --objective "Objetivo de la sesión completada" `
  -c "Logro 1 completado" `
  -c "Logro 2 completado" `
  -n "Próxima acción inmediata 1" `
  -n "Próxima acción 2" `
  --platform antigravity
```

### 2.8 Puente con ChatGPT Web / Projects (Export & Import)
Permite transferir sesiones fluidamente hacia y desde ChatGPT Web:

- **Exportar handoff para ChatGPT:**
  ```powershell
  python python tools/ai_protocol.py handoff export
  ```
  *Genera un mensaje formateado con el bloque ````aiwp-handoff```` listo para copiar y pegar en ChatGPT.*

- **Importar handoff devuelto por ChatGPT:**
  ```powershell
  python python tools/ai_protocol.py handoff import -f handoff_chatgpt.txt
  ```
  *Parsea el bloque ````aiwp-handoff````, valida el esquema JSON 1.1, escribe `handoff.json` y `handoff.md`, y registra el handoff en `INDEX.json` y en el router local.*

---

## 3. Pruebas Automatizadas

El runtime cuenta con una suite completa de pruebas unitarias e integración en `tests/test_ai_protocol.py`:
```powershell
python python tests/test_ai_protocol.py
```
*Cobertura: 100% PASS (7 tests: verify, status, adapters check, handoff list, inspect, export e importación/consumo aislado).*
