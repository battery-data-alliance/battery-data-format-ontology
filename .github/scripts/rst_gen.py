"""
RST documentation generator for EMMO-based ontologies.

Requires ontopy (EMMOntoPy) and owlready2. These are optional dependencies
installed via ``pip install ".[docs]"`` or ``pip install ".[ontopy]"``.
"""
from __future__ import annotations

import logging
import os
import re
import sys
from typing import Any

from rdflib.namespace import SKOS

LOGGER = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Annotation property display order
# ---------------------------------------------------------------------------
ANNOTATION_RANK = {
    "prefLabel":   "http://www.w3.org/2004/02/skos/core#prefLabel",
    "altLabel":    "http://www.w3.org/2004/02/skos/core#altLabel",
    "elucidation": "https://w3id.org/emmo#EMMO_967080e5_2f42_4eb2_a3a9_c58143e835f9",
    "comment":     "http://www.w3.org/2000/01/rdf-schema#comment",
    "example":     "http://www.w3.org/2004/02/skos/core#example",
    "seeAlso":     "http://www.w3.org/2000/01/rdf-schema#seeAlso",
    "isDefinedBy": "http://www.w3.org/2000/01/rdf-schema#isDefinedBy",
}

# Normalized annotation keys rendered as Sphinx admonitions instead of table rows
CALLOUTS: dict[str, tuple[str, str | None]] = {
    "note":      ("note",       None),
    "comment":   ("note",       None),
    "scopenote": ("note",       None),
    "example":   ("admonition", "Example"),
    "tip":       ("tip",        None),
    "caution":   ("caution",    None),
    "warning":   ("warning",    None),
    "important": ("important",  None),
    "danger":    ("danger",     None),
    "error":     ("error",      None),
}

_TABLE_SKIP_BASE = frozenset(
    {"iri", "preflabel", "subclassof", "subclasses", "restrictions", "deprecated",
     "wasderivedfrom"}
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def _indent(block: str, n: int = 3) -> str:
    pad = " " * n
    return "\n".join((pad + ln) if ln.strip() else "" for ln in block.splitlines())


def _linkify_value(val: str) -> str:
    if not isinstance(val, str):
        return val
    urls = re.findall(r"https?://[^\s;,]+", val)
    if not urls:
        return val
    if len(urls) == 1 and urls[0].lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".svg")):
        u = urls[0]
        return f'<a href="{u}"><img src="{u}" alt="{u}" style="max-width:400px;max-height:300px;"/></a>'
    return "; ".join(_html_link(u, u) for u in urls)


def _html_link(iri: str, label: str) -> str:
    frag = iri.split("#")[-1]
    return (
        f"<a href='#{frag}' "
        f"onclick=\"if(!document.getElementById('{frag}'))"
        f"{{window.location.href='{iri}';return false;}}\">"
        f"{label}</a>"
    )


def _html_table_row(label: str, value: str) -> str:
    return (
        "  <tr>\n"
        f"    <td class=\"element-table-key\"><span class=\"element-table-key\">{label}</span></td>\n"
        f"    <td class=\"element-table-value\">{value}</td>\n"
        "  </tr>\n"
    )


def _linkify_manchester(text: str, onto: Any) -> str:
    def _replace(match: re.Match) -> str:
        word = match.group(0)
        try:
            return _html_link(onto[word].iri, word)
        except (KeyError, AttributeError):
            return word
    return re.sub(r"\w+", _replace, text)


# ---------------------------------------------------------------------------
# Ontopy-dependent functions
# ---------------------------------------------------------------------------

def _require_ontopy() -> None:
    try:
        import ontopy  # noqa: F401
    except ImportError:
        LOGGER.error(
            "--generate-rst requires ontopy. Install with: pip install \".[docs]\""
        )
        sys.exit(1)


def load_ontology(filepath: str) -> Any:
    _require_ontopy()
    from ontopy import get_ontology
    only_local = os.environ.get("ONLY_LOCAL_IMPORTS", "").strip().lower() in {"1", "true", "yes"}
    return get_ontology(filepath).load(only_local=only_local)


def _sorted_annotations(onto: Any) -> list[Any]:
    priorities = [onto[iri] for iri in ANNOTATION_RANK.values() if onto[iri] is not None]

    def rank(prop: Any) -> int:
        if prop in priorities[:3]:
            return priorities.index(prop)
        ancestors = set(prop.ancestors())
        for idx, anchor in enumerate(priorities[3:], start=3):
            if anchor in ancestors:
                return idx
        return len(priorities)

    return sorted(onto.annotation_properties(imported=True), key=rank)


