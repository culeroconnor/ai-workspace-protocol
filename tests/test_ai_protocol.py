#!/usr/bin/env python3
"""
test_ai_protocol.py — Tests automatizados para tools/ai_protocol.py.
Verifica que los subcomandos status, verify, adapters check/deploy,
handoff list/inspect/create/consume/export/import funcionen de forma determinista.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent.parent / "tools"
CLI_SCRIPT = TOOLS_DIR / "ai_protocol.py"
PROTOCOL_ROOT = Path(__file__).resolve().parent.parent


class TestAIProtocolCLI(unittest.TestCase):

    def run_cli(self, args: list[str], env: dict = None) -> subprocess.CompletedProcess:
        e = os.environ.copy()
        if env:
            e.update(env)
        cmd = [sys.executable, str(CLI_SCRIPT)] + args
        return subprocess.run(cmd, capture_output=True, text=True, env=e, check=False)

    def test_verify_command(self):
        res = self.run_cli(["verify"])
        self.assertEqual(res.returncode, 0, f"verify falló: {res.stderr}\n{res.stdout}")
        self.assertIn("TODO CORRECTO (PASS)", res.stdout)
        self.assertIn("AI_WORKSPACE_PROTOCOL.md", res.stdout)
        self.assertIn("INDEX.json valida contra esquema", res.stdout)

    def test_status_json_command(self):
        res = self.run_cli(["status", "--json", "--workspace", str(PROTOCOL_ROOT)])
        self.assertEqual(res.returncode, 0, f"status falló: {res.stderr}\n{res.stdout}")
        data = json.loads(res.stdout)
        self.assertEqual(data["protocol_version"], "1.0.2-draft")
        self.assertIsNotNone(data["canonical_hash"])
        self.assertIn("adapters", data)
        self.assertIn("antigravity", data["adapters"])
        self.assertIn("claude_code", data["adapters"])
        self.assertIn("codex", data["adapters"])
        self.assertIn("chatgpt_web", data["adapters"])

    def test_adapters_check_command(self):
        res = self.run_cli(["adapters", "check"])
        self.assertEqual(res.returncode, 0, f"adapters check falló: {res.stderr}\n{res.stdout}")
        self.assertIn("Estado de Adaptadores de Plataforma", res.stdout)
        self.assertIn("antigravity", res.stdout)
        self.assertIn("claude_code", res.stdout)
        self.assertIn("codex", res.stdout)
        self.assertIn("chatgpt_web", res.stdout)

    def test_handoff_list_json_command(self):
        res = self.run_cli(["handoff", "list", "--json"])
        self.assertEqual(res.returncode, 0, f"handoff list falló: {res.stderr}\n{res.stdout}")
        data = json.loads(res.stdout)
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)
        for entry in data:
            self.assertIn("handoff_id", entry)
            self.assertIn("status", entry)
            self.assertIn("sha256", entry)

    def test_handoff_inspect_command(self):
        res = self.run_cli(["handoff", "inspect", "--json"])
        self.assertEqual(res.returncode, 0, f"handoff inspect falló: {res.stderr}\n{res.stdout}")
        data = json.loads(res.stdout)
        self.assertIn("handoff_id", data)
        self.assertEqual(data["schema_validation"], "PASS")
        self.assertTrue(data["index_sha256_match"])

    def test_handoff_export_command(self):
        res = self.run_cli(["handoff", "export"])
        self.assertEqual(res.returncode, 0, f"handoff export falló: {res.stderr}\n{res.stdout}")
        self.assertIn("```aiwp-handoff", res.stdout)
        self.assertIn("Relevo de Sesión para ChatGPT Web", res.stdout)

    def test_isolated_handoff_lifecycle_and_chatgpt_bridge(self):
        """Prueba de ciclo completo (create -> inspect -> export -> import -> consume) en entorno aislado."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_root = Path(tmp_dir)
            
            # Copiar esquemas necesarios
            (tmp_root / "schemas").mkdir(parents=True)
            for sname in ["handoff.schema.json", "handoff-index.schema.json"]:
                shutil.copy2(PROTOCOL_ROOT / "schemas" / sname, tmp_root / "schemas" / sname)

            # Crear estructura runtime inicial
            (tmp_root / "runtime" / "handoffs").mkdir(parents=True)
            initial_index = {
                "schema_version": "1.0",
                "protocol_version": "1.0.2-draft",
                "updated_at": "2026-10-23T12:00:00-03:00",
                "entries": []
            }
            with open(tmp_root / "runtime" / "handoffs" / "INDEX.json", "w", encoding="utf-8") as f:
                json.dump(initial_index, f, indent=2)

            # Crear workspace temporal con session-state.json
            mock_ws = tmp_root / "mock_project"
            (mock_ws / ".agents" / "antigravity-router").mkdir(parents=True)
            with open(mock_ws / ".agents" / "antigravity-router" / "session-state.json", "w", encoding="utf-8") as f:
                json.dump({"phase": "ACTIVE", "active_task": "Prueba unitaria"}, f)

            env = {"AI_SHARED_ROOT": str(tmp_root)}

            # 1. Crear handoff
            create_res = self.run_cli([
                "handoff", "create",
                "--id", "test-isolated-001",
                "--objective", "Probar creación de handoff",
                "-n", "Paso de prueba 1",
                "-c", "Paso completado 0",
                "--workspace", str(mock_ws),
                "--platform", "antigravity"
            ], env=env)
            self.assertEqual(create_res.returncode, 0, f"create falló: {create_res.stderr}\n{create_res.stdout}")
            self.assertTrue((tmp_root / "runtime" / "handoffs" / "test-isolated-001" / "handoff.json").exists())

            # 2. Exportar handoff para ChatGPT
            export_file = tmp_root / "chatgpt_payload.md"
            export_res = self.run_cli([
                "handoff", "export",
                "--id", "test-isolated-001",
                "--output", str(export_file)
            ], env=env)
            self.assertEqual(export_res.returncode, 0, f"export falló: {export_res.stderr}\n{export_res.stdout}")
            self.assertTrue(export_file.exists())

            # 3. Simular respuesta de ChatGPT (bloque ```aiwp-handoff ... ```)
            chatgpt_response_text = f"""
Aquí está el avance de la sesión en ChatGPT:

```aiwp-handoff
{{
  "schema_version": "1.1",
  "handoff_id": "chatgpt-20261023-analisis",
  "created_at": "2026-10-23T21:15:00-03:00",
  "protocol_version": "1.0.2-draft",
  "operating_level": 7,
  "source": {{
    "platform": "chatgpt",
    "surface": "chatgpt_web_projects",
    "model": "gpt-4o",
    "session_id": "session-chatgpt-123"
  }},
  "scope": {{
    "context_mode": "project",
    "project_id": "mock_project",
    "project_root": "{mock_ws.as_posix()}",
    "git_branch": "main",
    "topic_id": null
  }},
  "objective": "Análisis completado en ChatGPT",
  "status": "ready",
  "completed": [
    "Análisis de arquitectura realizado en ChatGPT"
  ],
  "validated": [],
  "decisions": [],
  "files_changed": [],
  "errors": [],
  "risks": [],
  "unresolved": [],
  "next_actions": [
    "Retomar en Antigravity y verificar impacto"
  ],
  "authority_sources": [
    "~/.agents/protocol/AI_WORKSPACE_PROTOCOL.md"
  ],
  "checkpoints": [],
  "log_refs": [],
  "knowledge_candidates": [],
  "privacy": {{
    "classification": "internal",
    "secrets_included": false,
    "redactions": []
  }}
}}
```

Podés continuar con la tarea localmente.
"""
            # 4. Importar el handoff de ChatGPT
            import_res = self.run_cli([
                "handoff", "import",
                "--text", chatgpt_response_text
            ], env=env)
            self.assertEqual(import_res.returncode, 0, f"import falló: {import_res.stderr}\n{import_res.stdout}")
            self.assertTrue((tmp_root / "runtime" / "handoffs" / "chatgpt-20261023-analisis" / "handoff.json").exists())

            # 5. Consumir el handoff importado desde Antigravity
            consume_res = self.run_cli([
                "handoff", "consume",
                "--id", "chatgpt-20261023-analisis",
                "--by", "antigravity",
                "--workspace", str(mock_ws)
            ], env=env)
            self.assertEqual(consume_res.returncode, 0, f"consume falló: {consume_res.stderr}\n{consume_res.stdout}")

            # 6. Validar que INDEX.json tiene ambas entradas registradas correctamente
            with open(tmp_root / "runtime" / "handoffs" / "INDEX.json", "r", encoding="utf-8") as f:
                idx = json.load(f)
            self.assertEqual(len(idx["entries"]), 2)
            # La primera entrada debe estar en superseded
            self.assertEqual(idx["entries"][0]["status"], "superseded")
            # La entrada de ChatGPT debe estar en consumed
            self.assertEqual(idx["entries"][1]["handoff_id"], "chatgpt-20261023-analisis")
            self.assertEqual(idx["entries"][1]["status"], "consumed")
            self.assertEqual(idx["entries"][1]["consumed_by"], "antigravity")


if __name__ == "__main__":
    unittest.main()
