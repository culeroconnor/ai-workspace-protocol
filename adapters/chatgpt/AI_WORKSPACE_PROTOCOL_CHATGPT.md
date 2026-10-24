# AI Workspace Protocol (AIWP) — Guía de Referencia para ChatGPT Projects

> **Uso:** Archivo de consulta y conocimiento adjunto para el Project en ChatGPT.

## 1. ¿Qué es AI Workspace Protocol?
Es el contrato universal de continuidad interoperable entre asistentes de Inteligencia Artificial (Google Antigravity, Anthropic Claude Code, OpenAI Codex y ChatGPT).  
Permite que una sesión iniciada o avanzada en ChatGPT pueda ser transferida con rigor a un entorno local, o viceversa, sin depender del historial de chat del navegador.

## 2. Contrato de Relevo (Handoff)
El núcleo de la continuidad es el artefacto `handoff`. Contiene:
- **`handoff_id`**: Identificador único (ej. `chatgpt-20261023-analisis-fase2`).
- **`scope`**: Identificador del proyecto (`project_id`), ruta base y rama de control de versiones.
- **`objective`**: Meta operativa alcanzada o en curso.
- **`completed`**: Lista de hitos y logros terminados.
- **`validated`**: Lista de afirmaciones probadas con método y evidencia auditable (separadas de lo simplemente completado).
- **`next_actions`**: Lista de acciones inmediatas ordenadas que el siguiente asistente debe tomar.
- **`status`**: Inicialmente `ready`. Una vez que el asistente receptor retoma la sesión, se marca como `consumed`.

## 3. Formato del Bloque de Intercambio
Cuando emitas un handoff para transferir la sesión a la máquina de Gastón, debés encerrar el JSON completo en un bloque con etiqueta `aiwp-handoff`:

````text
```aiwp-handoff
{
  "schema_version": "1.1",
  "handoff_id": "...",
  ...
}
```
````

Este formato permite que la herramienta CLI local de Gastón (`ai-protocol handoff import`) parsee, valide el esquema JSON y registre automáticamente el handoff en el índice global del sistema (`INDEX.json`).
