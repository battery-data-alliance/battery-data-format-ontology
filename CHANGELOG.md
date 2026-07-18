# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - Unreleased

### Added
- Four schedule-scoped quantity terms: `schedule_charging_capacity_ah`, `schedule_discharging_capacity_ah`, `schedule_charging_energy_wh`, `schedule_discharging_energy_wh` -- accumulators "since the most recent schedule-defined reset event". These carry the vendor accumulator columns of schedule-driven cyclers (e.g. Arbin MITS Charge_/Discharge_Capacity/Energy) under truthful semantics: reset points are operator-authored (per cycle, at scripted steps, or never), so the columns match no test-, cycle-, or step-scoped term in general. Definitions carry the reset invariant (decreases only to zero at a reset) and a scopeNote warning against cross-test aggregation; when a schedule defines no resets the quantity coincides with the test-scoped term, enabling verified upgrade by consumers. Evidence base: a five-laboratory, seven-schedule Arbin survey (see battery-data-format reference-data scorecards).
- Corresponding columns in the CSVW schema and generated JSON-LD context.
- Arbin XLSX vendor schema (`schema/vendors/arbin_xlsx.json`): the CSVW crosswalk for Arbin multi-sheet XLSX exports, resolving the previously dead `…/schema/vendors/arbin_xlsx` IRI referenced by the published Zenodo record. Covers both header dialects; the Charge/Discharge accumulators map to the new `schedule_*` terms and auxiliary temperature to `temperature_t1_celsius`, and it cross-references the `vendors/arbin` ontology module. (The `arbin_csv` schema still maps the accumulators to cycle-scope terms and temperature to `ambient_temperature_celsius`; harmonising it is tracked with the deferred package remap.)
- Docs: corrected the `vendor_schemas.rst` claim that the Digatron AhAccu/AhBal/AhStep accumulators are "recomputed by the normaliser" (no such mechanism) to state the divergence factually, and documented that Digatron's `#s` duration columns are emitted in milliseconds (added as `skos:note`s on the `digatron_csv` time columns).
- Arbin vendor ontology module (`vendors/arbin.ttl`, namespace `arbin:`): the first vendor *ontology* module (the existing `schema/vendors/*.json` remain the runtime CSVW crosswalks). One `owl:Class` per concept across all four export surfaces (channel time-series, EIS `ACIM` sheets, statistics sheets, `Global_Info` metadata; CSV/XLSX/`.res`/SQL/h5), covering **every** native column including zero-content bookkeeping fields. Every dialect spelling -- space vs underscore, bare `.res`, MITS 7 `PV` codes, and quirks (` Item_ID`, `Has Specail`, `Reference_Voltage(Ohm)`, GBK mojibake, padded `Date_Time`) -- is a verbatim `skos:altLabel`. Concepts with a core equivalent carry `rdfs:subClassOf` + `skos:exactMatch` to the core IRI (the accumulators map to the new `schedule_*` terms); the rest are vendor-only and self-described. Machine-readable `arbin:role`, `arbin:sheetScope`, `arbin:headerPattern`, and `arbin:verificationStatus` annotations. A coverage test parses the module and asserts every observed header and documented quirk resolves to exactly one term within its sheet scope. Empirical verification of `Capacity (Ah)` (unsigned active-direction accumulator), `TC_Counter` (nested loop counters, not reset markers), EIS `AC_Amp_RMS`/`DC_Base` (galvanostatic amperes), and `mAh/g` (mass-scaled `Capacity`) is recorded in the term definitions and `docs/adr/0001`.
- `step_record_index`: the new name of the within-step data-point counter formerly published as `step_index` (same definition, unit, and LaTeX symbol; carries `step_index` as a `skos:altLabel`). Added to the CSVW schema and JSON-LD context; the `landt_ccs` and `novonix_csv` vendor crosswalks now target it.

### Changed
- Quantity-kind links converted from `skos:exactMatch quantitykind:*` to `qudt:hasQuantityKind quantitykind:*` on every term. `exactMatch` asserted an identity between a BDF measurement column and an abstract QUDT quantity kind, which is semantically wrong; `hasQuantityKind` is the QUDT-native typing predicate. Consumers keying on `skos:exactMatch` for quantity kinds must switch predicates.
- Repaired eight unresolvable EMMO electrochemistry parent IRIs on the cycle-scope terms (the `electrochemistry_` prefix had been dropped from the parent class local names, leaving dangling references).
- `step_index` (now `step_record_index`) typed into the count family: `qudt:hasQuantityKind quantitykind:Count`, `rdfs:seeAlso unit:NUM`, and the OWL unit restriction repointed from the nonexistent `emmo:One` onto the same EMMO CountingUnit class used by `record_index`, `step_count`, and `cycle_count`.

