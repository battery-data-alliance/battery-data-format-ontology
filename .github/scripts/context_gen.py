"""
JSON-LD context generation for EMMO-based ontologies.

Two modes:
  generate_lean_context(ttl_path, config)
      Reads only the primary TTL (no imports fetched). Emits entries solely
      for subjects whose IRI falls within the project's own namespace, plus
      a standard set of W3C / cross-vocabulary prefix shortcuts. Output is
      small (<10 KB) and suitable for serving as the default machine-readable
      context for CSV annotations and schema documents.

  generate_full_context(inferred_ttl_path)
      Reads an inferred TTL that has been expanded with all EMMO imports.
      Output is large (~500 KB) and intended only for manual/debug use.
"""
from __future__ import annotations

import json
import logging
import os
import sys
from typing import Any

import rdflib
from rdflib.namespace import OWL, RDF, SKOS

LOGGER = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Default cross-vocabulary prefixes included in every lean context.
# These are appropriate for any EMMO-based domain ontology; the project-
# specific namespace prefix is added dynamically from config.
# ---------------------------------------------------------------------------
_DEFAULT_PREFIXES: dict[str, str] = {
    "csvw":         "http://www.w3.org/ns/csvw#",
    "dc":           "http://purl.org/dc/elements/1.1/",
    "dcterms":      "http://purl.org/dc/terms/",
    "emmo":         "https://w3id.org/emmo#",
    "owl":          "http://www.w3.org/2002/07/owl#",
    "qudt":         "http://qudt.org/schema/qudt/",
    "quantitykind": "http://qudt.org/vocab/quantitykind/",
    "rdf":          "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs":         "http://www.w3.org/2000/01/rdf-schema#",
    "schema":       "https://schema.org/",
    "skos":         "http://www.w3.org/2004/02/skos/core#",
    "sosa":         "http://www.w3.org/ns/sosa/",
    "ssn":          "http://www.w3.org/ns/ssn/",
    "unit":         "http://qudt.org/vocab/unit/",
    "xsd":          "http://www.w3.org/2001/XMLSchema#",
}

# EMMO object property always included so schema documents can use
# hasMeasurementUnit without importing EMMO.
_EMMO_OBJECT_PROPERTIES: dict[str, Any] = {
    "hasMeasurementUnit": {
        "@id":   "https://w3id.org/emmo#EMMO_bed1d005_b04e_4a90_94cf_02bc678a8569",
        "@type": "@id",
    },
}


def _ontology_version(graph: rdflib.Graph, ontology_uri: str) -> str:
    version_info = graph.value(rdflib.URIRef(ontology_uri), OWL.versionInfo)
    return str(version_info) if version_info else "unknown"


def generate_lean_context(ttl_path: str, config: dict[str, Any]) -> dict[str, Any]:
    """
    Build a lean JSON-LD context from *ttl_path*.

    Only subjects whose IRI starts with *config['ontology_prefix']* are
    included. Object properties are emitted with ``@type: @id``; all other
    labelled entities are emitted as plain IRI shortcuts.

    The short prefix key (e.g. ``"bdf"``) is derived from the prefix
    component of ``ontology_prefix`` — the substring before the final ``#``
    or ``/``, after the last ``/`` in the base URI. If the URI structure does
    not yield a clear short key, ``"ont"`` is used as a fallback.
    """
    ns = config["ontology_prefix"].rstrip("#/")
    # Derive a short key: last path segment of the base URI, lower-cased,
    # truncated to first three chars as a safe fallback.
    short_key = ns.split("/")[-1].split("#")[0].lower() or "ont"
    # Common abbreviations: battery-data-format → bdf, etc.
    parts = short_key.replace("-", " ").split()
    if len(parts) >= 2:
        short_key = "".join(p[0] for p in parts)

    g = rdflib.Graph()
    g.parse(ttl_path, format="turtle")

    project_ns = config["ontology_prefix"]
    class_entries: dict[str, str] = {}
    property_entries: dict[str, dict[str, str]] = {}

    for s, _p, o in g.triples((None, SKOS.prefLabel, None)):
        iri = str(s)
        if not iri.startswith(project_ns):
            continue
        label = str(o)
        local = iri[len(project_ns):]
        if (s, RDF.type, OWL.ObjectProperty) in g:
            property_entries[label] = {"@id": f"{short_key}:{local}", "@type": "@id"}
        else:
            class_entries[label] = f"{short_key}:{local}"

    version = _ontology_version(g, config["ontology_uri"])

    prefixes = {
        short_key: config["ontology_prefix"],
        **_DEFAULT_PREFIXES,
    }

    return {
        "@context": {
            **dict(sorted(prefixes.items())),
            **_EMMO_OBJECT_PROPERTIES,
            **dict(sorted(property_entries.items())),
            **dict(sorted(class_entries.items())),
        },
        "@id": f"{config['ontology_uri']}/{version}/context",
        "dcterms:version": version,
    }


