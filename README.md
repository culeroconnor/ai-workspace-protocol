# AI Workspace Protocol (AIWP)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Spec: 1.0.2-draft](https://img.shields.io/badge/spec-1.0.2--draft-brightgreen.svg)](AI_WORKSPACE_PROTOCOL.md)
[![Tests: 100% Pass](https://img.shields.io/badge/tests-7%2F7%20PASS-success.svg)](tests/test_ai_protocol.py)
[![Governance: Level 7](https://img.shields.io/badge/governance-Level%207-blueviolet.svg)](specs/NIVEL_7.md)

> **Universal context continuity, cryptographic state verification, and seamless handoffs across ChatGPT, Claude, Google Gemini / Antigravity, and OpenAI Codex.**

---

[English](#english) | [Español](#español)

---

<a name="english"></a>
## 🌐 English

### The Problem: Brilliant Models with Amnesia

Modern Large Language Models (LLMs) and agentic coding tools are extraordinary, but they suffer from two fundamental bottlenecks:

1. **Context Window Exhaustion (Amnesia):** Long sessions inevitably hit token limits or degrade into hallucination as older context is truncated or compressed.
2. **Ecosystem Fragmentation (The Tower of Babel):** OpenAI, Anthropic, and Google live in siloed walled gardens. You cannot transition a task from Claude to ChatGPT or Gemini without manual copy-pasting, explaining everything from scratch, and risking silent context corruption.

### The Solution: The Medical Handoff & Relay Race

Inspired by **hospital shift changeover protocols** and **athletic relay races**, the **AI Workspace Protocol (AIWP)** establishes an open, vendor-neutral standard:

- **The Handoff:** When an AI finishes a session or reaches a milestone, it outputs a cryptographically signed, structured handoff containing:
  - Exact objective and completed milestones.
  - **Empirically validated claims** (backed by verifiable methods, test outputs, and evidence refs, strictly separating *completed* from *empirically verified*).
  - Explicit architectural decisions.
  - The ordered, exact **next actions** for the incoming model.
- **Two-Level Relay Index:** A global index (`INDEX.json`) and a local workspace pointer (`session-state.json`) track who holds the active baton.
- **Cryptographic Guardrails (SHA-256):** Every handoff, specification, and adapter includes a content hash. If a single character is tampered with or corrupted, incoming assistants halt and flag drift.
- **Human Sovereignty (Level 7 Governance):** Autonomous execution stays within approved gates. High-impact operations require explicit confirmation.

```
       ┌────────────────────────────────────────────────────────┐
       │             AI WORKSPACE PROTOCOL (AIWP)               │
       │         Open, Verifiable Multi-LLM Continuity          │
       └───────────────────────────┬────────────────────────────┘
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         ▼                         ▼                         ▼
 [Google Antigravity]    [Anthropic Claude Code]    [OpenAI Codex/ChatGPT]
    (Local Workspace)        (CLI Assistant)          (Local & Cloud Web)
         │                         │                         │
         └─────────────────────────┴─────────────────────────┘
                                   │
                                   ▼
             Global Index & Cryptographic Two-Level Relay
```

---

### Quick Start (3 Minutes)

#### 1. Clone & Verify
```bash
git clone https://github.com/culeroconnor/ai-workspace-protocol.git
cd ai-workspace-protocol
pip install jsonschema
python tools/ai_protocol.py verify
```

#### 2. Run Session Diagnostics
```bash
python tools/ai_protocol.py status
```

#### 3. Inspect the Active Handoff
```bash
python tools/ai_protocol.py handoff inspect
```

#### 4. Safely Consume & Take Over
```bash
python tools/ai_protocol.py handoff consume --by claude-code
```

#### 5. Seamless Bridge with ChatGPT Web
Export current state into an optimized prompt:
```bash
python tools/ai_protocol.py handoff export
```
Paste it in ChatGPT, work on the cloud sandbox, and import the returned block back to your local machine:
```bash
python tools/ai_protocol.py handoff import -f response_from_chatgpt.txt
```

---

<a name="español"></a>
## 🇪🇸 Español

### El Problema: Modelos Brillantes con Amnesia

Las Inteligencias Artificiales modernas son extraordinarias programando y razonando, pero sufren de dos limitaciones críticas:
1. **Agotamiento de contexto (Amnesia):** Cuando una conversación se vuelve extensa, la IA olvida el inicio, compacta memoria y comienza a contradecirse o alucinar.
2. **Aislamiento entre plataformas:** OpenAI, Anthropic y Google no se comunican entre sí. Pasar de Claude a ChatGPT o Gemini exige copiar y pegar manualmente y re-explicar todo el proyecto.

### La Solución: El Pase de Guardia y la Carrera de Postas

Inspirado en los **pases de guardia médica** y en las **carreras de atletismo con testimonio**, el **AI Workspace Protocol (AIWP)** es un estándar abierto, libre y neutral:
- **El Handoff (Relevo estructurado):** Cada IA deja asentado qué logró, qué comprobó con pruebas reales (diferenciando completado de validado), qué decisiones tomó y cuál es la **próxima acción exacta**.
- **Relevo en Dos Niveles:** Un índice global y un puntero local registran qué asistente tiene el turno activo.
- **Seguridad Criptográfica (SHA-256):** Cada documento cuenta con una huella digital matemática. Si alguien altera un archivo, el sistema detecta la deriva de inmediato.
- **Gobernanza Nivel 7:** Trabajo estructurado en pasos delimitados con control humano en puntos críticos.

---

### Arquitectura del Repositorio

```text
├── AI_WORKSPACE_PROTOCOL.md    # Especificación canónica universal v1.0.2-draft
├── LICENSE                     # Licencia MIT (Atribución a Gastón)
├── CITATION.cff                # Metadatos de citación académica y técnica
├── CONTRIBUTING.md             # Guía de contribución comunitaria
├── schemas/                    # Esquemas JSON Draft 2020-12
│   ├── handoff.schema.json
│   ├── handoff-index.schema.json
│   └── session-event.schema.json
├── specs/                      # Especificación formal de Nivel 7
│   └── NIVEL_7.md
├── tools/                      # Runtime CLI universal
│   ├── ai_protocol.py          # Motor multiplataforma
│   ├── ai-protocol.ps1         # Wrapper para PowerShell
│   └── README.md
├── adapters/                   # Adaptadores oficiales listos para usar
│   ├── antigravity/            # Google Antigravity (~/.gemini/config/rules/)
│   ├── claude_code/            # Claude Code CLI (~/.claude/CLAUDE.md)
│   ├── codex/                  # OpenAI Codex (~/.codex/AGENTS.md)
│   └── chatgpt/                # ChatGPT Web / Projects (Instrucciones de proyecto)
├── examples/                   # Ejemplos reales de handoffs
└── tests/                      # Suite de pruebas automatizadas (100% PASS)
```

---

### Comandos del Runtime CLI (`tools/ai_protocol.py`)

| Comando | Acción |
|---|---|
| `ai_protocol.py status` | Diagnóstico de inicio (§3), git HEAD, último handoff y adaptadores. |
| `ai_protocol.py verify` | Verifica integridad contra `MANIFEST_SHA256.json` y valida esquemas. |
| `ai_protocol.py adapters check` | Detecta posibles derivas de versión en adaptadores instalados. |
| `ai_protocol.py handoff list` | Lista todos los handoffs registrados y sus estados (`ready`, `consumed`). |
| `ai_protocol.py handoff inspect` | Descubre el handoff activo, valida esquema, hash y contrastes Git. |
| `ai_protocol.py handoff consume` | Consume un relevo por merge no destructivo preservando telemetría. |
| `ai_protocol.py handoff create` | Genera `handoff.json` y `handoff.md`, calcula SHA-256 y actualiza índice. |
| `ai_protocol.py handoff export` | Genera bloque listo para transferir a ChatGPT Web. |
| `ai_protocol.py handoff import` | Importa y valida un bloque devuelto por ChatGPT Web. |

---

### Pruebas Automatizadas

```bash
python tests/test_ai_protocol.py
```
```text
Ran 7 tests in 3.55s
OK (100% PASS)
```

---

### Cita y Autoría

Si utilizás este protocolo, especificación o software en tu investigación, proyecto o empresa, por favor citá a su autor original:

```bibtex
@software{gaston2026aiwp,
  author = {Gastón Lefort},
  title = {AI Workspace Protocol (AIWP): Universal Context Continuity and Handoff across LLMs},
  year = {2026},
  url = {https://github.com/culeroconnor/ai-workspace-protocol},
  version = {1.0.2-draft}
}
```

---

### Licencia

Distribuido bajo la **Licencia MIT**. Consultar [LICENSE](LICENSE) para más detalles.
Libre para uso personal, educativo y comercial con atribución obligatoria al autor.
