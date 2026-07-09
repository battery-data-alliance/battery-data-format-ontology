import json
import unittest
from pathlib import Path

from rdflib import Graph, Literal, Namespace, OWL, RDF, RDFS, URIRef
from rdflib.namespace import SKOS

PROV = Namespace("http://www.w3.org/ns/prov#")
SOSA = Namespace("http://www.w3.org/ns/sosa/")

ONTOLOGY_IRI = URIRef("https://w3id.org/battery-data-alliance/ontology/battery-data-format")
ONTOLOGY_VERSION_IRI = URIRef(
    "https://w3id.org/battery-data-alliance/ontology/battery-data-format/1.2.0/battery-data-format"
)
BDF = Namespace("https://w3id.org/battery-data-alliance/ontology/battery-data-format#")
BDF_NS = str(BDF)
EMMO = Namespace("https://w3id.org/emmo#")
SCHEMA = Namespace("https://schema.org/")
HAS_MEASUREMENT_UNIT = URIRef("https://w3id.org/emmo#EMMO_bed1d005_b04e_4a90_94cf_02bc678a8569")
ELUCIDATION = URIRef("https://w3id.org/emmo#EMMO_967080e5_2f42_4eb2_a3a9_c58143e835f9")
OBLIGATION = URIRef(str(BDF) + "obligation")

# step_type is a string-valued channel, exempt from the EMMO unit restriction.
# step_id is a counting index without a UCUM unit code / QUDT unit see-also.
UNIT_RESTRICTION_EXEMPT = frozenset({"step_type"})
UNIT_CODE_SEEALSO_EXEMPT = frozenset({"step_id", "step_type"})

# Columns that must exist in the canonical schema (presence, not requiredness).
EXPECTED_SCHEMA_COLUMNS = {"test_time_second", "voltage_volt", "current_ampere", "unix_time_second"}
# Columns whose csvw:required flag must be true — derived from the ontology's
# obligation levels (unix_time_second is 'recommended', so not flagged).
REQUIRED_FLAG_COLUMNS = {"test_time_second", "voltage_volt", "current_ampere"}
STEP_COLUMNS = {"step_id", "step_type"}