def write_lean_context(config: dict[str, Any]) -> None:
    """Generate and write the lean context to ``context/context.json``."""
    ttl_files = config.get("ttl_files", [])
    if not ttl_files:
        LOGGER.error("No TTL files in config.")
        sys.exit(1)

    ttl_path = os.path.join(config["repo_root"], ttl_files[0]["path"])
    if not os.path.isfile(ttl_path):
        LOGGER.error("TTL file not found: %s", ttl_path)
        sys.exit(1)

    context_doc = generate_lean_context(ttl_path, config)

    out_dir = os.path.join(config["repo_root"], "context")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "context.json")
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(context_doc, fh, indent=4, ensure_ascii=False)

    LOGGER.info("Lean JSON-LD context saved to %s", out_path)
    print(f"JSON-LD context saved to {out_path}")


def write_full_context(config: dict[str, Any]) -> None:
    """
    Generate and write the full EMMO-loaded context to
    ``context/context-full.json``. Requires the inferred TTL to exist.

    This is a large file (~500 KB) intended only for manual/debug use.
    It is not generated in CI.
    """
    from urllib.parse import urljoin
    from urllib.request import pathname2url

    inferred = config.get("inferred_ttl_filename", "")
    if not inferred:
        LOGGER.error("inferred_ttl not configured in config.yml output section.")
        sys.exit(1)

    inferred_path = os.path.join(config["repo_root"], inferred)
    if not os.path.isfile(inferred_path):
        LOGGER.error(
            "Inferred TTL not found at %s. "
            "Run --run-reasoner-check first to generate it.",
            inferred_path,
        )
        sys.exit(1)

    file_uri = urljoin("file:", pathname2url(inferred_path))
    g = rdflib.Graph()
    g.parse(file_uri, format="ttl")

    object_properties: dict[str, Any] = {}
    other_entries: dict[str, str] = {}
    ns_prefixes: dict[str, str] = {}

    for s, p, o in g:
        if (s, RDF.type, OWL.ObjectProperty) in g:
            label = g.value(s, SKOS.prefLabel)
            if label:
                object_properties[str(label)] = {"@id": str(s), "@type": "@id"}
        elif p == SKOS.prefLabel:
            other_entries[str(o)] = str(s)

    for prefix, uri in g.namespace_manager.namespaces():
        if len(prefix) >= 2:
            ns_prefixes[prefix] = str(uri)

    context_doc = {
        "@context": {
            **dict(sorted(ns_prefixes.items())),
            **dict(sorted(object_properties.items())),
            **dict(sorted(other_entries.items())),
        }
    }

    out_dir = os.path.join(config["repo_root"], "context")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "context-full.json")
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(context_doc, fh, indent=4)

    LOGGER.info("Full JSON-LD context saved to %s", out_path)
    print(f"Full JSON-LD context saved to {out_path}")
