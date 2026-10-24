#!/usr/bin/env python3
"""
ai_protocol.py — Runtime CLI para el AI Workspace Protocol (AIWP).
Implementa las operaciones de bootstrap (§3), verificación (§14),
relevo interoperable en dos niveles (§5.4), ciclo de vida de handoff (§5),
gestión de adaptadores (§9) e intercambio portable con ChatGPT Web.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import jsonschema
except ImportError:
    jsonschema = None


# -----------------------------------------------------------------------------
# Constantes y resolución de rutas
# -----------------------------------------------------------------------------

def get_shared_root() -> Path:
    env_root = os.environ.get("AI_SHARED_ROOT")
    if env_root:
        p = Path(env_root).resolve()
        if p.exists():
            return p

    # Si se invoca desde <AI_SHARED_ROOT>/tools/ai_protocol.py
    script_parent = Path(__file__).resolve().parent.parent
    if (script_parent / "AI_WORKSPACE_PROTOCOL.md").exists():
        return script_parent

    # Ruta estándar en Windows
    user_home = Path.home()
    default_root = user_home / ".agents" / "protocol"
    if default_root.exists():
        return default_root.resolve()

    raise FileNotFoundError(
        "No se pudo localizar <AI_SHARED_ROOT>. Verifique que 'AI_SHARED_ROOT' esté definida "
        "o que exista en '~/.agents/protocol'."
    )


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat(timespec="seconds")


def detect_git_info(workspace: Optional[Path]) -> Dict[str, Any]:
    if not workspace or not workspace.exists():
        return {"is_git": False, "head": None, "branch": None, "clean": None, "root": None}

    try:
        r_root = subprocess.run(
            ["git", "-C", str(workspace), "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=False
        )
        if r_root.returncode != 0:
            return {"is_git": False, "head": None, "branch": None, "clean": None, "root": None}

        git_root = Path(r_root.stdout.strip()).resolve()
        r_head = subprocess.run(
            ["git", "-C", str(workspace), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=False
        )
        r_branch = subprocess.run(
            ["git", "-C", str(workspace), "branch", "--show-current"],
            capture_output=True, text=True, check=False
        )
        r_status = subprocess.run(
            ["git", "-C", str(workspace), "status", "--porcelain"],
            capture_output=True, text=True, check=False
        )

        return {
            "is_git": True,
            "root": str(git_root).replace("\\", "/"),
            "head": r_head.stdout.strip() if r_head.returncode == 0 else None,
            "branch": r_branch.stdout.strip() if r_branch.returncode == 0 else None,
            "clean": len(r_status.stdout.strip()) == 0 if r_status.returncode == 0 else False,
        }
    except Exception:
        return {"is_git": False, "head": None, "branch": None, "clean": None, "root": None}


def validate_schema(instance: Any, schema_path: Path) -> Tuple[bool, Optional[str]]:
    if not jsonschema:
        return False, "Librería jsonschema no instalada."
    if not schema_path.exists():
        return False, f"Esquema no encontrado: {schema_path}"

    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    try:
        jsonschema.validate(instance=instance, schema=schema)
        return True, None
    except jsonschema.exceptions.ValidationError as e:
        return False, f"Validación de esquema falló en '{e.json_path}': {e.message}"
    except Exception as e:
        return False, f"Error general validando esquema: {e}"


def load_or_init_index(index_path: Path) -> dict:
    if index_path.exists():
        with open(index_path, "r", encoding="utf-8") as f:
            return json.load(f)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    initial = {
        "schema_version": "1.0",
        "protocol_version": "1.0.2-draft",
        "updated_at": now_iso(),
        "entries": []
    }
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(initial, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return initial


# -----------------------------------------------------------------------------
# Adaptadores registrados (§9)
# -----------------------------------------------------------------------------

def check_adapters(canonical_hash: str) -> Dict[str, Any]:
    home = Path.home()
    root = get_shared_root()
    results = {}

    # 1. Google Antigravity
    antigravity_rule = home / ".gemini" / "config" / "rules" / "ai_workspace_protocol.md"
    template_antigravity = root / "adapters" / "antigravity" / "ai_workspace_protocol.md"
    if antigravity_rule.exists():
        text = antigravity_rule.read_text(encoding="utf-8")
        stale = canonical_hash.lower() not in text.lower()
        results["antigravity"] = {
            "path": str(antigravity_rule),
            "template": str(template_antigravity) if template_antigravity.exists() else None,
            "status": "UP_TO_DATE" if not stale else "STALE",
            "matches_canonical": not stale,
        }
    else:
        results["antigravity"] = {"status": "NOT_INSTALLED", "path": str(antigravity_rule)}

    # 2. Claude Code
    claude_adapter = home / ".claude" / "AI_WORKSPACE_PROTOCOL.md"
    template_claude = root / "adapters" / "claude_code" / "AI_WORKSPACE_PROTOCOL.md"
    if claude_adapter.exists():
        text = claude_adapter.read_text(encoding="utf-8")
        m = re.search(r"canonical_sha256:\s*([0-9a-fA-F]{64})", text)
        found_hash = m.group(1).lower() if m else None
        matches = (found_hash == canonical_hash.lower())
        results["claude_code"] = {
            "path": str(claude_adapter),
            "template": str(template_claude) if template_claude.exists() else None,
            "status": "UP_TO_DATE" if matches else "STALE",
            "declared_hash": found_hash,
            "matches_canonical": matches,
        }
    else:
        results["claude_code"] = {"status": "NOT_INSTALLED", "path": str(claude_adapter)}

    # 3. OpenAI Codex
    codex_agents = home / ".codex" / "AGENTS.md"
    template_codex = root / "adapters" / "codex" / "ai_workspace_protocol_block.md"
    if codex_agents.exists():
        text = codex_agents.read_text(encoding="utf-8")
        m = re.search(r"canonical_sha256:\s*([0-9a-fA-F]{64})", text)
        found_hash = m.group(1).lower() if m else None
        matches = (found_hash == canonical_hash.lower())
        results["codex"] = {
            "path": str(codex_agents),
            "template": str(template_codex) if template_codex.exists() else None,
            "status": "UP_TO_DATE" if matches else "STALE" if found_hash else "UNCONFIGURED",
            "declared_hash": found_hash,
            "matches_canonical": matches,
        }
    else:
        results["codex"] = {"status": "NOT_INSTALLED", "path": str(codex_agents)}

    # 4. ChatGPT Web / Projects
    chatgpt_inst = root / "adapters" / "chatgpt" / "PROJECT_INSTRUCTIONS.md"
    if chatgpt_inst.exists():
        text = chatgpt_inst.read_text(encoding="utf-8")
        m = re.search(r"canonical_sha256:\s*([0-9a-fA-F]{64})", text)
        found_hash = m.group(1).lower() if m else None
        matches = (found_hash == canonical_hash.lower())
        results["chatgpt_web"] = {
            "path": str(chatgpt_inst),
            "template": str(chatgpt_inst),
            "status": "UP_TO_DATE" if matches else "STALE",
            "declared_hash": found_hash,
            "matches_canonical": matches,
            "note": "Plantilla maestra lista para copiar en Instrucciones de Project",
        }
    else:
        results["chatgpt_web"] = {
            "status": "PENDING_SPEC",
            "path": None,
            "note": "Requiere despliegue en memoria / instrucciones de Project",
        }

    return results


# -----------------------------------------------------------------------------
# Subcomando: status / bootstrap (§3)
# -----------------------------------------------------------------------------

def cmd_status(args: argparse.Namespace) -> int:
    root = get_shared_root()
    canonical = root / "AI_WORKSPACE_PROTOCOL.md"
    canonical_hash = sha256_file(canonical) if canonical.exists() else None

    # Detectar workspace
    workspace = Path(args.workspace).resolve() if args.workspace else Path.cwd().resolve()
    git_info = detect_git_info(workspace)
    if git_info["is_git"] and git_info["root"]:
        workspace_path = Path(git_info["root"])
        project_id = workspace_path.name
        context_mode = "project"
    else:
        workspace_path = workspace
        project_id = workspace_path.name
        context_mode = "project" if workspace.exists() and any((workspace / f).exists() for f in ["START_HERE.md", ".git"]) else "general"

    # INDEX.json
    index_path = root / "runtime" / "handoffs" / "INDEX.json"
    last_handoff_id = None
    last_handoff_status = None
    if index_path.exists():
        try:
            with open(index_path, "r", encoding="utf-8") as f:
                index_data = json.load(f)
            matching_entries = [
                e for e in index_data.get("entries", [])
                if e.get("scope_key") == project_id or e.get("workspace") == str(workspace_path).replace("\\", "/")
            ]
            if matching_entries:
                last_entry = matching_entries[-1]
                last_handoff_id = last_entry.get("handoff_id")
                last_handoff_status = last_entry.get("status")
            elif index_data.get("entries"):
                last_entry = index_data["entries"][-1]
                last_handoff_id = last_entry.get("handoff_id")
                last_handoff_status = last_entry.get("status")
        except Exception as e:
            last_handoff_id = f"ERROR_READING_INDEX: {e}"

    # session-state local
    local_state_path = workspace_path / ".agents" / "antigravity-router" / "session-state.json"
    local_handoff_id = None
    local_handoff_status = None
    if local_state_path.exists():
        try:
            with open(local_state_path, "r", encoding="utf-8") as f:
                sdata = json.load(f)
            lh = sdata.get("handoff", {})
            local_handoff_id = lh.get("handoff_id")
            local_handoff_status = lh.get("status")
        except Exception:
            pass

    adapters = check_adapters(canonical_hash or "")

    output_data = {
        "platform_surface": args.platform or os.environ.get("AI_PLATFORM", "observed_local"),
        "protocol_version": "1.0.2-draft",
        "canonical_hash": canonical_hash,
        "context_mode": context_mode,
        "project_root": str(workspace_path).replace("\\", "/") if context_mode == "project" else None,
        "operating_level": "7 (specs/NIVEL_7.md)",
        "git": git_info,
        "last_handoff": {
            "index_handoff_id": last_handoff_id,
            "index_status": last_handoff_status,
            "local_handoff_id": local_handoff_id,
            "local_status": local_handoff_status,
        },
        "adapters": adapters,
        "activation_status": "ACTIVO_Y_VERIFICADO" if last_handoff_status == "consumed" else "CONFIGURADO_SIN_VERIFICAR",
    }

    if args.json:
        print(json.dumps(output_data, indent=2, ensure_ascii=False))
    else:
        print("=== AI Workspace Protocol — Diagnóstico de Inicio (§3) ===")
        print(f"Platform / Surface        : {output_data['platform_surface']}")
        print(f"Protocolo / Hash canónico : {output_data['protocol_version']} / {canonical_hash}")
        print(f"Modo de contexto          : {context_mode}")
        print(f"Raíz de proyecto          : {output_data['project_root']}")
        if git_info['is_git']:
            print(f"Git                       : rama {git_info['branch']} | HEAD {git_info['head'][:8]} | limpio: {git_info['clean']}")
        print(f"Nivel operativo           : {output_data['operating_level']}")
        print(f"Último handoff (INDEX)    : {last_handoff_id} (status: {last_handoff_status})")
        if local_handoff_id:
            print(f"Puntero local (router)    : {local_handoff_id} (status: {local_handoff_status})")
        print("\nEstado de adaptadores:")
        for name, ad in adapters.items():
            print(f"  - {name.ljust(15)} : {ad['status']}")
        print(f"\nEstado de adopción (§11)  : {output_data['activation_status']}")

    return 0


# -----------------------------------------------------------------------------
# Subcomando: verify (§14)
# -----------------------------------------------------------------------------

def cmd_verify(args: argparse.Namespace) -> int:
    root = get_shared_root()
    manifest_path = root / "MANIFEST_SHA256.json"
    if not manifest_path.exists():
        print(f"ERROR: Manifiesto no encontrado en {manifest_path}", file=sys.stderr)
        return 1

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    all_pass = True
    results = []

    print("Verificando integridad de archivos canónicos contra MANIFEST_SHA256.json...")
    for item in manifest.get("files", []):
        rel_path = item["path"]
        expected_hash = item["sha256"]
        fpath = root / rel_path
        if not fpath.exists():
            print(f"  [MISSING] {rel_path}")
            results.append({"path": rel_path, "status": "MISSING"})
            all_pass = False
            continue

        actual_hash = sha256_file(fpath)
        if actual_hash == expected_hash:
            print(f"  [PASS]    {rel_path}")
            results.append({"path": rel_path, "status": "PASS", "sha256": actual_hash})
        else:
            print(f"  [FAIL]    {rel_path}")
            print(f"            Esperado: {expected_hash}")
            print(f"            Obtenido: {actual_hash}")
            results.append({"path": rel_path, "status": "FAIL", "expected": expected_hash, "actual": actual_hash})
            all_pass = False

    # Validar schemas
    schema_dir = root / "schemas"
    for sname in ["handoff.schema.json", "handoff-index.schema.json", "session-event.schema.json"]:
        spath = schema_dir / sname
        if spath.exists():
            try:
                with open(spath, "r", encoding="utf-8") as f:
                    s_obj = json.load(f)
                if jsonschema:
                    jsonschema.Draft202012Validator.check_schema(s_obj)
                    print(f"  [SCHEMA]  {sname} es válido Draft 2020-12.")
            except Exception as e:
                print(f"  [SCHEMA-FAIL] {sname}: {e}")
                all_pass = False

    # Validar INDEX.json actual
    index_path = root / "runtime" / "handoffs" / "INDEX.json"
    if index_path.exists():
        try:
            with open(index_path, "r", encoding="utf-8") as f:
                idata = json.load(f)
            ok, err = validate_schema(idata, schema_dir / "handoff-index.schema.json")
            if ok:
                print("  [PASS]    runtime/handoffs/INDEX.json valida contra esquema.")
            else:
                print(f"  [FAIL]    runtime/handoffs/INDEX.json: {err}")
                all_pass = False
        except Exception as e:
            print(f"  [FAIL]    runtime/handoffs/INDEX.json: {e}")
            all_pass = False

    print("\nResultado general:", "TODO CORRECTO (PASS)" if all_pass else "FALLOS DETECTADOS")
    return 0 if all_pass else 1


# -----------------------------------------------------------------------------
# Subcomandos: adapters check / deploy (§9)
# -----------------------------------------------------------------------------

def cmd_adapters_check(args: argparse.Namespace) -> int:
    root = get_shared_root()
    canonical = root / "AI_WORKSPACE_PROTOCOL.md"
    canonical_hash = sha256_file(canonical) if canonical.exists() else None

    if not canonical_hash:
        print("ERROR: No se pudo calcular el hash del canónico.", file=sys.stderr)
        return 1

    adapters = check_adapters(canonical_hash)

    if args.json:
        print(json.dumps(adapters, indent=2, ensure_ascii=False))
        return 0

    print("=== Estado de Adaptadores de Plataforma (§9) ===")
    print(f"Hash canónico de referencia: {canonical_hash}\n")
    fmt = "{:<16} {:<15} {:<64}"
    print(fmt.format("PLATAFORMA", "ESTADO", "ARCHIVO / PLANTILLA"))
    print("-" * 95)

    all_pass = True
    for name, info in adapters.items():
        st = info.get("status", "UNKNOWN")
        path_str = info.get("path") or info.get("note", "N/D")
        print(fmt.format(name, st, path_str[:64]))
        if st not in ["UP_TO_DATE", "PENDING_SPEC"]:
            all_pass = False

    print("-" * 95)
    return 0 if all_pass else 1


def cmd_adapters_deploy(args: argparse.Namespace) -> int:
    root = get_shared_root()
    canonical = root / "AI_WORKSPACE_PROTOCOL.md"
    canonical_hash = sha256_file(canonical) if canonical.exists() else None

    if not canonical_hash:
        print("ERROR: No se pudo calcular el hash del canónico.", file=sys.stderr)
        return 1

    target = args.target.lower()
    adapters_dir = root / "adapters"
    home = Path.home()

    if target == "antigravity":
        src = adapters_dir / "antigravity" / "ai_workspace_protocol.md"
        dst = home / ".gemini" / "config" / "rules" / "ai_workspace_protocol.md"
    elif target == "claude_code":
        src = adapters_dir / "claude_code" / "AI_WORKSPACE_PROTOCOL.md"
        dst = home / ".claude" / "AI_WORKSPACE_PROTOCOL.md"
    elif target == "chatgpt":
        print("ChatGPT Web/Projects no utiliza archivos locales. Usá el texto de 'adapters/chatgpt/PROJECT_INSTRUCTIONS.md'.")
        return 0
    else:
        print(f"Target '{target}' no soportado para despliegue automático directo.", file=sys.stderr)
        return 1

    if not src.exists():
        print(f"ERROR: Plantilla maestra no encontrada en {src}", file=sys.stderr)
        return 1

    content = src.read_text(encoding="utf-8")
    # Asegurar que tiene el hash canónico actual
    content = re.sub(r"canonical_sha256:\s*[0-9a-fA-F]{64}", f"canonical_sha256: {canonical_hash}", content)

    if args.dry_run:
        print(f"[DRY-RUN] Se escribiría en {dst}:")
        print(content[:400] + "\n...")
        return 0

    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(content, encoding="utf-8")
    print(f"Adaptador '{target}' desplegado exitosamente en {dst}.")
    return 0


# -----------------------------------------------------------------------------
# Subcomando: handoff list
# -----------------------------------------------------------------------------

def cmd_handoff_list(args: argparse.Namespace) -> int:
    root = get_shared_root()
    index_path = root / "runtime" / "handoffs" / "INDEX.json"
    data = load_or_init_index(index_path)

    entries = data.get("entries", [])
    if args.status:
        entries = [e for e in entries if e.get("status") == args.status]
    if args.scope:
        entries = [e for e in entries if e.get("scope_key") == args.scope]

    if args.json:
        print(json.dumps(entries, indent=2, ensure_ascii=False))
        return 0

    print(f"Índice de Handoffs ({len(entries)} entradas):")
    print("-" * 90)
    fmt = "{:<32} {:<10} {:<12} {:<12} {:<24}"
    print(fmt.format("HANDOFF ID", "STATUS", "ORIGEN", "CONSUMIDO", "CREADO"))
    print("-" * 90)
    for e in entries:
        hid = e.get("handoff_id", "")[:32]
        st = e.get("status", "")
        src = e.get("source_platform", "")[:12]
        cby = (e.get("consumed_by") or "-")[:12]
        dt = e.get("created_at", "")[:24]
        print(fmt.format(hid, st, src, cby, dt))
    print("-" * 90)
    return 0


# -----------------------------------------------------------------------------
# Subcomando: handoff inspect
# -----------------------------------------------------------------------------

def cmd_handoff_inspect(args: argparse.Namespace) -> int:
    root = get_shared_root()
    index_path = root / "runtime" / "handoffs" / "INDEX.json"
    if not index_path.exists():
        print(f"No existe {index_path}", file=sys.stderr)
        return 1

    with open(index_path, "r", encoding="utf-8") as f:
        index_data = json.load(f)

    workspace = Path(args.workspace).resolve() if args.workspace else Path.cwd().resolve()
    git_info = detect_git_info(workspace)
    scope_key = workspace.name

    # Localizar handoff
    entry = None
    if args.id:
        entry = next((e for e in index_data.get("entries", []) if e.get("handoff_id") == args.id), None)
        if not entry:
            print(f"ERROR: Handoff '{args.id}' no encontrado en INDEX.json", file=sys.stderr)
            return 1
    elif args.path:
        p_str = args.path.replace("\\", "/")
        entry = next((e for e in index_data.get("entries", []) if e.get("path") == p_str or str(root / e.get("path")) == str(Path(args.path).resolve())), None)
        if not entry:
            target_path = Path(args.path).resolve()
    else:
        # Auto-descubrimiento: buscar el último 'ready' para el scope
        ready_entries = [
            e for e in index_data.get("entries", [])
            if e.get("status") == "ready" and (e.get("scope_key") == scope_key or not args.strict_scope)
        ]
        if ready_entries:
            entry = ready_entries[-1]
        else:
            if index_data.get("entries"):
                entry = index_data["entries"][-1]

    if not entry and not args.path:
        print("No se encontró ningún handoff para inspeccionar.", file=sys.stderr)
        return 1

    if entry:
        target_path = root / entry["path"]
        expected_sha = entry.get("sha256")
    else:
        target_path = Path(args.path).resolve()
        expected_sha = None

    if not target_path.exists():
        print(f"ERROR: Archivo handoff.json no encontrado en {target_path}", file=sys.stderr)
        return 1

    # 1. SHA-256 de handoff.json
    actual_sha = sha256_file(target_path)
    sha_match = (actual_sha == expected_sha) if expected_sha else None

    # 2. Validar esquema
    with open(target_path, "r", encoding="utf-8") as f:
        handoff_obj = json.load(f)

    schema_path = root / "schemas" / "handoff.schema.json"
    schema_ok, schema_err = validate_schema(handoff_obj, schema_path)

    # 3. Validar consistencia con local session-state.json
    local_state_path = workspace / ".agents" / "antigravity-router" / "session-state.json"
    session_state_sha_match = None
    if local_state_path.exists():
        try:
            with open(local_state_path, "r", encoding="utf-8") as f:
                ls_data = json.load(f)
            ls_sha = ls_data.get("handoff", {}).get("sha256")
            session_state_sha_match = (ls_sha == actual_sha)
        except Exception:
            pass

    # 4. Validar afirmaciones de archivos si se pueden verificar
    validated_checks = []
    for val in handoff_obj.get("validated", []):
        claim = val.get("claim", "")
        method = val.get("method", "")
        evidence_ref = val.get("evidence_ref", "")
        status = "UNCHECKED"

        if evidence_ref and Path(evidence_ref).exists() and ("SHA-256" in claim or "sha256" in method.lower()):
            file_h = sha256_file(Path(evidence_ref))
            if file_h in claim or file_h in method:
                status = "PASS"
            else:
                status = "MISMATCH"
        validated_checks.append({"claim": claim, "status": status, "ref": evidence_ref})

    report = {
        "handoff_id": handoff_obj.get("handoff_id"),
        "status": handoff_obj.get("status"),
        "path": str(target_path).replace("\\", "/"),
        "sha256": actual_sha,
        "index_sha256_match": sha_match,
        "session_state_sha256_match": session_state_sha_match,
        "schema_validation": "PASS" if schema_ok else f"FAIL: {schema_err}",
        "objective": handoff_obj.get("objective"),
        "next_actions": handoff_obj.get("next_actions", []),
        "git_checks": git_info,
        "validated_claims": validated_checks,
    }

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print("=== Inspección de Handoff ===")
        print(f"ID              : {report['handoff_id']}")
        print(f"Estado          : {report['status']}")
        print(f"Archivo         : {report['path']}")
        print(f"SHA-256         : {report['sha256']}")
        print(f"Coincide INDEX  : {report['index_sha256_match']}")
        print(f"Coincide Router : {report['session_state_sha256_match']}")
        print(f"Esquema JSON    : {report['schema_validation']}")
        print(f"Objetivo        : {report['objective']}")
        print("\nPróximas acciones inmediatas:")
        for i, act in enumerate(report["next_actions"], start=1):
            print(f"  {i}. {act}")

        if validated_checks:
            print("\nAfirmaciones auditadas:")
            for vc in validated_checks:
                print(f"  [{vc['status']}] {vc['claim']}")

    return 0 if (schema_ok and (sha_match is None or sha_match)) else 1


# -----------------------------------------------------------------------------
# Subcomando: handoff consume
# -----------------------------------------------------------------------------

def cmd_handoff_consume(args: argparse.Namespace) -> int:
    root = get_shared_root()
    index_path = root / "runtime" / "handoffs" / "INDEX.json"
    if not index_path.exists():
        print(f"ERROR: {index_path} no existe", file=sys.stderr)
        return 1

    with open(index_path, "r", encoding="utf-8") as f:
        index_data = json.load(f)

    target_id = args.id
    target_entry = None
    if target_id:
        target_entry = next((e for e in index_data.get("entries", []) if e.get("handoff_id") == target_id), None)
    else:
        ready_entries = [e for e in index_data.get("entries", []) if e.get("status") == "ready"]
        if ready_entries:
            target_entry = ready_entries[-1]
            target_id = target_entry.get("handoff_id")

    if not target_entry:
        print(f"ERROR: No se encontró ningún handoff en estado 'ready' para consumir.", file=sys.stderr)
        return 1

    if target_entry.get("status") == "consumed":
        print(f"AVISO: El handoff '{target_id}' ya está marcado como 'consumed'.")
        return 0

    handoff_file = root / target_entry["path"]
    if not handoff_file.exists():
        print(f"ERROR: Archivo {handoff_file} no existe", file=sys.stderr)
        return 1

    actual_sha = sha256_file(handoff_file)
    if actual_sha != target_entry.get("sha256"):
        print(f"ERROR: Hash de {handoff_file} no coincide con INDEX.json", file=sys.stderr)
        return 1

    consumer = args.by or os.environ.get("AI_PLATFORM") or "antigravity"
    consume_time = now_iso()

    # 1. Actualizar INDEX.json por merge
    target_entry["status"] = "consumed"
    target_entry["consumed_by"] = consumer
    target_entry["consumed_at"] = consume_time
    index_data["updated_at"] = consume_time

    schema_path = root / "schemas" / "handoff-index.schema.json"
    ok, err = validate_schema(index_data, schema_path)
    if not ok:
        print(f"ERROR: Validación de INDEX.json falló: {err}", file=sys.stderr)
        return 1

    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    # 2. Actualizar session-state.json local si existe el workspace
    workspace = Path(args.workspace).resolve() if args.workspace else Path.cwd().resolve()
    local_state_path = workspace / ".agents" / "antigravity-router" / "session-state.json"
    if local_state_path.exists():
        try:
            with open(local_state_path, "r", encoding="utf-8") as f:
                s_data = json.load(f)

            if "handoff" not in s_data:
                s_data["handoff"] = {}

            s_data["handoff"]["handoff_id"] = target_id
            s_data["handoff"]["status"] = "consumed"
            s_data["handoff"]["consumed_by"] = consumer
            s_data["handoff"]["consumed_at"] = consume_time
            s_data["handoff"]["sha256"] = actual_sha

            with open(local_state_path, "w", encoding="utf-8") as f:
                json.dump(s_data, f, indent=2, ensure_ascii=False)
                f.write("\n")
            print(f"session-state.json actualizado por merge en {local_state_path}")
        except Exception as e:
            print(f"AVISO: No se pudo actualizar session-state.json: {e}", file=sys.stderr)

    print(f"Handoff '{target_id}' consumido exitosamente por '{consumer}' a las {consume_time}.")
    return 0


# -----------------------------------------------------------------------------
# Subcomando: handoff create
# -----------------------------------------------------------------------------

def cmd_handoff_create(args: argparse.Namespace) -> int:
    root = get_shared_root()
    index_path = root / "runtime" / "handoffs" / "INDEX.json"
    workspace = Path(args.workspace).resolve() if args.workspace else Path.cwd().resolve()
    git_info = detect_git_info(workspace)

    handoff_id = args.id or f"handoff-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"
    created_at = now_iso()
    platform = args.platform or os.environ.get("AI_PLATFORM") or "antigravity"
    surface = args.surface or "agent_cli"
    objective = args.objective or "Continuación de sesión de trabajo"

    handoff_obj: Dict[str, Any] = {
        "schema_version": "1.1",
        "handoff_id": handoff_id,
        "created_at": created_at,
        "protocol_version": "1.0.2-draft",
        "operating_level": 7,
        "source": {
            "platform": platform,
            "surface": surface,
            "model": args.model or "unknown",
            "session_id": args.session_id or f"session_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
        },
        "scope": {
            "context_mode": "project" if workspace.exists() else "general",
            "project_id": workspace.name,
            "project_root": str(workspace).replace("\\", "/"),
            "git_branch": git_info["branch"],
            "topic_id": None,
        },
        "objective": objective,
        "status": "ready",
        "completed": args.completed or ["Inicio de handoff formal"],
        "validated": [],
        "decisions": [],
        "files_changed": [],
        "errors": [],
        "risks": [],
        "unresolved": [],
        "next_actions": args.next_actions or ["Continuar tareas en la siguiente sesión"],
        "authority_sources": [
            "AI_WORKSPACE_PROTOCOL.md"
        ],
        "checkpoints": [],
        "log_refs": [],
        "knowledge_candidates": [],
        "privacy": {
            "classification": "internal",
            "secrets_included": False,
            "redactions": [],
        },
    }

    if git_info["is_git"] and git_info["head"]:
        handoff_obj["checkpoints"].append({
            "type": "git_commit",
            "ref": git_info["head"],
            "description": f"Rama {git_info['branch']}, árbol limpio: {git_info['clean']}",
        })

    if args.json_input:
        j_path = Path(args.json_input).resolve()
        if j_path.exists():
            with open(j_path, "r", encoding="utf-8") as f:
                extra = json.load(f)
            for k, v in extra.items():
                if k in handoff_obj and isinstance(handoff_obj[k], list) and isinstance(v, list):
                    handoff_obj[k].extend(v)
                elif k in handoff_obj and isinstance(handoff_obj[k], dict) and isinstance(v, dict):
                    handoff_obj[k].update(v)
                else:
                    handoff_obj[k] = v

    schema_path = root / "schemas" / "handoff.schema.json"
    ok, err = validate_schema(handoff_obj, schema_path)
    if not ok:
        print(f"ERROR: El objeto handoff no cumple el esquema: {err}", file=sys.stderr)
        return 1

    handoff_dir = root / "runtime" / "handoffs" / handoff_id
    handoff_dir.mkdir(parents=True, exist_ok=True)
    target_json = handoff_dir / "handoff.json"
    target_md = handoff_dir / "handoff.md"

    with open(target_json, "w", encoding="utf-8") as f:
        json.dump(handoff_obj, f, indent=2, ensure_ascii=False)
        f.write("\n")

    md_content = f"""# Handoff — {objective}

