"""
BDA Ontology Toolkit — command-line entry point.

Delegates to focused modules:
  config.py      — project configuration loading
  context_gen.py — JSON-LD context generation
  rst_gen.py     — RST documentation generation
  checks.py      — EMMOCheck and OWL reasoner

Usage:
  python .github/scripts/ontology_toolkit.py --help
"""
from __future__ import annotations

import argparse
import logging
import os
import sys

# Ensure sibling modules are importable regardless of working directory.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import checks
import config as cfg
import context_gen
import rst_gen

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="ontology_toolkit",
        description="BDA Ontology Toolkit — build, validate, and publish ontology artefacts.",
    )
    p.add_argument(
        "--print-env",
        action="store_true",
        help="Print config as KEY=VALUE lines for $GITHUB_ENV.",
    )
    p.add_argument(
        "--print-ttl-files",
        action="store_true",
        help="Print space-separated TTL file paths.",
    )
    p.add_argument(
        "--generate-context",
        action="store_true",
        help="Generate lean JSON-LD context (context/context.json).",
    )
    p.add_argument(
        "--generate-context-full",
        action="store_true",
        help=(
            "Generate full EMMO-loaded context (context/context-full.json). "
            "Requires the inferred TTL. Manual/debug use only."
        ),
    )
    p.add_argument(
        "--generate-rst",
        action="store_true",
        help="Generate RST documentation from TTL. Requires ontopy.",
    )
    p.add_argument(
        "--run-emmocheck",
        action="store_true",
        help="Run EMMOCheck on all configured TTL files.",
    )
    p.add_argument(
        "--run-reasoner-check",
        action="store_true",
        help="Run OWL 2 RL reasoner check. Requires owlrl.",
    )
    return p


def main() -> None:
    args = _build_parser().parse_args()

    # Load config once; pass to all sub-commands.
    config = cfg.load_config()

    if args.print_env:
        cfg.print_env_vars(config)

    if args.print_ttl_files:
        cfg.print_ttl_files(config)

    if args.generate_context:
        context_gen.write_lean_context(config)

    if args.generate_context_full:
        context_gen.write_full_context(config)

    if args.generate_rst:
        rst_gen.generate_rst(config)

    if args.run_emmocheck:
        checks.run_emmocheck(config)

    if args.run_reasoner_check:
        checks.run_reasoner_check(config)


if __name__ == "__main__":
    main()
