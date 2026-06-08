# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.0] - 2026-06-08

### Added

- `step_cumulative_capacity_ah` and `step_cumulative_energy_wh`: replacements for the deprecated `step_capacity_ah` / `step_energy_wh`. Running accumulation of throughput within the step, reset at each step transition; concept unchanged. Carry `prov:wasRevisionOf` / `dcterms:replaces` back-links, and retain the legacy names as `skos:altLabel`.
- `step_net_capacity_ah` and `step_net_energy_wh`: completed from prefLabel-only stubs to the full annotation set; defined as `step_charging_* − step_discharging_*` (running signed integral over the step, reset at each step transition). The step capacity and energy families now mirror the test level: charging, discharging, net, cumulative.

### Deprecated

- `step_capacity_ah` → use `step_cumulative_capacity_ah`. Renamed for consistency with the {charging, discharging, net, cumulative} naming convention; tombstoned with `owl:deprecated true` and `dcterms:isReplacedBy`. The IRI continues to resolve.
- `step_energy_wh` → use `step_cumulative_energy_wh`. Same treatment.

## [1.0.0] - 2026-05-14

### Added

**Ontology enrichment**
- QUDT alignment: `skos:exactMatch quantitykind:X`, `qudt:hasUnit`, `rdfs:seeAlso unit:X` on all 40 quantity classes
- `schema:unitCode` (UCUM), `schema:unitText`, and `schema:measurementTechnique` annotations on all quantity classes
- SOSA alignment: all 40 BDF quantity classes declare `rdfs:subClassOf sosa:ObservableProperty` (OWL 2 DL)
- PROV-O derivation graph: `prov:wasDerivedFrom` on 13 derived quantities (power, capacity integrals, energy integrals, EIS computed components)
- New quantity classes: `step_id`, `step_type`, `step_index`, `step_count`, `surface_temperature_celsius`, `temperature_t1`–`t5_celsius`, `surface_pressure_pa`, `applied_pressure_pa`, EIS quantities (`absolute_impedance_ohm`, `real_impedance_ohm`, `imaginary_impedance_ohm`, `phase_degree`, `frequency_hertz`)
- `prov:`, `sosa:`, `quantitykind:`, `unit:`, `schema:` prefix declarations

**Schema and vendor schemas**
- `schema/schema.json`: full canonical CSVW schema with `csvw:propertyUrl` pointing to BDF class IRIs, `hasMeasurementUnit`, `qudt:hasUnit`, `qudt:hasQuantityKind`, `schema:unitCode`, `csvw:required` flags
- `schema/vendors/`: 10 new CSVW vendor column-mapping schemas: Arbin, Basytec, Bio-Logic EC-Lab MPT, Digatron, LANDT CCS/CSV/TXT, Neware CSV, Neware NDA binary, Novonix UHPC

**Context**
- `context/context.json`: lean 3.6 KB BDF-only JSON-LD context (replaced 517 KB full EMMO dump); 58 terms; all required prefixes

**CI/CD**
- `pyproject.toml` replaces `requirements.txt` and `requirements-docs.txt`; optional `[docs]` and `[ontopy]` dependency groups; Python ≥ 3.11
- Decomposed `.github/scripts/` into `config.py`, `context_gen.py`, `rst_gen.py`, `checks.py`, `validate.py`; `ontology_toolkit.py` is now a thin entry point
- Rewritten `ci.yml`: two-job pipeline (validate + check-context), pip caching, no bot commits to source branches
- Rewritten `docs-build-and-deploy.yml`: concurrency guard, no git push to source branches
- `foops-badge-update.yml` removed; badge generation folded into the docs workflow

**Tests**
- Expanded from 3 to 14 tests covering: SOSA subClassOf alignment, PROV derivation graph completeness, context prefix coverage, step column regression guards, `unit:CountingUnit` regression guard

**Documentation**
- New pages: `concepts.rst` (CSVW/SOSA/EMMO architecture), `vendor_schemas.rst` (instrument reference)
- Filled pages: `about.rst`, `examples.rst` (SOSA observations, SPARQL queries), `faq.rst`
- Updated landing page with orientation text and six navigation cards
- `generate_specification.py` enriched with UCUM and Quantity Kind columns
- `docs/README.md` replaces `README.org` with current build instructions

**Infrastructure**
- `tools/verify_htaccess_rules.py`: standalone mod_rewrite simulator for w3id.org redirect verification (28/28 rules)
- w3id.org `.htaccess`: added `application/ld+json` content negotiation, vendor schema IRI resolution, fixed unreachable `-inferred` alternate rule

### Changed

- `step_capacity_ah` and `step_energy_wh`: redefined as **unsigned** (magnitude, always ≥ 0); direction of transfer indicated by `step_type` or sign of `current_ampere`
- `cycle_count`: definition tightened to two explicit constraints — non-negative integer, monotonically non-decreasing; no constraint on starting value
- `schema:unitCode` replaces custom `bdf:sourceUnit` in all vendor schemas
- `csvw:propertyUrl` values corrected from invented `bdf:hasXxxValue` IRIs to actual BDF class IRIs
- `qudt:unit` corrected to `qudt:hasUnit` throughout `schema.json`
- `unit:CountingUnit` corrected to `unit:NUM` for `cycle_count` and `step_count`
- `csvw:primaryKey` corrected from string to array form per CSVW spec

### Removed

- `requirements.txt`, `requirements-docs.txt` (superseded by `pyproject.toml`)
- `foops-badge-update.yml` workflow (consolidated)
- `purl/.htaccess`, `purl/README.md` (superseded by w3id.org redirect; now maintained at [w3id.org/battery-data-alliance](https://github.com/perma-id/w3id.org/tree/master/battery-data-alliance))
- `battery-data-format-inferred.ttl` from version control (generated artefact; served via CI and GitHub Pages)

## [0.1.0-beta] - 2025-01-23

- Initial public beta release of the Battery Data Format application ontology.