- **Objetivo:** {objective}
- **Estado:** ready
- **Próxima acción inmediata:** {handoff_obj['next_actions'][0] if handoff_obj['next_actions'] else 'N/D'}

## 1. Contexto y alcance
- **Protocolo:** `1.0.2-draft` · **Nivel operativo:** `7` · **context_mode:** `{handoff_obj['scope']['context_mode']}`
- **Proyecto:** `{handoff_obj['scope']['project_id']}` · **Raíz:** `{handoff_obj['scope']['project_root']}`
- **Rama:** `{handoff_obj['scope']['git_branch']}`
- **Origen:** `{platform}` ({surface}), creado `{created_at}`

## 2. Próximas acciones
"""
    for i, act in enumerate(handoff_obj["next_actions"], start=1):
        md_content += f"{i}. {act}\n"

    md_content += "\n## 3. Logros completados\n"
    for comp in handoff_obj["completed"]:
        md_content += f"- {comp}\n"

    md_content += "\n## 4. Privacidad\n- Clasificación `internal`; sin secretos.\n"

    with open(target_md, "w", encoding="utf-8") as f:
        f.write(md_content)

    h_sha = sha256_file(target_json)

    index_data = load_or_init_index(index_path)

    scope_k = handoff_obj["scope"]["project_id"]
    for e in index_data.get("entries", []):
        if e.get("scope_key") == scope_k and e.get("status") == "ready":
            e["status"] = "superseded"

    new_entry = {
        "scope_key": scope_k,
        "context_mode": handoff_obj["scope"]["context_mode"],
        "workspace": handoff_obj["scope"]["project_root"],
        "handoff_id": handoff_id,
        "path": f"runtime/handoffs/{handoff_id}/handoff.json",
        "sha256": h_sha,
        "status": "ready",
        "created_at": created_at,
        "source_platform": platform,
        "consumed_by": None,
        "consumed_at": None,
    }
    index_data.setdefault("entries", []).append(new_entry)
    index_data["updated_at"] = created_at

    index_schema = root / "schemas" / "handoff-index.schema.json"
    ok, err = validate_schema(index_data, index_schema)
    if not ok:
        print(f"ERROR: INDEX.json no valida contra esquema: {err}", file=sys.stderr)
        return 1

    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    local_state = workspace / ".agents" / "antigravity-router" / "session-state.json"
    if local_state.exists():
        try:
            with open(local_state, "r", encoding="utf-8") as f:
                s_data = json.load(f)
            s_data["handoff"] = {
                "handoff_id": handoff_id,
                "index": str(index_path).replace("\\", "/"),
                "path": f"runtime/handoffs/{handoff_id}/handoff.json",
                "sha256": h_sha,
                "status": "ready",
                "protocol_version": "1.0.2-draft",
            }
            with open(local_state, "w", encoding="utf-8") as f:
                json.dump(s_data, f, indent=2, ensure_ascii=False)
                f.write("\n")
            print(f"session-state.json actualizado en {local_state}")
        except Exception as e:
            print(f"AVISO: No se pudo actualizar session-state.json: {e}", file=sys.stderr)

    print(f"Handoff '{handoff_id}' creado exitosamente (SHA-256: {h_sha}).")
    print(f"JSON : {target_json}")
    print(f"MD   : {target_md}")
    return 0


# -----------------------------------------------------------------------------
# Subcomandos: handoff export / import (ChatGPT Web Bridge)
# -----------------------------------------------------------------------------

def cmd_handoff_export(args: argparse.Namespace) -> int:
    """Exporta un handoff en formato de bloque portable para pegar en ChatGPT Web."""
    root = get_shared_root()
    index_path = root / "runtime" / "handoffs" / "INDEX.json"
    if not index_path.exists():
        print(f"ERROR: {index_path} no existe", file=sys.stderr)
        return 1

    with open(index_path, "r", encoding="utf-8") as f:
        index_data = json.load(f)

    target_id = args.id
    target_entry = None
    if target_id:
        target_entry = next((e for e in index_data.get("entries", []) if e.get("handoff_id") == target_id), None)
    else:
        # Último handoff disponible
        if index_data.get("entries"):
            target_entry = index_data["entries"][-1]

    if not target_entry:
        print("ERROR: No se encontró ningún handoff para exportar.", file=sys.stderr)
        return 1

    handoff_file = root / target_entry["path"]
    if not handoff_file.exists():
        print(f"ERROR: Archivo {handoff_file} no encontrado.", file=sys.stderr)
        return 1

    with open(handoff_file, "r", encoding="utf-8") as f:
        handoff_obj = json.load(f)

    # Construir bloque markdown
    export_payload = f"""# AI Workspace Protocol — Relevo de Sesión para ChatGPT Web