class TestOntologyReleaseReadiness(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = Graph()
        cls.graph.parse("battery-data-format.ttl", format="turtle")
        cls.schema = json.loads(Path("schema/schema.json").read_text(encoding="utf-8"))
        cls.context = json.loads(Path("context/context.json").read_text(encoding="utf-8"))

        # Build lookup: csvw:name -> column dict
        cls.schema_columns = {
            col["csvw:name"]: col
            for col in cls.schema.get("csvw:columns", [])
            if "csvw:name" in col
        }

    # ------------------------------------------------------------------
    # Ontology structure
    # ------------------------------------------------------------------

    def test_ontology_declares_expected_version(self):
        self.assertIn((ONTOLOGY_IRI, RDF.type, OWL.Ontology), self.graph)
        self.assertIn((ONTOLOGY_IRI, OWL.versionIRI, ONTOLOGY_VERSION_IRI), self.graph)
        self.assertIn((ONTOLOGY_IRI, OWL.versionInfo, Literal("1.2.0")), self.graph)

    def test_internal_resistance_has_ohm_unit_restriction(self):
        entity = BDF.internal_resistance_ohm
        found = any(
            (candidate, RDF.type, OWL.Restriction) in self.graph
            and (candidate, OWL.onProperty, HAS_MEASUREMENT_UNIT) in self.graph
            and (candidate, OWL.someValuesFrom, EMMO.Ohm) in self.graph
            for _, _, candidate in self.graph.triples((entity, RDFS.subClassOf, None))
        )
        self.assertTrue(found, "Missing expected Ohm unit restriction on internal_resistance_ohm")

    def _non_deprecated_bdf_classes(self):
        classes = []
        for s in self.graph.subjects(RDF.type, OWL.Class):
            if not str(s).startswith(BDF_NS):
                continue
            dep = self.graph.value(s, OWL.deprecated)
            if dep is not None and str(dep).lower() == "true":
                continue
            classes.append(s)
        return classes

    def _has_unit_restriction(self, entity):
        return any(
            (candidate, RDF.type, OWL.Restriction) in self.graph
            and (candidate, OWL.onProperty, HAS_MEASUREMENT_UNIT) in self.graph
            and any(True for _ in self.graph.objects(candidate, OWL.someValuesFrom))
            for _, _, candidate in self.graph.triples((entity, RDFS.subClassOf, None))
        )

    def test_annotation_parity_across_non_deprecated_terms(self):
        """Every non-deprecated BDF class must carry the full annotation set, an
        EMMO unit restriction (except string channels), and a UCUM unit code plus
        QUDT see-also (except unitless index/string channels).

        Guards against the EIS/late-added terms silently missing annotations the
        rest carry. Removing any of these from the TTL must fail this test.
        """
        required_annotations = {
            "skos:prefLabel": SKOS.prefLabel,
            "skos:definition": SKOS.definition,
            "skos:notation": SKOS.notation,
            ":obligation": OBLIGATION,
            "rdfs:label": RDFS.label,
            "rdfs:comment": RDFS.comment,
            "schema:name": SCHEMA.name,
            "schema:description": SCHEMA.description,
            "emmo:elucidation": ELUCIDATION,
        }
        classes = self._non_deprecated_bdf_classes()
        self.assertTrue(classes, "No non-deprecated BDF classes found in the ontology graph.")
        for entity in classes:
            name = str(entity).split("#")[-1]
            with self.subTest(term=name):
                for label, pred in required_annotations.items():
                    self.assertTrue(
                        any(True for _ in self.graph.objects(entity, pred)),
                        f"{name} is missing {label}",
                    )
                if name not in UNIT_RESTRICTION_EXEMPT:
                    self.assertTrue(
                        self._has_unit_restriction(entity),
                        f"{name} is missing the EMMO unit restriction",
                    )
                if name not in UNIT_CODE_SEEALSO_EXEMPT:
                    self.assertTrue(
                        any(True for _ in self.graph.objects(entity, SCHEMA.unitCode)),
                        f"{name} is missing schema:unitCode",
                    )
                    self.assertTrue(
                        any(True for _ in self.graph.objects(entity, RDFS.seeAlso)),
                        f"{name} is missing rdfs:seeAlso",
                    )

    # ------------------------------------------------------------------
    # Schema completeness
    # ------------------------------------------------------------------

    def test_schema_version_matches_ontology_release(self):
        self.assertEqual(self.schema.get("dcterms:version"), "1.2.0")
        self.assertEqual(self.schema.get("schema:version"), "1.2.0")
        self.assertIn("/1.2.0/", self.schema.get("@id", ""))

    def test_all_required_bdf_columns_in_schema(self):
        missing = EXPECTED_SCHEMA_COLUMNS - self.schema_columns.keys()
        self.assertFalse(
            missing,
            f"schema.json is missing required columns: {sorted(missing)}",
        )

    def test_step_id_and_step_type_in_schema(self):
        """Regression guard: these columns were added in fix/step-quantity-semantics."""
        missing = STEP_COLUMNS - self.schema_columns.keys()
        self.assertFalse(
            missing,
            f"schema.json is missing step columns: {sorted(missing)}. "
            "Did fix/step-quantity-semantics get applied?",
        )

    def test_required_columns_flagged_as_required(self):
        not_required = [
            name
            for name in REQUIRED_FLAG_COLUMNS
            if not self.schema_columns.get(name, {}).get("csvw:required", False)
        ]
        self.assertFalse(
            not_required,
            f"These columns should have csvw:required=true: {sorted(not_required)}",
        )

    def test_required_flags_match_ontology_obligation(self):
        """csvw:required must agree with the ontology's :obligation annotation."""
        obligation = URIRef(str(BDF) + "obligation")
        for name, col in self.schema_columns.items():
            term_obligation = self.graph.value(BDF[name], obligation)
            if term_obligation is None:
                continue  # deprecated tombstones carry no obligation
            with self.subTest(column=name):
                self.assertEqual(
                    bool(col.get("csvw:required", False)),
                    str(term_obligation) == "required",
                    f"{name}: csvw:required disagrees with obligation '{term_obligation}'",
                )

    def test_no_unit_CountingUnit_in_schema(self):
        """unit:CountingUnit is a QUDT class, not a unit individual. Regression guard."""
        schema_text = Path("schema/schema.json").read_text(encoding="utf-8")
        self.assertNotIn(
            "unit:CountingUnit",
            schema_text,
            "schema.json contains 'unit:CountingUnit' which is a QUDT class. Use 'unit:NUM' instead.",
        )

    # ------------------------------------------------------------------
    # Context completeness and correctness
    # ------------------------------------------------------------------

    def test_context_defines_bdf_prefix(self):
        inner = self.context.get("@context", {})
        self.assertIn("bdf", inner, "context.json is missing the 'bdf:' prefix declaration.")
        self.assertEqual(
            inner["bdf"],
            str(BDF),
            f"context.json 'bdf:' prefix resolves to wrong IRI: {inner.get('bdf')}",
        )

    def test_context_defines_required_prefixes(self):
        inner = self.context.get("@context", {})
        for prefix in ("emmo", "qudt", "quantitykind", "unit"):
            with self.subTest(prefix=prefix):
                self.assertIn(
                    prefix,
                    inner,
                    f"context.json is missing the '{prefix}:' prefix declaration.",
                )

    def test_step_id_and_step_type_in_context(self):
        """Regression guard: context must include labels for the new step columns."""
        inner = self.context.get("@context", {})
        self.assertIn(
            "Step ID",
            inner,
            "context.json is missing 'Step ID'. Regenerate with --generate-context.",
        )
        self.assertIn(
            "Step Type",
            inner,
            "context.json is missing 'Step Type'. Regenerate with --generate-context.",
        )

    # ------------------------------------------------------------------
    # SOSA alignment
    # ------------------------------------------------------------------

    def test_all_bdf_classes_subclass_sosa_observable_property(self):
        """Every BDF quantity class must declare rdfs:subClassOf sosa:ObservableProperty.
        Uses subClassOf (OWL 2 DL) rather than punning to preserve EMMO DL compatibility."""
        bdf_classes = {
            s for s, p, o in self.graph.triples((None, RDF.type, OWL.Class))
            if str(s).startswith(str(BDF))
        }
        self.assertTrue(bdf_classes, "No BDF classes found in the ontology graph.")
        not_sosa = [
            str(c) for c in bdf_classes
            if (c, RDFS.subClassOf, SOSA.ObservableProperty) not in self.graph
        ]
        self.assertFalse(
            not_sosa,
            f"{len(not_sosa)} BDF class(es) missing 'rdfs:subClassOf sosa:ObservableProperty': "
            f"{sorted(not_sosa)[:5]}{'...' if len(not_sosa) > 5 else ''}",
        )

    # ------------------------------------------------------------------
    # PROV-O derivation graph
    # ------------------------------------------------------------------

    EXPECTED_DERIVATIONS = {
        "power_watt":                  {"voltage_volt", "current_ampere"},
        "step_cumulative_capacity_ah": {"current_ampere", "step_time_second"},
        "charging_capacity_ah":        {"current_ampere", "test_time_second"},
        "discharging_capacity_ah":     {"current_ampere", "test_time_second"},
        "cumulative_capacity_ah":      {"current_ampere", "test_time_second"},
        "charging_energy_wh":          {"power_watt", "test_time_second"},
        "discharging_energy_wh":       {"power_watt", "test_time_second"},
        "cumulative_energy_wh":        {"power_watt", "test_time_second"},
        "net_capacity_ah":             {"charging_capacity_ah", "discharging_capacity_ah"},
        "step_cumulative_energy_wh":   {"power_watt", "step_time_second"},
        "net_energy_wh":               {"charging_energy_wh", "discharging_energy_wh"},
        "step_net_capacity_ah":        {"step_charging_capacity_ah", "step_discharging_capacity_ah"},
        "step_net_energy_wh":          {"step_charging_energy_wh", "step_discharging_energy_wh"},
        "cycle_charging_capacity_ah":    {"current_ampere", "cycle_count"},
        "cycle_discharging_capacity_ah": {"current_ampere", "cycle_count"},
        "cycle_cumulative_capacity_ah":  {"current_ampere", "cycle_count"},
        "cycle_net_capacity_ah":         {"cycle_charging_capacity_ah", "cycle_discharging_capacity_ah"},
        "cycle_charging_energy_wh":      {"power_watt", "cycle_count"},
        "cycle_discharging_energy_wh":   {"power_watt", "cycle_count"},
        "cycle_cumulative_energy_wh":    {"power_watt", "cycle_count"},
        "cycle_net_energy_wh":           {"cycle_charging_energy_wh", "cycle_discharging_energy_wh"},
        "absolute_impedance_ohm":      {"real_impedance_ohm", "imaginary_impedance_ohm"},
        "phase_degree":                {"real_impedance_ohm", "imaginary_impedance_ohm"},
    }

    def test_prov_derivation_graph_complete_and_targets_bdf_classes(self):
        """All expected prov:wasDerivedFrom edges are present and point only to known BDF classes."""
        bdf_classes = {
            str(s).split("#")[1]
            for s, p, o in self.graph.triples((None, RDF.type, OWL.Class))
            if str(s).startswith(str(BDF))
        }
        errors = []
        for derived, expected_sources in self.EXPECTED_DERIVATIONS.items():
            derived_iri = BDF[derived]
            actual_sources = {
                str(o).split("#")[1]
                for _, _, o in self.graph.triples((derived_iri, PROV.wasDerivedFrom, None))
            }
            missing = expected_sources - actual_sources
            extra   = actual_sources - expected_sources
            unknown = actual_sources - bdf_classes
            if missing:
                errors.append(f"{derived}: missing sources {sorted(missing)}")
            if extra:
                errors.append(f"{derived}: unexpected extra sources {sorted(extra)}")
            if unknown:
                errors.append(f"{derived}: sources not BDF classes {sorted(unknown)}")
        self.assertFalse(errors, "\n".join(errors))

    def test_sosa_prefix_in_context(self):
        inner = self.context.get("@context", {})
        self.assertIn("sosa", inner, "context.json is missing the 'sosa:' prefix declaration.")
        self.assertEqual(
            inner["sosa"],
            str(SOSA),
            f"context.json 'sosa:' prefix resolves to wrong IRI: {inner.get('sosa')}",
        )

    def test_context_bdf_terms_resolve_to_bdf_namespace(self):
        """All BDF label entries in the context must point into the BDF namespace."""
        inner = self.context.get("@context", {})
        bad = {}
        for key, val in inner.items():
            iri = val if isinstance(val, str) else val.get("@id", "") if isinstance(val, dict) else ""
            # Only check entries whose IRI starts with bdf: or the full BDF namespace
            if iri.startswith("bdf:") or iri.startswith(BDF_NS):
                resolved = iri.replace("bdf:", BDF_NS) if iri.startswith("bdf:") else iri
                if not resolved.startswith(BDF_NS):
                    bad[key] = iri
        self.assertFalse(bad, f"Context BDF terms with unexpected IRIs: {bad}")
