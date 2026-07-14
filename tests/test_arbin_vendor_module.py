"""Structural and header-coverage tests for the Arbin vendor ontology module.

Guarantees, per the module's contract:
  * every observed native Arbin header resolves to exactly one vendor term
    within its sheet scope (timeseries / eis / statistics / metadata);
  * every documented dialect quirk (leading-space, typo, unit-label bug,
    mojibake, bare .res spelling, MITS 7 PV code) resolves verbatim;
  * every term carries a role, at least one sheet scope, a definition and a
    label; indexed families carry a headerPattern;
  * mapped terms point (via rdfs:subClassOf and skos:exactMatch) at a real
    BDF core class; unverified terms carry no core mapping.
"""
import json
import re
import unittest
from pathlib import Path

from rdflib import Graph, Namespace, RDF, RDFS, OWL, URIRef
from rdflib.namespace import SKOS

REPO = Path(__file__).resolve().parent.parent
ARBIN_TTL = REPO / "vendors" / "arbin.ttl"
CORE_TTL = REPO / "battery-data-format.ttl"
OBSERVED = REPO / "tests" / "data" / "arbin_observed_headers.json"

ARBIN = Namespace("https://w3id.org/battery-data-alliance/ontology/battery-data-format/vendors/arbin#")
BDF = Namespace("https://w3id.org/battery-data-alliance/ontology/battery-data-format#")
A_ROLE = ARBIN.role
A_SCOPE = ARBIN.sheetScope
A_PATTERN = ARBIN.headerPattern
A_STATUS = ARBIN.verificationStatus

VALID_ROLES = {"measurement", "derived", "identifier", "bookkeeping", "metadata"}
VALID_SCOPES = {"timeseries", "eis", "statistics", "metadata"}

# Documented dialect spellings that are NOT present in the sampled files but
# are required to resolve verbatim (handoff sections 4 and 5): bare .res/SQL
# spellings, MITS 7 numeric PV codes, and known Arbin quirks.
DOCUMENTED = [
    # (header, scope)
    ("Charge_Capacity", "timeseries"),
    ("Discharge_Capacity", "timeseries"),
    ("Charge_Energy", "timeseries"),
    ("Discharge_Energy", "timeseries"),
    ("Cycle_ID", "timeseries"),
    ("Step_ID", "timeseries"),
    ("PV28", "timeseries"),
    ("PV45", "timeseries"),
    ("Reference_Voltage(Ohm)", "timeseries"),   # Arbin unit-label bug
    ("Reference_Voltage", "timeseries"),
    (" Item_ID", "metadata"),                    # leading-space quirk
    ("Has Specail", "metadata"),                 # Arbin typo
    ("Schedule_File_Name", "metadata"),
    ("MASS", "metadata"),
    ("Capacity", "metadata"),                    # nominal (distinct from time-series)
    ("rowstate", "metadata"),
]


class ArbinModule:
    """Parsed view of the Arbin module for resolution."""

    def __init__(self, graph: Graph):
        self.g = graph
        self.terms = {}  # iri -> dict
        for c in graph.subjects(RDF.type, OWL.Class):
            if not str(c).startswith(str(ARBIN)):
                continue
            alts = {str(o) for o in graph.objects(c, SKOS.altLabel)}
            scopes = {str(o) for o in graph.objects(c, A_SCOPE)}
            patterns = [str(o) for o in graph.objects(c, A_PATTERN)]
            roles = [str(o) for o in graph.objects(c, A_ROLE)]
            status = [str(o) for o in graph.objects(c, A_STATUS)]
            exact = [o for o in graph.objects(c, SKOS.exactMatch)]
            subs = [o for o in graph.objects(c, RDFS.subClassOf)]
            self.terms[c] = dict(
                iri=c, alts=alts, scopes=scopes, patterns=patterns,
                roles=roles, status=status, exact=exact, subs=subs,
                defn=list(graph.objects(c, SKOS.definition)),
                label=list(graph.objects(c, SKOS.prefLabel)),
            )

    def resolve(self, header: str, scope: str):
        hits = []
        for iri, t in self.terms.items():
            if scope not in t["scopes"]:
                continue
            if header in t["alts"] or any(re.match(p, header) for p in t["patterns"]):
                hits.append(iri)
        return hits