Copiá este mensaje completo y pegalo en el chat de **ChatGPT**:

---

Hola ChatGPT. Te transfiero la sesión de trabajo bajo el **AI Workspace Protocol (AIWP)** en Nivel 7.
A continuación tenés el handoff de continuidad de la sesión:

```aiwp-handoff
{json.dumps(handoff_obj, indent=2, ensure_ascii=False)}
```

Por favor, confirmá la recepción de este handoff, reportá tu diagnóstico de inicio (§3) y continuá con la primera de las `next_actions`.
"""

    if args.output:
        out_p = Path(args.output).resolve()
        out_p.write_text(export_payload, encoding="utf-8")
        print(f"Payload de relevo exportado exitosamente en: {out_p}")
    else:
        print(export_payload)

    return 0


def cmd_handoff_import(args: argparse.Namespace) -> int:
    """Importa un bloque handoff generado por ChatGPT Web o archivo externo y lo registra localmente."""
    root = get_shared_root()
    index_path = root / "runtime" / "handoffs" / "INDEX.json"

    raw_text = None
    if args.file:
        fpath = Path(args.file).resolve()
        if not fpath.exists():
            print(f"ERROR: Archivo no encontrado: {fpath}", file=sys.stderr)
            return 1
        raw_text = fpath.read_text(encoding="utf-8")
    elif args.text:
        raw_text = args.text
    else:
        print("Leyendo handoff desde entrada estándar (presione Ctrl+D o Ctrl+Z para finalizar)...")
        raw_text = sys.stdin.read()

    if not raw_text or not raw_text.strip():
        print("ERROR: No se proporcionó ningún texto de handoff.", file=sys.stderr)
        return 1

    # Extraer JSON de un bloque ```aiwp-handoff ... ``` si existe
    m = re.search(r"```(?:aiwp-handoff|json)?\s*(\{.*?\})\s*```", raw_text, re.DOTALL)
    if m:
        json_str = m.group(1)
    else:
        json_str = raw_text.strip()

    try:
        handoff_obj = json.loads(json_str)
    except Exception as e:
        print(f"ERROR: No se pudo parsear el JSON del handoff: {e}", file=sys.stderr)
        return 1

    # Validar schema
    schema_path = root / "schemas" / "handoff.schema.json"
    ok, err = validate_schema(handoff_obj, schema_path)
    if not ok:
        print(f"ERROR: El handoff importado no cumple con el esquema: {err}", file=sys.stderr)
        return 1

    handoff_id = handoff_obj.get("handoff_id")
    if not handoff_id:
        print("ERROR: El handoff no tiene 'handoff_id'.", file=sys.stderr)
        return 1

    # Escribir en runtime/handoffs/<id>/
    handoff_dir = root / "runtime" / "handoffs" / handoff_id
    handoff_dir.mkdir(parents=True, exist_ok=True)
    target_json = handoff_dir / "handoff.json"
    target_md = handoff_dir / "handoff.md"

    with open(target_json, "w", encoding="utf-8") as f:
        json.dump(handoff_obj, f, indent=2, ensure_ascii=False)
        f.write("\n")

    # Generar handoff.md correspondiente
    md_content = f"""# Handoff — {handoff_obj.get('objective', 'Importado desde ChatGPT')}

