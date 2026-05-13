import json
import unittest
from pathlib import Path

from rdflib import Graph, Literal, Namespace, OWL, RDF, RDFS, URIRef


ONTOLOGY_IRI = URIRef("https://w3id.org/battery-data-alliance/ontology/battery-data-format")
ONTOLOGY_VERSION_IRI = URIRef(
    "https://w3id.org/battery-data-alliance/ontology/battery-data-format/1.0.0/battery-data-format"
)
BDF = Namespace("https://w3id.org/battery-data-alliance/ontology/battery-data-format#")
EMMO = Namespace("https://w3id.org/emmo#")
HAS_MEASUREMENT_UNIT = URIRef("https://w3id.org/emmo#EMMO_bed1d005_b04e_4a90_94cf_02bc678a8569")


class TestOntologyReleaseReadiness(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = Graph()
        cls.graph.parse("battery-data-format.ttl", format="turtle")
        cls.schema = json.loads(Path("schema/schema.json").read_text(encoding="utf-8"))

    def test_ontology_declares_expected_version(self):
        self.assertIn((ONTOLOGY_IRI, RDF.type, OWL.Ontology), self.graph)
        self.assertIn((ONTOLOGY_IRI, OWL.versionIRI, ONTOLOGY_VERSION_IRI), self.graph)
        self.assertIn((ONTOLOGY_IRI, OWL.versionInfo, Literal("1.0.0")), self.graph)

    def test_internal_resistance_has_ohm_unit_restriction(self):
        entity = BDF.internal_resistance_ohm
        found_restriction = False

        for _, _, candidate in self.graph.triples((entity, RDFS.subClassOf, None)):
            if (
                (candidate, RDF.type, OWL.Restriction) in self.graph
                and (candidate, OWL.onProperty, HAS_MEASUREMENT_UNIT) in self.graph
                and (candidate, OWL.someValuesFrom, EMMO.Ohm) in self.graph
            ):
                found_restriction = True
                break

        self.assertTrue(found_restriction, "Missing expected Ohm unit restriction on internal_resistance_ohm")

    def test_schema_version_matches_ontology_release(self):
        self.assertEqual(self.schema.get("dcterms:version"), "1.0.0")
        self.assertEqual(self.schema.get("schema:version"), "1.0.0")
        self.assertIn("/1.0.0/", self.schema.get("@id", ""))


if __name__ == "__main__":
    unittest.main()
