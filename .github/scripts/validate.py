"""
Ontology project CI validation script.

Checks (all exit non-zero on failure):
  1. All configured TTL files parse as valid Turtle
  2. context/context.json and schema/schema.json are valid JSON
  3. config.yml is valid YAML
  4. schema.json contains the required BDF core columns
  5. schema.json contains the step-quantity columns (regression guard)
  6. Required columns are flagged csvw:required=true
  7. schema.json does not contain known-incorrect QUDT terms
  8. context.json declares the project namespace prefix and cross-vocab prefixes

Exit codes:
  0  All checks passed
  1  One or more checks failed
"""
from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path

import yaml
from rdflib import Graph

# Ensure sibling modules are importable regardless of working directory.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import load_config

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
LOGGER = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# BDF-specific column requirements (regression guards)
# ---------------------------------------------------------------------------
# Core columns — must be present in the canonical schema.
_CORE_REQUIRED = frozenset({
    "test_time_second",
    "voltage_volt",
    "current_ampere",
    "unix_time_second",
})

# Columns flagged csvw:required=true — derived from the ontology's obligation
# levels (unix_time_second is 'recommended', so present but not required).
_REQUIRED_FLAG = frozenset({
    "test_time_second",
    "voltage_volt",
    "current_ampere",
})

# Step-quantity columns added in fix/step-quantity-semantics.
# Listed separately so the error message names the relevant branch.
_STEP_COLUMNS = frozenset({"step_id", "step_type"})

# Known-incorrect QUDT terms: the validator fails if any appear in schema.json.
_BAD_QUDT_TERMS = frozenset({
    "unit:CountingUnit",   # QUDT class — use unit:NUM (a unit individual)
})

# Cross-vocabulary prefixes that must be declared in context.json.
_REQUIRED_CONTEXT_PREFIXES = frozenset({"emmo", "qudt", "quantitykind", "unit"})

# At least one column from each group must appear in a compliant BDF file.
# CSVW has no native oneOf constraint; this is enforced here and in SHACL shapes.
_AT_LEAST_ONE_OF: list[tuple[str, ...]] = [
    ("test_time_second", "unix_time_second"),
]


# ---------------------------------------------------------------------------
# Individual check functions
# ---------------------------------------------------------------------------

def _fail(msg: str) -> None:
    print(f"\nFAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def check_ttl(paths: list[Path]) -> None:
    print("Checking TTL files…")
    for path in paths:
        if not path.exists():
            _fail(f"Missing TTL file: {path}")
        g = Graph()
        try:
            g.parse(path, format="turtle")
        except Exception as exc:
            _fail(f"TTL parse error in {path}: {exc}")
        print(f"  OK  {path.name}  ({len(g)} triples)")


def check_json(paths: list[Path]) -> None:
    print("Checking JSON files…")
    for path in paths:
        if not path.exists():
            _fail(f"Missing JSON file: {path}")
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            _fail(f"JSON parse error in {path}: {exc}")
        print(f"  OK  {path.name}")


def check_yaml(paths: list[Path]) -> None:
    print("Checking YAML files…")
    for path in paths:
        if not path.exists():
            _fail(f"Missing YAML file: {path}")
        try:
            yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            _fail(f"YAML parse error in {path}: {exc}")
        print(f"  OK  {path.name}")


def check_schema(schema_path: Path) -> None:
    print("Checking schema.json content…")
    if not schema_path.exists():
        _fail(f"Missing schema file: {schema_path}")

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    columns = schema.get("csvw:columns", [])
    col_names = {col.get("csvw:name") for col in columns}

    missing_core = _CORE_REQUIRED - col_names
    if missing_core:
        _fail(f"schema.json missing required core columns: {sorted(missing_core)}")

    missing_step = _STEP_COLUMNS - col_names
    if missing_step:
        _fail(
            f"schema.json missing step-quantity columns: {sorted(missing_step)}\n"
            "  (These were introduced in fix/step-quantity-semantics.)"
        )

    not_required = [
        name for col in columns
        if (name := col.get("csvw:name")) in _REQUIRED_FLAG
        and not col.get("csvw:required", False)
    ]
    if not_required:
        _fail(f"Columns should have csvw:required=true: {sorted(not_required)}")

    # Verify that the schema declares at least one column from each "at least one of" group.
    # (CSVW cannot express this natively; we check it here and via SHACL shapes.)
    for group in _AT_LEAST_ONE_OF:
        if not any(name in col_names for name in group):
            _fail(
                f"schema.json must define at least one of: {list(group)}\n"
                "  (Cross-column constraint — CSVW has no native oneOf syntax.)"
            )

    schema_text = schema_path.read_text(encoding="utf-8")
    for bad in _BAD_QUDT_TERMS:
        if bad in schema_text:
            _fail(
                f"schema.json contains '{bad}' which is a QUDT class, not a unit individual.\n"
                f"  Replace with the correct QUDT unit individual (e.g. unit:NUM)."
            )

    print(f"  OK  schema.json  ({len(col_names)} columns)")


def check_context(context_path: Path, project_prefix_key: str) -> None:
    print("Checking context.json content…")
    if not context_path.exists():
        _fail(f"Missing context file: {context_path}")

    ctx = json.loads(context_path.read_text(encoding="utf-8"))
    inner = ctx.get("@context", {})

    if project_prefix_key not in inner:
        _fail(
            f"context.json is missing the '{project_prefix_key}:' project prefix.\n"
            "  Run: python .github/scripts/ontology_toolkit.py --generate-context"
        )

    missing_vocab = _REQUIRED_CONTEXT_PREFIXES - inner.keys()
    if missing_vocab:
        _fail(
            f"context.json is missing cross-vocabulary prefixes: {sorted(missing_vocab)}\n"
            "  Run: python .github/scripts/ontology_toolkit.py --generate-context"
        )

    print(f"  OK  context.json  ({len(inner)} terms, all required prefixes present)")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    config = load_config()
    root = Path(config["repo_root"])

    ttl_paths = [root / f["path"] for f in config["ttl_files"]]

    print("=" * 60)
    check_ttl(ttl_paths)

    print()
    check_json([root / "context" / "context.json", root / "schema" / "schema.json"])

    print()
    check_yaml([root / "config.yml"])

    print()
    check_schema(root / "schema" / "schema.json")

    print()
    # Derive the short namespace key from config (same logic as context_gen.py).
    ns = config["ontology_prefix"].rstrip("#/")
    short_key = ns.split("/")[-1].split("#")[0].lower() or "ont"
    parts = short_key.replace("-", " ").split()
    if len(parts) >= 2:
        short_key = "".join(p[0] for p in parts)
    check_context(root / "context" / "context.json", short_key)

    print()
    print("=" * 60)
    print("All checks passed.")


if __name__ == "__main__":
    main()