- **Objetivo:** {handoff_obj.get('objective')}
- **Estado:** {handoff_obj.get('status', 'ready')}
- **Próxima acción inmediata:** {handoff_obj.get('next_actions', ['N/D'])[0]}

## 1. Contexto y alcance
- **Protocolo:** `{handoff_obj.get('protocol_version')}` · **Nivel operativo:** `{handoff_obj.get('operating_level')}`
- **Proyecto:** `{handoff_obj.get('scope', {}).get('project_id')}`
- **Origen:** `{handoff_obj.get('source', {}).get('platform')}` ({handoff_obj.get('source', {}).get('surface')})
- **Creado:** `{handoff_obj.get('created_at')}`

## 2. Próximas acciones
"""
    for i, act in enumerate(handoff_obj.get("next_actions", []), start=1):
        md_content += f"{i}. {act}\n"

    with open(target_md, "w", encoding="utf-8") as f:
        f.write(md_content)

    h_sha = sha256_file(target_json)

    # Actualizar INDEX.json
    index_data = load_or_init_index(index_path)

    scope_k = handoff_obj.get("scope", {}).get("project_id", "general")
    # Si existía entrada en ready, superseded
    for e in index_data.get("entries", []):
        if e.get("scope_key") == scope_k and e.get("status") == "ready":
            e["status"] = "superseded"

    new_entry = {
        "scope_key": scope_k,
        "context_mode": handoff_obj.get("scope", {}).get("context_mode", "project"),
        "workspace": handoff_obj.get("scope", {}).get("project_root"),
        "handoff_id": handoff_id,
        "path": f"runtime/handoffs/{handoff_id}/handoff.json",
        "sha256": h_sha,
        "status": handoff_obj.get("status", "ready"),
        "created_at": handoff_obj.get("created_at", now_iso()),
        "source_platform": handoff_obj.get("source", {}).get("platform", "chatgpt"),
        "consumed_by": None,
        "consumed_at": None,
    }
    index_data.setdefault("entries", []).append(new_entry)
    index_data["updated_at"] = now_iso()

    index_schema = root / "schemas" / "handoff-index.schema.json"
    ok, err = validate_schema(index_data, index_schema)
    if not ok:
        print(f"ERROR: INDEX.json inválido tras importación: {err}", file=sys.stderr)
        return 1

    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    # Actualizar router si se puede inferir workspace
    ws_str = handoff_obj.get("scope", {}).get("project_root")
    if ws_str and Path(ws_str).exists():
        local_state = Path(ws_str) / ".agents" / "antigravity-router" / "session-state.json"
        if local_state.exists():
            try:
                with open(local_state, "r", encoding="utf-8") as f:
                    s_data = json.load(f)
                s_data["handoff"] = {
                    "handoff_id": handoff_id,
                    "index": str(index_path).replace("\\", "/"),
                    "path": f"runtime/handoffs/{handoff_id}/handoff.json",
                    "sha256": h_sha,
                    "status": handoff_obj.get("status", "ready"),
                    "protocol_version": "1.0.2-draft",
                }
                with open(local_state, "w", encoding="utf-8") as f:
                    json.dump(s_data, f, indent=2, ensure_ascii=False)
                    f.write("\n")
                print(f"session-state.json actualizado por merge en {local_state}")
            except Exception as e:
                print(f"AVISO: No se pudo actualizar session-state.json: {e}", file=sys.stderr)

    print(f"Handoff '{handoff_id}' importado y registrado exitosamente (SHA-256: {h_sha}).")
    return 0


# -----------------------------------------------------------------------------
# Main entrypoint
# -----------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        prog="ai-protocol",
        description="Runtime CLI para el AI Workspace Protocol (AIWP).",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # status
    p_status = subparsers.add_parser("status", help="Diagnóstico §3 y bootstrap de sesión.")
    p_status.add_argument("--workspace", "-w", help="Ruta del workspace a evaluar.")
    p_status.add_argument("--platform", "-p", help="Nombre de plataforma observada.")
    p_status.add_argument("--json", action="store_true", help="Salida estructurada en JSON.")

    # verify
    p_verify = subparsers.add_parser("verify", help="Verifica MANIFEST_SHA256 y esquemas JSON.")

    # adapters
    p_adapters = subparsers.add_parser("adapters", help="Gestión y control de adaptadores (§9).")
    a_sub = p_adapters.add_subparsers(dest="subcommand", required=True)

    a_check = a_sub.add_parser("check", help="Comprueba estado y posibles derivas de hash en adaptadores.")
    a_check.add_argument("--json", action="store_true", help="Salida en JSON.")

    a_deploy = a_sub.add_parser("deploy", help="Despliega o actualiza un adaptador desde su plantilla maestra.")
    a_deploy.add_argument("--target", "-t", required=True, choices=["antigravity", "claude_code", "chatgpt"], help="Plataforma objetivo.")
    a_deploy.add_argument("--dry-run", action="store_true", help="Muestra el contenido sin escribir.")

    # handoff
    p_handoff = subparsers.add_parser("handoff", help="Gestión de handoffs.")
    h_sub = p_handoff.add_subparsers(dest="subcommand", required=True)

    # handoff list
    h_list = h_sub.add_parser("list", help="Lista handoffs registrados en INDEX.json.")
    h_list.add_argument("--status", choices=["ready", "consumed", "superseded", "blocked"], help="Filtrar por estado.")
    h_list.add_argument("--scope", help="Filtrar por scope_key (proyecto o tema).")
    h_list.add_argument("--json", action="store_true", help="Salida en JSON.")

    # handoff inspect
    h_inspect = h_sub.add_parser("inspect", help="Inspecciona y valida un handoff.")
    h_inspect.add_argument("--id", help="Handoff ID específico a inspeccionar.")
    h_inspect.add_argument("--path", help="Ruta de un archivo handoff.json.")
    h_inspect.add_argument("--workspace", "-w", help="Workspace para validar claims y session-state.")
    h_inspect.add_argument("--strict-scope", action="store_true", help="Limitar descubrimiento al scope.")
    h_inspect.add_argument("--json", action="store_true", help="Salida en JSON.")

    # handoff consume
    h_consume = h_sub.add_parser("consume", help="Consume un handoff validado por merge.")
    h_consume.add_argument("--id", help="Handoff ID específico a consumir.")
    h_consume.add_argument("--by", help="Nombre del asistente que consume (ej. antigravity, claude-code, codex).")
    h_consume.add_argument("--workspace", "-w", help="Workspace donde actualizar session-state.json.")

    # handoff create
    h_create = h_sub.add_parser("create", help="Crea un nuevo handoff interoperable.")
    h_create.add_argument("--id", help="Handoff ID personalizado.")
    h_create.add_argument("--objective", "-o", help="Objetivo principal del handoff.")
    h_create.add_argument("--next-actions", "-n", action="append", help="Próxima acción inmediata (repetible).")
    h_create.add_argument("--completed", "-c", action="append", help="Tarea completada (repetible).")
    h_create.add_argument("--platform", help="Plataforma emisora.")
    h_create.add_argument("--surface", help="Superficie emisora.")
    h_create.add_argument("--model", help="Modelo emisor.")
    h_create.add_argument("--session-id", help="ID de sesión.")
    h_create.add_argument("--workspace", "-w", help="Workspace del handoff.")
    h_create.add_argument("--json-input", help="Archivo JSON con metadatos adicionales.")

    # handoff export (ChatGPT Web Bridge)
    h_export = h_sub.add_parser("export", help="Exporta un handoff formateado para transferir a ChatGPT Web.")
    h_export.add_argument("--id", help="Handoff ID a exportar (por defecto, el último).")
    h_export.add_argument("--output", "-o", help="Ruta de archivo donde guardar el payload.")

    # handoff import (ChatGPT Web Bridge)
    h_import = h_sub.add_parser("import", help="Importa y valida un handoff generado por ChatGPT Web u otra IA externa.")
    h_import.add_argument("--file", "-f", help="Ruta del archivo con el handoff o bloque aiwp-handoff.")
    h_import.add_argument("--text", "-t", help="Cadena de texto con el bloque aiwp-handoff.")

    args = parser.parse_args()

    if args.command == "status":
        return cmd_status(args)
    elif args.command == "verify":
        return cmd_verify(args)
    elif args.command == "adapters":
        if args.subcommand == "check":
            return cmd_adapters_check(args)
        elif args.subcommand == "deploy":
            return cmd_adapters_deploy(args)
    elif args.command == "handoff":
        if args.subcommand == "list":
            return cmd_handoff_list(args)
        elif args.subcommand == "inspect":
            return cmd_handoff_inspect(args)
        elif args.subcommand == "consume":
            return cmd_handoff_consume(args)
        elif args.subcommand == "create":
            return cmd_handoff_create(args)
        elif args.subcommand == "export":
            return cmd_handoff_export(args)
        elif args.subcommand == "import":
            return cmd_handoff_import(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