def _truthy_literal(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if hasattr(value, "toPython"):
        try:
            return _truthy_literal(value.toPython())
        except Exception:
            pass
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes"}
    return False


def _is_deprecated(entity: Any) -> bool:
    try:
        value = getattr(entity, "deprecated", None)
    except Exception:
        return False
    if value is None:
        return False
    if isinstance(value, (list, tuple, set)):
        return any(_truthy_literal(v) for v in value)
    return _truthy_literal(value)


def extract_terms(onto: Any, ontology_prefix: str) -> list[dict[str, Any]]:
    """Extract term metadata dicts from *onto*, filtered to *ontology_prefix*."""
    import owlready2

    base = ontology_prefix.rstrip("#/")
    all_annotations = _sorted_annotations(onto)
    skos_annotations = [
        p for p in all_annotations
        if getattr(p, "iri", "").startswith(str(SKOS))
    ]
    multi_row = {str(SKOS.altLabel), str(SKOS.example)}

    entities = []
    for entity in onto.get_entities(imported=False):
        if not entity.iri.split("#")[0] == base:
            continue
        try:
            pref_labels = entity.prefLabel
        except Exception:
            pref_labels = []
        if not pref_labels:
            continue

        record: dict[str, Any] = {"IRI": entity.iri, "deprecated": _is_deprecated(entity)}

        for ann in skos_annotations:
            values = ann._get_values_for_class(entity)
            if not values:
                continue
            extracted = []
            for v in values:
                if isinstance(v, str):
                    extracted.append(v)
                elif hasattr(v, "lang") and v.lang == "en":
                    extracted.append(v)
            if ann.iri in multi_row:
                record[ann] = extracted
            else:
                record[ann] = "; ".join(str(x) for x in extracted)

        # BDF-specific annotations: the LaTeX symbol/formula (emitted as MathJax
        # inline math \(...\) in the raw-HTML table) and the obligation level.
        # Keys are lowercased to match the local-name style of the other rows.
        for disp_key, ann_iri, as_math in (
            ("symbol",     base + "#latexSymbol",  True),
            ("formula",    base + "#latexFormula", True),
            ("obligation", base + "#obligation",   False),
        ):
            prop = onto[ann_iri]
            if prop is None:
                continue
            vals = prop._get_values_for_class(entity)
            if not vals:
                continue
            text = str(vals[0]).strip()
            if text:
                record[disp_key] = f"\\({text}\\)" if as_math else text

        # qudt:hasQuantityKind -> the QUDT quantity-kind alignment (formerly
        # carried by skos:exactMatch, which the SKOS-namespace loop above picked
        # up automatically; the qudt: property needs an explicit read).
        qk_prop = onto["http://qudt.org/schema/qudt/hasQuantityKind"]
        if qk_prop is not None:
            qk_values = [
                str(getattr(v, "iri", v))
                for v in qk_prop._get_values_for_class(entity)
            ]
            if qk_values:
                record["hasQuantityKind"] = "; ".join(qk_values)

        # prov:wasDerivedFrom -> resolve targets to entities for linked rendering
        deriv_prop = onto["http://www.w3.org/ns/prov#wasDerivedFrom"]
        if deriv_prop is not None:
            derived = []
            for val in deriv_prop._get_values_for_class(entity):
                target = val if hasattr(val, "iri") else onto[str(val)]
                if target is not None and getattr(target, "iri", "").split("#")[0] == base:
                    derived.append(target)
            if derived:
                record["wasDerivedFrom"] = list(dict.fromkeys(derived))

        record["subclassOf"] = [
            e for e in entity.is_a
            if isinstance(e, (owlready2.ThingClass, owlready2.PropertyClass))
        ]
        record["subclasses"] = list(entity.subclasses())
        record["restrictions"] = [
            r for r in entity.is_a if isinstance(r, owlready2.Restriction)
        ]
        entities.append(record)

    entities.sort(key=lambda e: e[onto.prefLabel])
    return entities


def entities_to_rst(entities: list[dict[str, Any]], onto: Any) -> str:
    """Render a list of entity metadata dicts to RST with raw HTML tables."""
    import owlready2
    from ontopy.utils import asstring
    from ontopy.patch import get_preferred_label

    def _pref_label(obj: Any) -> str | None:
        try:
            lbl = get_preferred_label(obj)
            return str(lbl).strip() if lbl else None
        except Exception:
            return None

    def _canon_key(k: Any) -> str:
        if isinstance(k, str):
            return _norm(k)
        lbl = _pref_label(k)
        if lbl:
            return _norm(lbl)
        iri = getattr(k, "iri", None)
        if iri:
            return _norm(iri.split("#")[-1].split("/")[-1])
        return _norm(getattr(k, "name", None) or str(k))

    def _display_key(k: Any) -> str:
        lbl = _pref_label(k)
        if lbl:
            return lbl
        iri = getattr(k, "iri", None)
        if iri:
            return iri.split("#")[-1].split("/")[-1]
        return getattr(k, "name", None) or str(k)

    def _get_links(item: dict, key: str) -> list[str]:
        links = []
        for ent in item[key]:
            try:
                label = ent.prefLabel.get_lang("en")[0]
            except (IndexError, AttributeError):
                label = str(ent)
            links.append(_html_link(ent.iri, label))
        return links

    TABLE_SKIP = _TABLE_SKIP_BASE | set(CALLOUTS.keys())
    rst = ""

    for item in entities:
        if "#" not in item["IRI"]:
            continue

        _, iri_suffix = item["IRI"].split("#", 1)
        title = item[onto.prefLabel]

        rst += "\n.. raw:: html\n\n"
        rst += f"   <hr class=\"term-separator\" />\n   <div id=\"{iri_suffix}\"></div>\n\n"
        rst += f"{title}\n{'-' * len(title)}\n\n"
        rst += f"IRI: {item['IRI']}\n\n"

        norm: dict[str, Any] = {}
        display: dict[str, str] = {}
        for k, v in item.items():
            ck = _canon_key(k)
            norm[ck] = v
            display[ck] = _display_key(k)

        rst += ".. raw:: html\n\n"
        rst += "  <table class=\"element-table\">\n"

        for ck, value in norm.items():
            if ck in TABLE_SKIP or value in ("None", "", None):
                continue
            for val in (value if isinstance(value, list) else [value]):
                rst += _html_table_row(display.get(ck, ck), _linkify_value(str(val)))

        if item.get("restrictions"):
            restr = list(dict.fromkeys(
                _linkify_manchester(asstring(r), onto) for r in item["restrictions"]
            ))
            items_html = "".join(f"<li>{s}</li>" for s in restr)
            rst += _html_table_row(
                "restrictions",
                f"<div class=\"restriction-list\"><ul>{items_html}</ul></div>",
            )

        if norm.get("subclassof"):
            rst += _html_table_row("subclassOf", ", ".join(_get_links(item, "subclassOf")))
        if norm.get("subclasses"):
            rst += _html_table_row("subclasses", ", ".join(_get_links(item, "subclasses")))
        if norm.get("wasderivedfrom"):
            rst += _html_table_row("wasDerivedFrom", ", ".join(_get_links(item, "wasDerivedFrom")))

        rst += "  </table>\n\n"

        for ck, (directive, title_txt) in CALLOUTS.items():
            raw = norm.get(ck)
            if not raw:
                continue
            items = (
                [str(x).strip() for x in raw if str(x).strip()]
                if isinstance(raw, (list, tuple))
                else [p.strip() for p in str(raw).split("\n\n") if p.strip()]
            )
            for item_text in items:
                if directive == "admonition":
                    hdr = title_txt or display.get(ck, ck).capitalize()
                    rst += f".. admonition:: {hdr}\n\n"
                else:
                    rst += f".. {directive}::\n\n"
                rst += _indent(item_text) + "\n\n"

    return rst


def generate_rst(config: dict[str, Any]) -> None:
    """Generate RST documentation for all configured TTL files."""
    _require_ontopy()

    rst_path = config["rst_output_filename"]
    prefix = config["ontology_prefix"]
    content = _rst_header(config)

    for module in config["ttl_files"]:
        filepath = module["path"]
        if not os.path.isfile(filepath):
            LOGGER.warning("TTL file not found, skipping: %s", filepath)
            continue

        onto = load_ontology(filepath)
        all_entities = extract_terms(onto, prefix)
        section = module["section_title"]

        content += f"\n{section}\n{'=' * len(section)}\n\n"
        content += _rst_abstract(onto)

        active = [e for e in all_entities if not e.get("deprecated")]
        deprecated = [e for e in all_entities if e.get("deprecated")]

        content += entities_to_rst(active, onto)
        if deprecated:
            content += "\nDeprecated Terms\n" + "-" * len("Deprecated Terms") + "\n\n"
            content += entities_to_rst(deprecated, onto)

    content += "\nEnd of Document.\n"

    with open(rst_path, "w", encoding="utf-8") as fh:
        fh.write(content)
    LOGGER.info("RST file generated: %s", rst_path)
    print(f"RST file generated: {rst_path}")


def _rst_header(config: dict[str, Any]) -> str:
    title = f"{config['ontology_name']} Terms"
    line = "=" * len(title)
    return f"\n{line}\n{title}\n{line}\n\n"


def _rst_abstract(onto: Any) -> str:
    try:
        abstract = onto.metadata.abstract.en[0]
    except Exception:
        return "\n\n"
    return f"\n{abstract}\n\n" if abstract else "\n\n"
