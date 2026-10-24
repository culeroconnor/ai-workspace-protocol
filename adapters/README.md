# Repositorio Central de Adaptadores — AI Workspace Protocol

En este directorio se mantienen las plantillas maestras de proyección del protocolo hacia las diferentes plataformas y asistentes.

```text
adapters/
├── antigravity/
│   └── ai_workspace_protocol.md           # Regla global para Google Antigravity (~/.gemini/config/rules/)
├── claude_code/
│   └── AI_WORKSPACE_PROTOCOL.md           # Regla importada para Claude Code CLI (~/.claude/CLAUDE.md)
├── codex/
│   └── ai_workspace_protocol_block.md     # Bloque delimitado para OpenAI Codex (~/.codex/AGENTS.md)
└── chatgpt/
    ├── PROJECT_INSTRUCTIONS.md            # Instrucciones del sistema para ChatGPT Projects / Custom GPTs
    └── AI_WORKSPACE_PROTOCOL_CHATGPT.md   # Documento adjunto de conocimiento para ChatGPT Projects
```

---

## Detección y Verificación de Deriva

Cada adaptador incluye en su encabezado el `canonical_sha256` del protocolo canónico ([AI_WORKSPACE_PROTOCOL.md](../AI_WORKSPACE_PROTOCOL.md)).

Para verificar el estado de los adaptadores instalados en la máquina contra el canónico:
```powershell
python python tools/ai_protocol.py adapters check
```
