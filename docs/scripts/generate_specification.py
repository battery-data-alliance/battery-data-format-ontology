import datetime
from pathlib import Path

from rdflib import Graph, Literal, Namespace, RDF, RDFS, OWL, URIRef
from rdflib.namespace import DCTERMS

BASE_IRI = "https://w3id.org/battery-data-alliance/ontology/battery-data-format"
BDF = Namespace(f"{BASE_IRI}#")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
EMMO = Namespace("https://w3id.org/emmo#")
SCHEMA = Namespace("https://schema.org/")

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


def _get_notes(graph: Graph, subject, definition):
    values = _get_literals(graph, subject, RDFS.comment)
    if not values:
        return ""
    note = _pick_literal(values)
    if note and note != definition:
        return note
    return ""


def _get_alt_labels(graph: Graph, subject):
    values = _get_literals(graph, subject, SKOS.altLabel)
    return sorted({_literal_text(value) for value in values if _literal_text(value)})


def _get_notation(graph: Graph, subject):
    values = _get_literals(graph, subject, SKOS.notation)
    return _pick_literal(values)


def _get_superclasses(graph: Graph, subject):
    supers = []
    for obj in graph.objects(subject, RDFS.subClassOf):
        if isinstance(obj, URIRef) and obj != OWL.Thing:
            supers.append(obj)
    return supers


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


def _get_deprecated(graph: Graph, subject) -> bool:
    for value in graph.objects(subject, OWL.deprecated):
        if isinstance(value, Literal) and str(value).lower() == "true":
            return True
    return False


def _format_iri_list(graph: Graph, items):
    if not items:
        return "-"
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
    publisher = _pick_literal(_get_literals(graph, ONTOLOGY_IRI, DCTERMS.publisher))
    license_iri = next(graph.objects(ONTOLOGY_IRI, DCTERMS.license), None)
    version_info = _pick_literal(_get_literals(graph, ONTOLOGY_IRI, OWL.versionInfo))
    imports = sorted(
        {str(obj) for obj in graph.objects(ONTOLOGY_IRI, OWL.imports) if isinstance(obj, URIRef)}
    )

    terms = []
    for subject in graph.subjects(RDF.type, OWL.Class):
        if isinstance(subject, URIRef) and str(subject).startswith(str(BDF)):
            terms.append(subject)

    def sort_key(term):
        notation = _get_notation(graph, term)
        return notation or _local_name(term)

    terms = sorted(terms, key=sort_key)

    lines = []
    lines.append("Battery Data Format Specification")
    lines.append("=================================")
    lines.append("")
    lines.append(".. note::")
    lines.append("   This page is generated from the ontology file ``battery-data-format.ttl``.")
    lines.append("")
    lines.append("Status")
    lines.append("------")
    lines.append(f"- Title: {title or '-'}")
    lines.append(f"- Version: {version_info or '-'}")
    lines.append(f"- Issued: {issued or '-'}")
    lines.append(f"- Modified: {modified or '-'}")
    lines.append(f"- Publisher: {publisher or '-'}")
    lines.append(f"- License: {str(license_iri) if license_iri else '-'}")
    lines.append("")
    lines.append("Scope")
    lines.append("-----")
    lines.append(abstract or "-")
    lines.append("")
    lines.append("Normative References")
    lines.append("--------------------")
    if imports:
        for item in imports:
            lines.append(f"- {item}")
    else:
        lines.append("- None.")
    lines.append("")
    lines.append("Identifiers")
    lines.append("-----------")
    lines.append(f"Base IRI: {BASE_IRI}#")
    lines.append("Full term IRIs are formed by concatenating the base IRI with the notation.")
    lines.append("")
    lines.append("Terms and Definitions")
    lines.append("---------------------")
    lines.append("")
    lines.append(".. list-table::")
    lines.append("   :widths: 20 15 45 20")
    lines.append("   :header-rows: 1")
    lines.append("")
    lines.append("   * - Term")
    lines.append("     - Notation")
    lines.append("     - Definition")
    lines.append("     - Unit")

    for term in terms:
        label = _get_labels(graph, term)
        definition = _get_definition(graph, term) or "-"
        notation = _get_notation(graph, term) or "-"
        units = _format_iri_list(graph, _get_units(graph, term))

        lines.append("   * - " + label.replace("\n", " "))
        lines.append("     - " + notation.replace("\n", " "))
        lines.append("     - " + definition.replace("\n", " "))
        lines.append("     - " + units.replace("\n", " "))

    lines.append("")
    lines.append("See :doc:`BDF Ontology Terms </battery-data-format>` for full term metadata.")
    lines.append("")

    OUTPUT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    build_specification()
