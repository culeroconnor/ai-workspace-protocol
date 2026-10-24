# Contributing to AI Workspace Protocol (AIWP)

Thank you for your interest in improving and expanding the **AI Workspace Protocol**! This project is open source and community-driven, aimed at solving context fragmentation and enabling seamless interoperability across all modern AI models and agentic coding tools.

---

## 1. Guiding Principles

1. **Vendor Neutrality:** AIWP is not tied to any single provider. All major model families (OpenAI, Anthropic, Google, open-weight models like Llama, Mistral, Qwen) are first-class citizens.
2. **Empirical Verification over Hypotheses:** A claim is only valid if backed by an observable method and evidence (`validated[]`). Completed work is distinct from verified work.
3. **Cryptographic Integrity:** State handoffs and canonical policies rely on SHA-256 content hashes to detect drift and tampering.
4. **Human Sovereignty:** Autonomous execution must respect defined operational boundaries (Level 7 governance). Tools must not escalate permissions or make unapproved commitments.

---

## 2. Ways to Contribute

- **New Adapters:** Create and test adapters for emerging platforms (e.g., Cursor, Roo Code, Windsurf, Ollama, vLLM, GitHub Copilot Workspace).
- **Runtime Enhancements:** Improve `tools/ai_protocol.py` (e.g., support for additional packaging formats, MCP native servers, cross-platform shell wrappers).
- **Documentation & Translations:** Help translate specifications, guides, and examples into additional languages.
- **Bug Reports & Issues:** Identify edge cases in JSON schema validation, Git status detection, or cross-platform path handling.

---

## 3. Contribution Workflow

1. **Fork the repository** on GitHub.
2. **Create a feature branch:**
   ```bash
   git checkout -b feature/adapter-cursor
   ```
3. **Ensure All Automated Tests Pass:**
   ```bash
   python tests/test_ai_protocol.py
   python tools/ai_protocol.py verify
   ```
4. **Follow Schema Compliance:** Any change to handoffs or index files must validate against the schemas in `schemas/`.
5. **Open a Pull Request:** Provide a clear description of your change, testing evidence, and the motivation behind it.

---

## 4. Code of Conduct & Attribution

- Maintain a welcoming, respectful, and collaborative environment.
- Respect copyright and attribution: all contributions remain open under the **MIT License**, preserving the original authorship notice of Gastón as defined in `LICENSE` and `CITATION.cff`.
