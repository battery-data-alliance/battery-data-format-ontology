import datetime
from pathlib import Path

from rdflib import Graph, Literal, Namespace, RDF, RDFS, OWL, URIRef
from rdflib.namespace import DCTERMS

BASE_IRI = "https://w3id.org/battery-data-alliance/ontology/battery-data-format"
BDF = Namespace(f"{BASE_IRI}#")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
EMMO = Namespace("https://w3id.org/emmo#")
SCHEMA = Namespace("https://schema.org/")
QUDT_KIND = Namespace("http://qudt.org/vocab/quantitykind/")
PROV = Namespace("http://www.w3.org/ns/prov#")

ONTOLOGY_IRI = URIRef(BASE_IRI)
TTL_PATH = Path("battery-data-format.ttl")
OUTPUT_PATH = Path("docs/pages/specification.rst")


def _local_name(uri: URIRef) -> str:
    text = str(uri)
    if "#" in text:
        return text.rsplit("#", 1)[-1]
    return text.rsplit("/", 1)[-1]


def _literal_text(literal: Literal) -> str:
    if literal is None:
        return ""
    return str(literal)


def _pick_literal(values):
    if not values:
        return ""
    for value in values:
        if isinstance(value, Literal) and value.language == "en":
            return _literal_text(value)
    return _literal_text(values[0])


def _get_literals(graph: Graph, subject, predicate):
    return [obj for obj in graph.objects(subject, predicate) if isinstance(obj, Literal)]


def _get_labels(graph: Graph, subject):
    for pred in (SKOS.prefLabel, RDFS.label, SCHEMA.name):
        values = _get_literals(graph, subject, pred)
        label = _pick_literal(values)
        if label:
            return label
    return _local_name(subject)


def _get_definition(graph: Graph, subject):
    values = _get_literals(graph, subject, SKOS.definition)
    if values:
        return _pick_literal(values)
    values = _get_literals(graph, subject, RDFS.comment)
    if values:
        return _pick_literal(values)
    return ""


def _get_notation(graph: Graph, subject):
    values = _get_literals(graph, subject, SKOS.notation)
    return _pick_literal(values)


def _get_units(graph: Graph, subject):
    units = []
    for obj in graph.objects(subject, RDFS.subClassOf):
        if not isinstance(obj, URIRef):
            if (obj, RDF.type, OWL.Restriction) in graph and (
                obj, OWL.onProperty, EMMO.EMMO_bed1d005_b04e_4a90_94cf_02bc678a8569
            ) in graph:
                for unit in graph.objects(obj, OWL.someValuesFrom):
                    if isinstance(unit, URIRef):
                        units.append(unit)
                for unit in graph.objects(obj, OWL.hasValue):
                    if isinstance(unit, URIRef):
                        units.append(unit)
    return units


def _get_unit_code(graph: Graph, subject) -> str:
    val = graph.value(subject, SCHEMA.unitCode)
    return str(val) if val else ""


def _get_symbol(graph: Graph, subject) -> str:
    val = graph.value(subject, BDF.latexSymbol)
    return str(val) if val else ""


def _get_formula(graph: Graph, subject) -> str:
    val = graph.value(subject, BDF.latexFormula)
    return str(val) if val else ""


def _get_quantity_kind(graph: Graph, subject) -> str:
    """Return the local name of the QUDT quantitykind: match, e.g. 'Voltage'."""
    for obj in graph.objects(subject, SKOS.exactMatch):
        if isinstance(obj, URIRef) and str(obj).startswith(str(QUDT_KIND)):
            return _local_name(obj)
    return ""


def _get_derived_from(graph: Graph, subject) -> str:
    """Return comma-separated notations of prov:wasDerivedFrom sources."""
    sources = []
    for obj in graph.objects(subject, PROV.wasDerivedFrom):
        if isinstance(obj, URIRef):
            notation = _get_notation(graph, obj)
            sources.append(notation or _local_name(obj))
    return ", ".join(sorted(sources)) if sources else ""


def _format_iri_list(graph: Graph, items):
    if not items:
        return "—"
    labels = []
    for item in items:
        label = _get_labels(graph, item)
        local = _local_name(item)
        if label and label != local:
            labels.append(f"{label} ({local})")
        else:
            labels.append(local)
    return ", ".join(sorted(labels))


