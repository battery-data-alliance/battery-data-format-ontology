"""
Ontology quality checks: EMMOCheck and OWL RL reasoning.

Both checks are optional — they require ontopy / owlrl / Java and are
not run in routine CI. They can be invoked manually via ontology_toolkit.py.
"""
from __future__ import annotations

import logging
import os
import subprocess
import sys
from typing import Any

import rdflib

LOGGER = logging.getLogger(__name__)


def run_emmocheck(config: dict[str, Any]) -> None:
    """Run EMMOCheck on all configured TTL files."""
    ttl_files = config.get("ttl_files", [])
    if not ttl_files:
        LOGGER.error("No TTL files in config.")
        sys.exit(1)

    emmocheck_config = os.path.join(
        config["repo_root"], ".github", "utils", "emmocheck_config.yml"
    )

    for entry in ttl_files:
        path = entry["path"]
        title = entry.get("section_title", path)

        if not os.path.isfile(path):
            LOGGER.error("TTL file not found: %s", path)
            sys.exit(1)

        LOGGER.info("Running EMMOCheck on %s (%s)…", title, path)
        cmd = [
            "emmocheck",
            "--verbose",
            "--url-from-catalog",
            "--skip", "test_namespace",
            "--skip", "test_quantity_dimension",
        ]
        if os.path.isfile(emmocheck_config):
            cmd += ["--configfile", emmocheck_config]

        result = subprocess.run(cmd + [path])
        if result.returncode != 0:
            LOGGER.error("EMMOCheck failed for %s", path)
            sys.exit(result.returncode)

    LOGGER.info("All EMMOCheck passes.")


def run_reasoner_check(config: dict[str, Any]) -> None:
    """
    Load the ontology, expand with OWL 2 RL reasoning, and verify that
    triples are inferred. Saves the expanded graph to the inferred TTL path
    configured in config.yml.
    """
    try:
        from owlrl import DeductiveClosure, OWLRL_Semantics
    except ImportError:
        LOGGER.error(
            "--run-reasoner-check requires owlrl. Install with: pip install \".[ontopy]\""
        )
        sys.exit(1)

    ttl_files = config.get("ttl_files", [])
    if not ttl_files:
        LOGGER.error("No TTL files in config.")
        sys.exit(1)

    # Prefer a file with "core" or "main" in its section title; fall back to first.
    main_file = next(
        (
            f["path"] for f in ttl_files
            if "core" in f.get("section_title", "").lower()
            or f.get("section_title", "").lower() == "main ontology"
        ),
        ttl_files[0]["path"],
    )

    full_path = os.path.join(config["repo_root"], main_file)
    if not os.path.isfile(full_path):
        LOGGER.error("Ontology file not found: %s", full_path)
        sys.exit(1)

    g = rdflib.Graph()
    try:
        g.parse(full_path, format="ttl")
        LOGGER.info("Loaded %s (%d triples before reasoning)", full_path, len(g))
    except Exception as exc:
        LOGGER.error("Failed to parse %s: %s", full_path, exc)
        sys.exit(1)

    try:
        DeductiveClosure(OWLRL_Semantics).expand(g)
        LOGGER.info("OWL 2 RL reasoning complete (%d triples after)", len(g))
    except Exception as exc:
        LOGGER.error("Reasoning failed: %s", exc)
        sys.exit(1)

    if len(g) == 0:
        LOGGER.error("No triples in graph after reasoning — something is wrong.")
        sys.exit(1)

    inferred_filename = config.get("inferred_ttl_filename", "")
    if inferred_filename:
        out_path = os.path.join(config["repo_root"], inferred_filename)
        g.serialize(destination=out_path, format="turtle")
        LOGGER.info("Inferred TTL saved to %s", out_path)
        print(f"Inferred TTL saved to {out_path}")