class TestArbinVendorModule(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.g = Graph()
        cls.g.parse(ARBIN_TTL, format="turtle")
        cls.mod = ArbinModule(cls.g)
        cls.core = Graph()
        cls.core.parse(CORE_TTL, format="turtle")
        cls.core_classes = {
            s for s in cls.core.subjects(RDF.type, OWL.Class)
            if str(s).startswith(str(BDF))
        }
        cls.observed = json.loads(OBSERVED.read_text(encoding="utf-8"))

    def test_module_parses_and_has_terms(self):
        self.assertGreaterEqual(len(self.mod.terms), 70,
                                "expected the full four-tier Arbin term inventory")

    def test_every_term_has_role_scope_label_definition(self):
        errs = []
        for iri, t in self.mod.terms.items():
            n = str(iri).split("#")[1]
            if len(t["roles"]) != 1 or t["roles"][0] not in VALID_ROLES:
                errs.append(f"{n}: role must be exactly one of {VALID_ROLES}, got {t['roles']}")
            if not t["scopes"] or not t["scopes"] <= VALID_SCOPES:
                errs.append(f"{n}: sheetScope must be a non-empty subset of {VALID_SCOPES}, got {t['scopes']}")
            if not t["defn"]:
                errs.append(f"{n}: missing skos:definition")
            if not t["label"]:
                errs.append(f"{n}: missing skos:prefLabel")
        self.assertFalse(errs, "\n".join(errs))

    def test_mapped_terms_point_at_real_core_classes(self):
        """A mapped term uses both rdfs:subClassOf and skos:exactMatch to the
        same existing BDF core class."""
        errs = []
        for iri, t in self.mod.terms.items():
            n = str(iri).split("#")[1]
            if not t["exact"]:
                continue
            for target in t["exact"]:
                if target not in self.core_classes:
                    errs.append(f"{n}: skos:exactMatch target {target} is not a BDF core class")
                if target not in t["subs"]:
                    errs.append(f"{n}: skos:exactMatch {target} not mirrored by rdfs:subClassOf")
        self.assertFalse(errs, "\n".join(errs))

    def test_unverified_terms_carry_no_core_mapping(self):
        errs = []
        for iri, t in self.mod.terms.items():
            n = str(iri).split("#")[1]
            if t["status"] and t["status"][0] == "unverified" and t["exact"]:
                errs.append(f"{n}: unverified term must not assert a core mapping")
        self.assertFalse(errs, "\n".join(errs))

    def test_no_ambiguous_altlabel_within_scope(self):
        """No native header may resolve to more than one term in a given scope."""
        errs = []
        for scope in VALID_SCOPES:
            # collect every literal altLabel that lives in this scope
            labels = set()
            for t in self.mod.terms.values():
                if scope in t["scopes"]:
                    labels |= t["alts"]
            for lbl in labels:
                hits = self.mod.resolve(lbl, scope)
                if len(hits) > 1:
                    names = sorted(str(h).split("#")[1] for h in hits)
                    errs.append(f"[{scope}] {lbl!r} resolves to {names}")
        self.assertFalse(errs, "\n".join(errs))

    def test_observed_headers_resolve_to_exactly_one_term(self):
        errs = []
        for scope, headers in self.observed.items():
            for h in headers:
                hits = self.mod.resolve(h, scope)
                if len(hits) == 0:
                    errs.append(f"[{scope}] UNRESOLVED: {h!r}")
                elif len(hits) > 1:
                    names = sorted(str(x).split("#")[1] for x in hits)
                    errs.append(f"[{scope}] AMBIGUOUS {h!r} -> {names}")
        self.assertFalse(errs, f"{len(errs)} header(s) failed:\n" + "\n".join(errs))

    def test_documented_quirks_resolve_verbatim(self):
        errs = []
        for h, scope in DOCUMENTED:
            hits = self.mod.resolve(h, scope)
            if len(hits) != 1:
                names = sorted(str(x).split("#")[1] for x in hits)
                errs.append(f"[{scope}] {h!r} -> {names or 'UNRESOLVED'}")
        self.assertFalse(errs, "\n".join(errs))

    def test_indexed_families_have_pattern_and_match_arbitrary_index(self):
        """Indexed families resolve indices beyond those enumerated as altLabels."""
        cases = [
            ("TC_Counter7", "timeseries"),
            ("MetaCode_MV_UD12", "timeseries"),
            ("Aux_Voltage(V)_9", "timeseries"),
        ]
        for h, scope in cases:
            hits = self.mod.resolve(h, scope)
            self.assertEqual(len(hits), 1, f"{h!r} should resolve via headerPattern, got {hits}")


if __name__ == "__main__":
    unittest.main()