### Deprecated
- `step_index`, replaced by `step_record_index` (`owl:deprecated` + `dcterms:isReplacedBy`, concept unchanged). Rationale: virtually every cycler vendor uses "Step Index" for the *program step identifier* (Arbin `Step_Index`, etc.), which maps to `step_id` -- the old name invited exactly that mis-mapping, the most common defect class in the reference-data audit (battery-data-format#54). A legacy column entry remains in the CSVW schema for compatibility.

### Fixed
- Vendor crosswalks pointed at two nonexistent term IRIs: `power_w` (correct: `power_watt`) in `biologic_mpt`, `digatron_csv`, and `novonix_csv`, and `surface_temperature_t1_celsius` in `novonix_csv` -- the latter now maps Novonix `Circuit Temperature` to `temperature_t1_celsius`, matching the battery-data-format normaliser.
- `biologic_mpt` and `digatron_csv` crosswalks retargeted from the deprecated `step_capacity_ah`/`step_energy_wh` to their replacements `step_cumulative_capacity_ah`/`step_cumulative_energy_wh`. The BioLogic `dQ` entry carries a note that its within-step signedness needs verification against real exports (signed would match `step_net_capacity_ah` instead).
- Removed the false claim in the `digatron_csv` `skos:note`s that the battery-data-format normaliser recomputes signed step accumulators from AhCha/AhDch increments (no such mechanism exists); the notes now state the unsigned-accumulator semantics factually. Completes the correction started in the 1.3.0 docs fix for `vendor_schemas.rst`.
- `docs/pages/specification.rst` now includes the four `schedule_*` terms (rows generated from the TTL definitions, symbols, and formulas); they had been missing from the human-readable specification table since the terms merged.

## [Unreleased]

## [1.2.0] - 2026-06-11

### Added

- **Cycle-scope running quantities** (8 terms): `cycle_{charging,discharging,cumulative,net}_capacity_ah` and `cycle_{charging,discharging,cumulative,net}_energy_wh` — running accumulations within the current cycle, reset when `cycle_count` increments (cycle boundaries remain instrument-defined). These are the quantities cyclers natively export in cycle-reset configurations (e.g. Arbin `Charge_Capacity(Ah)` / `Discharge_Capacity(Ah)`, noted in the definitions); the end-of-cycle value of `cycle_discharging_capacity_ah` is the capacity-fade quantity, and the end-of-cycle value of `cycle_net_*` is the per-cycle coulombic slippage / net energy loss. End-of-cycle aggregate terms and the efficiency ratios (`coulombic_efficiency`, `energy_efficiency`) are deferred to the per-cycle summary-table release.
- **Resistance family**: `internal_resistance_ohm` broadened to a method-agnostic parent (symbol `R_int`); new subclasses `dc_internal_resistance_ohm` (`R_DC`, ΔV/ΔI current-pulse methods, instrument-specific) and `ac_internal_resistance_ohm` (`R_AC`, impedance magnitude at fixed frequency, conventionally 1 kHz; vendor "ACR"). The previously released state was internally inconsistent (a DC-specific definition with the Arbin ACR column mapped to it); broadening reconciles existing data without invalidating it.
- `dcterms:isReplacedBy` and `skos:historyNote` added to the `test_time_millisecond` and `unix_time_millisecond` tombstones, so all deprecated terms are now machine-followable to their replacements.
- Arbin vendor schema: `Charge/Discharge_Capacity(Ah)` and `Charge/Discharge_Energy(Wh)` remapped to the new cycle-scope terms (they reset per cycle, contradicting the never-resetting test-level terms they previously mapped to); `ACR(Ohm)` split out and mapped to `ac_internal_resistance_ohm`.
- **Canonical schema completed**: `schema/schema.json` now carries a column for every active ontology term (56 columns, up from 32) — the step-directional family, the new cycle and resistance terms, EIS quantities, and the remaining base terms — generated from the ontology annotations so descriptions cannot drift. Orphan columns fixed: `power_w` renamed to the canonical `power_watt`; the ambiguous `temperature_celsius` column became `surface_temperature_celsius` (explicit-surface), with the unqualified "Temperature / degC" header reassigned to `temperature_t1_celsius` per the default mapping convention. The stale `step_cumulative_*` descriptions (the documentation residue of battery-data-alliance/battery-data-format#36) are synced from the ontology, and all `schema:unitCode` values are normalised to UCUM (e.g. `AMH` → `A.h`, `VLT` → `V`), as originally intended. `csvw:required` flags now agree with the ontology's `:obligation` levels (enforced by a new test): `unix_time_second` corrected from required to non-required, since its obligation is `recommended` — the schema previously contradicted both the ontology and the package validator. Whether time requiredness should become "at least one of test_time/unix_time" (battery-data-alliance/battery-data-format#19) remains an open conformance-policy question for the SHACL profile work.

### Removed

- `scripts/add_latex_annotations.py`: the one-shot bootstrap that seeded the LaTeX annotations. Its data tables predate the 1.1.0/1.2.0 renames, and re-running it would attach stale symbols to deprecated tombstones; the TTL is the sole source of truth for `latexSymbol`/`latexFormula`.

### Changed

- **Energy formulas gated by current direction**: charging/discharging energy integrands changed from `max(±P, 0)` (sign-of-power gating) to `±P·[I ≷ 0]` (current-interval gating), and cumulative energy from `∫|P|` to `∫P·sgn(I)`. Numerically identical wherever voltage is positive (all normal cycling data); the forms now agree with the capacity family and the prose in the cell-reversal edge case (forced over-discharge), where power-sign gating misclassifies dissipated energy as charging energy.

- **Definition clarity pass** (no semantic changes to any quantity; wording only):
  - `current_ampere`: the sign convention is now stated explicitly — positive current charges the test object, negative discharges it; the charging/discharging capacity and energy families are defined by this convention.
  - `test_time_second`: defined as elapsed time since test start, monotonically non-decreasing; pause behaviour is instrument-defined and preserved as reported (was circular "Test time recorded in second").
  - `voltage_volt`: measured across the terminals of the test object.
  - `unix_time_second`: defined as seconds since 1970-01-01T00:00:00 UTC (the Unix epoch), excluding leap seconds.
  - `surface_pressure_pa` vs `applied_pressure_pa` disambiguated: surface pressure is *measured* at the test object surface (may be nonzero from swelling alone); applied pressure is *actively applied and controlled* by an external agent. Each definition cross-references the other.
  - EIS terms (`absolute/real/imaginary_impedance_ohm`, `phase_degree`, `frequency_hertz`): rewritten in sentence style, `schema:description` added; `imaginary_impedance_ohm` states the as-reported sign convention (negative for capacitive behaviour, vs the negated Nyquist plotting convention); `phase_degree` formula uses two-argument `atan2`.
  - All eight step-level `latexFormula` annotations now define `t_s` (start of the current step) inline.
  - `record_index` and `step_time_second` definitions normalised to sentence style.
  - **Temperature channels unqualified**: `temperature_t1`–`t5_celsius` relabelled from "Surface Temperature TN / degC" to "Temperature TN / degC" (old labels retained as `skos:altLabel`, so legacy headers still resolve) and redefined as auxiliary channel readings with setup-defined sensor placement — the labels previously asserted "surface" while the definitions explicitly declined to. They are no longer subclasses of `surface_temperature_celsius` (re-parented to the generic EMMO temperature class); `surface_temperature_celsius` is now the explicitly-surface semantic term, and the two definitions cross-reference each other. A `skos:scopeNote` on `temperature_t1_celsius` states the default mapping convention — unqualified single temperature columns and unqualified numbered channels map to `temperature_t1_celsius`; explicit chamber/environment columns to `ambient_temperature_celsius`; explicit surface columns to `surface_temperature_celsius` — and the Basytec and Digatron vendor schemas are harmonised to it (resolves #9).
  - Usage advice moved out of `cumulative_capacity_ah`'s definition into a new `skos:scopeNote` (declared as an annotation property).
  - `latexSymbol` added for `record_index` (i), `step_count` (k), `step_index` (j), and `unix_time_second` (t_unix).

## [1.1.0] - 2026-06-08

### Added

- `step_cumulative_capacity_ah` and `step_cumulative_energy_wh`: replacements for the deprecated `step_capacity_ah` / `step_energy_wh`. Running accumulation of throughput within the step, reset at each step transition; concept unchanged. Carry `prov:wasRevisionOf` / `dcterms:replaces` back-links, and retain the legacy names as `skos:altLabel`.
- `step_net_capacity_ah` and `step_net_energy_wh`: completed from prefLabel-only stubs to the full annotation set; defined as `step_charging_* − step_discharging_*` (running signed integral over the step, reset at each step transition). The step capacity and energy families now mirror the test level: charging, discharging, net, cumulative.
- `:obligation` annotation property (`required` / `recommended` / `optional`), applied to every non-deprecated quantity class for the default BDF profile: `test_time_second`, `voltage_volt`, `current_ampere` are **required**; `unix_time_second`, `step_count`, `cycle_count`, `ambient_temperature_celsius` are **recommended**; all other columns **optional**. Obligation is profile-scoped — this annotation expresses the default profile only; per-profile conformance is expressed in the SHACL shapes.
- `:latexSymbol` and `:latexFormula` annotation properties, populated for the base and derived quantities (e.g. symbol \(Q_\mathrm{cum}^\mathrm{step}\) and its integral formula).
- Documentation rendering of the math and metadata: the generated **Specification** table gains a *Symbol* column with each derived term's *Formula*, and the per-term reference tables now render `symbol`, `formula`, `obligation`, and a linked `wasDerivedFrom` row. MathJax is enabled (`sphinx.ext.mathjax` for the spec page; `ensure-mathjax.js` for the raw-HTML term tables).

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