def build_specification():
    graph = Graph()
    graph.parse(TTL_PATH, format="turtle")

    title = _pick_literal(_get_literals(graph, ONTOLOGY_IRI, DCTERMS.title))
    abstract = _pick_literal(_get_literals(graph, ONTOLOGY_IRI, DCTERMS.abstract))
    issued = _pick_literal(_get_literals(graph, ONTOLOGY_IRI, DCTERMS.issued))
    modified = _pick_literal(_get_literals(graph, ONTOLOGY_IRI, DCTERMS.modified))
    # Publisher may be a literal name or an organisation IRI. Prefer a literal
    # (or the IRI's rdfs:label); fall back to the IRI string itself.
    publisher_obj = next(graph.objects(ONTOLOGY_IRI, DCTERMS.publisher), None)
    if isinstance(publisher_obj, URIRef):
        publisher = _pick_literal(_get_literals(graph, publisher_obj, RDFS.label)) or str(publisher_obj)
    elif publisher_obj is not None:
        publisher = str(publisher_obj)
    else:
        publisher = ""
    license_iri = next(graph.objects(ONTOLOGY_IRI, DCTERMS.license), None)
    version_info = _pick_literal(_get_literals(graph, ONTOLOGY_IRI, OWL.versionInfo))
    imports = sorted(
        {str(obj) for obj in graph.objects(ONTOLOGY_IRI, OWL.imports) if isinstance(obj, URIRef)}
    )

    terms = [
        subject for subject in graph.subjects(RDF.type, OWL.Class)
        if isinstance(subject, URIRef) and str(subject).startswith(str(BDF))
    ]
    terms = sorted(terms, key=lambda t: _get_notation(graph, t) or _local_name(t))

    lines = []
    lines.append("Battery Data Format Specification")
    lines.append("=================================")
    lines.append("")
    lines.append(".. note::")
    lines.append("   This page is generated from the ontology file ``battery-data-format.ttl``.")
    lines.append("   Do not edit it directly.")
    lines.append("")

    # --- Status ---
    lines.append("Status")
    lines.append("------")
    lines.append("")
    lines.append(".. list-table::")
    lines.append("   :widths: 25 75")
    lines.append("   :stub-columns: 1")
    lines.append("")
    for label, value in [
        ("Title",     title or "—"),
        ("Version",   version_info or "—"),
        ("Issued",    issued or "—"),
        ("Modified",  modified or "—"),
        ("Publisher", publisher or "—"),
        ("License",   str(license_iri) if license_iri else "—"),
    ]:
        lines.append(f"   * - {label}")
        lines.append(f"     - {value}")
    lines.append("")

    # --- Scope ---
    lines.append("Scope")
    lines.append("-----")
    lines.append("")
    lines.append(abstract or "—")
    lines.append("")

    # --- Normative references ---
    lines.append("Normative References")
    lines.append("--------------------")
    lines.append("")
    if imports:
        for item in imports:
            lines.append(f"- `{item} <{item}>`_")
    else:
        lines.append("- None.")
    lines.append("")

    # --- Identifiers ---
    lines.append("Identifiers")
    lines.append("-----------")
    lines.append("")
    lines.append(f"- **Base IRI:** ``{BASE_IRI}#``")
    lines.append("- Full term IRIs are formed by appending the notation to the base IRI,")
    lines.append(f"  e.g. ``{BASE_IRI}#voltage_volt``.")
    ttl_stem = TTL_PATH.stem  # battery-data-format
    lines.append(f"- **Version IRI:** ``{BASE_IRI}/{version_info}/{ttl_stem}``")
    lines.append("")

    # --- Terms and definitions ---
    lines.append("Terms and Definitions")
    lines.append("---------------------")
    lines.append("")
    lines.append(".. list-table::")
    lines.append("   :widths: 18 15 10 39 6 12")
    lines.append("   :header-rows: 1")
    lines.append("")
    lines.append("   * - Term")
    lines.append("     - Notation")
    lines.append("     - Symbol")
    lines.append("     - Definition")
    lines.append("     - UCUM")
    lines.append("     - Quantity Kind")

    for term in terms:
        label        = _get_labels(graph, term)
        definition   = _get_definition(graph, term) or "—"
        notation     = _get_notation(graph, term) or "—"
        symbol       = _get_symbol(graph, term)
        formula      = _get_formula(graph, term)
        ucum         = _get_unit_code(graph, term) or "—"
        qty_kind     = _get_quantity_kind(graph, term) or "—"
        derived_from = _get_derived_from(graph, term)

        if derived_from:
            definition = definition.rstrip(".") + f". *Derived from:* ``{derived_from}``."
        if formula:
            definition = definition.rstrip(".") + f". *Formula:* :math:`{formula}`."

        symbol_cell = f":math:`{symbol}`" if symbol else "—"

        lines.append("   * - " + label.replace("\n", " "))
        lines.append("     - ``" + notation.replace("\n", " ") + "``")
        lines.append("     - " + symbol_cell)
        lines.append("     - " + definition.replace("\n", " "))
        lines.append("     - ``" + ucum + "``")
        lines.append("     - " + qty_kind)

    lines.append("")
    lines.append("See :doc:`BDF Ontology Terms </battery-data-format>` for full term metadata,")
    lines.append("including EMMO superclasses, QUDT unit alignments, and PROV derivation graph.")
    lines.append("")

    OUTPUT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    build_specification()
