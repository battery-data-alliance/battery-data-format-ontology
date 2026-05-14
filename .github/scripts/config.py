"""
Ontology project configuration loader.

Reads config.yml, searches upward from the calling script's directory,
and returns a typed dict of project settings. All other toolkit modules
import from here rather than duplicating config logic.
"""
from __future__ import annotations

import json
import logging
import os
import sys
from typing import Any

import yaml

LOGGER = logging.getLogger(__name__)


def find_repo_root(start: str | None = None) -> str:
    """
    Walk upward from *start* (default: this file's directory) until a
    directory containing ``config.yml`` is found. Returns that directory.

    Override the search by setting the ``CONFIG_PATH`` environment variable
    to the absolute path of a specific config.yml file.
    """
    override = os.environ.get("CONFIG_PATH")
    if override:
        override = os.path.abspath(override)
        if os.path.isfile(override):
            return os.path.dirname(override)
        LOGGER.warning("CONFIG_PATH='%s' does not point to a file; ignoring.", override)

    current = os.path.abspath(start or os.path.dirname(__file__))
    while True:
        if os.path.isfile(os.path.join(current, "config.yml")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            LOGGER.error("config.yml not found (searched upward from %s)", start or __file__)
            sys.exit(1)
        current = parent


def load_config(repo_root: str | None = None) -> dict[str, Any]:
    """
    Load and validate config.yml from the repository root.

    Returns a normalized dict with the following guaranteed keys:
      ontology_name, ontology_uri, ontology_prefix, ontology_description,
      ttl_files, inferred_ttl_filename, rst_output_filename
    """
    root = repo_root or find_repo_root()
    config_path = os.path.join(root, "config.yml")
    try:
        with open(config_path, encoding="utf-8") as fh:
            raw = yaml.safe_load(fh)
    except Exception as exc:
        LOGGER.error("Failed to load %s: %s", config_path, exc)
        sys.exit(1)

    if not isinstance(raw, dict):
        LOGGER.error("config.yml is empty or not a mapping: %s", config_path)
        sys.exit(1)

    required = ("ontology_name", "ontology_uri", "ontology_prefix")
    missing = [k for k in required if not raw.get(k)]
    if missing:
        LOGGER.error("config.yml is missing required keys: %s", missing)
        sys.exit(1)

    output = raw.get("output", {}) or {}
    return {
        "repo_root":             root,
        "ontology_name":         raw["ontology_name"],
        "ontology_noun":         raw.get("ontology_noun", ""),
        "ontology_adjective":    raw.get("ontology_adjective", ""),
        "ontology_uri":          raw["ontology_uri"],
        "ontology_prefix":       raw["ontology_prefix"],
        "ontology_description":  raw.get("ontology_description", ""),
        "ttl_files":             raw.get("ttl_files", []),
        "inferred_ttl_filename": output.get("inferred_ttl", ""),
        "rst_output_filename":   output.get("rst_file", "docs/ontology.rst"),
        "emmocheck_classes":     raw.get("emmocheck_classes", []),
    }


def print_ttl_files(config: dict[str, Any] | None = None) -> None:
    """Print space-separated TTL paths for shell consumption."""
    cfg = config or load_config()
    print(" ".join(f["path"] for f in cfg["ttl_files"]))


def print_env_vars(config: dict[str, Any] | None = None) -> None:
    """Print KEY=VALUE lines suitable for appending to $GITHUB_ENV."""
    cfg = config or load_config()
    lines = [
        f"ONTOLOGY_NAME={cfg['ontology_name']}",
        f"ONTOLOGY_URI={cfg['ontology_uri']}",
        f"ONTOLOGY_IRI={cfg['ontology_uri']}",
        f"RST_FILE={cfg['rst_output_filename']}",
        f"INFERRED_TTL_FILENAME={cfg['inferred_ttl_filename']}",
        f"ONTOLOGY_FILE_BASE={cfg['ontology_noun']}",
        f"TTL_FILES_JSON={json.dumps([f['path'] for f in cfg['ttl_files']])}",
    ]
    print("\n".join(lines))
