# ADR 0001 — Schedule-scoped core terms and the Arbin vendor ontology module

- Status: Accepted
- Date: 2026-07-14
- Scope: BDF ontology 1.3.0

This is the first architecture decision record in this repository; it establishes `docs/adr/` as the home for future ADRs (one file per decision, MADR-style).

## Context

Arbin Battery Test System cyclers export a large, dialect-ridden set of native columns and fields across four surfaces: channel time-series, EIS (`ACIM_chan_1`) sheets, statistics (`StatisticsByCycle/Step`) sheets, and `Global_Info` metadata, over the MITS / MITS_PRO / DataPro CSV and XLSX formats plus the `.res`, SQL, and h5 backends. A five-laboratory, seven-schedule survey of real exports established two problems:

1. **The Charge/Discharge Capacity and Energy accumulators reset at operator-authored boundaries.** In a real Arbin export the accumulators reset at 3 of ~60 step boundaries while the cycle index stayed constant — a reset pattern that fits none of BDF's existing observation scopes (bare = never, `cycle_*` = per cycle, `step_*` = per step). Empirical re-verification for this release (shandong + melasta, ~376k rows) confirmed that `Charge_Capacity` / `Discharge_Capacity` themselves reset at scripted step boundaries, so they are neither test-scoped nor cycle-scoped. They were previously mis-typed, with the resulting validity failures suppressed by four `xfail`s in the bdf package.

2. **No vendor layer resolved the full native header set to honest semantics.** The existing `schema/vendors/arbin_csv.json` CSVW crosswalk maps only the subset of columns that have a core equivalent and silently drops everything else, so an agent meeting a raw Arbin header could not always resolve it.

## Decision 1 — Mint four schedule-scoped **core** terms

Add to the BDF core ontology: `schedule_charging_capacity_ah`, `schedule_discharging_capacity_ah`, `schedule_charging_energy_wh`, `schedule_discharging_energy_wh`, each defined as an accumulator "since the most recent **schedule-defined reset event**", carrying the reset invariant (a value decreases only at a reset, and only to zero), a `scopeNote` warning against cross-test aggregation, and the coincidence property (with no resets the quantity equals the test-scoped term, enabling verified upgrade by consumers). They are full annotation-parity siblings of the `step_*` family (labels, definitions, EMMO unit restrictions, electrochemistry superclasses, `qudt:hasQuantityKind`, LaTeX symbol/formula, PROV derivation, schema.org fields) and appear as columns in the CSVW schema and generated context.

**These are core, not vendor, terms** because: the vendor module is a crosswalk, so its mapping target must be vendor-neutral; the term's intension ("accumulator with test-program-defined reset windows") contains nothing Arbin-specific — only its current attestation is Arbin-only; and mixing namespaces in a flat table schema breaks BDF's lexical header → context architecture.

### Minting gate (recorded for reuse)

A **core** data-column term requires all of: (i) real instances in actual exports; (ii) information not expressible via existing terms plus metadata; (iii) a vendor-neutral intension (definable without naming any vendor); (iv) a behaviourally testable contract. `schedule_*` passes all four. Typical vendor quirks fail (iii) and therefore stay in a vendor module.

### Guardrails encoded on the terms

Same EMMO parent as the bare/`cycle_`/`step_` sibling (an observation-scope modifier, not a new quantity kind); instrument-authoritative (never recomputed from current/time); deliberately **no** `schedule_cumulative_*` / `schedule_net_*` (aggregation across program-defined windows is meaningless); a soft authoring-time lint remains future work (warn when a `schedule_*` column's observed resets align 1:1 with step/cycle boundaries, suppressible by converter provenance — Arbin data legitimately always maps to `schedule_*` because the rule is program-defined even when realized resets coincide with cycles/steps).

## Decision 2 — Represent the Arbin vendor module as a **TTL ontology module**

The repository previously had no vendor *ontology*, only CSVW crosswalks. For BDF 1.3.0 we add `vendors/arbin.ttl`: a standalone Turtle ontology, namespace `arbin:` = `…/battery-data-format/vendors/arbin#`, and `owl:imports` the core ontology. (Chosen over an enriched CSVW schema so vendor concepts are first-class, reasoner-visible classes; the CSVW crosswalk remains the normaliser's runtime artifact.) The module is deliberately **not** added to `config.yml` `ttl_files`: the context/RST generators filter by the core `bdf#` prefix, so listing it there would only emit an empty documentation section while pulling the module into the tag-gated deploy path. Instead it is parsed and structurally validated by its dedicated test suite, which runs in the same CI job as the core tests.

Design rules:

- **One `owl:Class` per concept**, not per header spelling. Every dialect spelling — space vs underscore, bare `.res`, MITS 7 numeric `PV` codes, and quirks (` Item_ID` leading space, `Has Specail` typo, `Reference_Voltage(Ohm)` unit-label bug, GBK `Aux_Temperature(¡æ)_N` mojibake, right-padded statistics `Date_Time`) — is a **verbatim `skos:altLabel`**.
- **All four tiers are in scope**, including zero-scientific-content bookkeeping fields, which carry `arbin:role "bookkeeping"` rather than being excluded, so agents can distinguish "no scientific content" from "not modelled". This includes the scattered `Global_Info` report layout: its `Mapped_Aux_Number` and `Log_Data_Flag` blocks resolve via `internal_bookkeeping` / `log_flags`.
- Machine-readable annotations on every term: `arbin:role` (measurement/derived/identifier/bookkeeping/metadata), `arbin:sheetScope` (timeseries/eis/statistics/metadata), `arbin:headerPattern` (regex for indexed families — aux channels, `TC_Counter`, `MetaCode_MV_UD`), and `arbin:verificationStatus "unverified"` where semantics/units are unconfirmed.
- **Mapping convention:** a mapped concept carries both `rdfs:subClassOf` and `skos:exactMatch` to the same core IRI (`owl:equivalentClass` is not used because the repo has no precedent for it). Two deliberate exceptions to `exactMatch`: a concept maps only to the term the repo itself asserts — e.g. `internal_resistance_ohm` maps to the method-agnostic core parent, not the DC subtype, because the export does not fix the method; and an indexed family that spans channels (`aux_temperature_celsius` over `Aux_Temperature_N`) asserts no single-channel equivalence — it uses `rdfs:seeAlso` to point at the `temperature_tN_celsius` family instead, since `exactMatch` to `t1` would be false for `_2`, `_3`. Vendor-only measured/derived concepts are `rdfs:subClassOf sosa:ObservableProperty`; vendor-only identifiers/bookkeeping/metadata are plain classes. Unverified terms carry no core mapping.
- **Coverage is tested** (`tests/test_arbin_vendor_module.py` + `tests/data/arbin_observed_headers.json`): every header observed in real exports across all four sheet scopes, and every documented quirk, resolves to **exactly one** term within its sheet scope; indexed families resolve arbitrary indices via `headerPattern`.

## Decision 3 — Empirical resolution of the open verification items

Verified against real exports (see the coverage-test data and the term `skos:scopeNote`s):

- **`Capacity (Ah)`** (time-series) is an **unsigned active-direction accumulator** — equal to `Charge_Capacity` on charge steps and `Discharge_Capacity` on discharge steps, re-zeroing 1:1 with `Step_Index`. It is *not* signed net capacity, so it is **not** mapped to `net_capacity_ah`; it stays vendor-only (`arbin:capacity_ah`).
- **`TC_Counter1..4`** are nested schedule loop counters (outer→inner). They do **not** by themselves expose accumulator reset boundaries — resets align with `Step_Index`, not with counter transitions — correcting the prior hypothesis.
- **`AC_Amp_RMS` / `DC_Base`** units are keyed by `Driven_Type`; all accessible EIS data is galvanostatic → amperes (`DC_Base` observed constant 0 = at OCV). The potentiostatic→volts branch is a documented convention, not observed. No standalone `Amplitude` column exists in the sampled files; `arbin:amplitude` is retained from the documented inventory and kept `unverified`.
- **`mAh/g`** is `Capacity(Ah) × 1000 / MASS`, inheriting `capacity_ah`'s unsigned, step-resetting behaviour (not derived from the charge/discharge accumulators).

## Alternatives considered and rejected

- **Drop-and-derive** the accumulators (map to `cycle_*` and recompute): rejected — the reset rule is not recoverable from the exported time-series, so recomputation would silently fabricate boundaries; the survey shows the resets are real and program-defined.
- **Place `schedule_*` in the vendor namespace**: rejected — a crosswalk's target must be vendor-neutral, and the intension is not Arbin-specific (Decision 1).
- **Per-column CSVW metadata scoping** instead of core terms: rejected — BDF's contract is a flat lexical header → term mapping via the JSON-LD context; encoding scope in per-column CSVW annotations breaks that architecture.
- **Enriched CSVW vendor schema** instead of a TTL ontology module for Decision 2: considered as the convention-preserving option, rejected in favour of first-class reasoner-visible vendor classes.

## Consequences

- The core ontology gains four terms; the Arbin module (`vendors/arbin.ttl`, 75 classes) resolves every observed native header and documented quirk to honest semantics. CI parses and tests both.
- **Follow-up (separate, per the release plan):** the bdf Python package remap — cover the underscore dialect and an xlsx plugin in `table_normalizers.py`, remap the accumulators to the `schedule_*` terms, replace the four `xfail`s with the real monotone-except-resets validity rule, and refresh the ontology snapshot. Not to be started until the 1.3.0 ontology release lands; the module crosswalk here is the authoritative source for it. Note that until that remap, `arbin_csv.json` still maps the accumulators to cycle-scope terms — a known, deferred divergence from this module.

## Amendment (2026-07-19): assignment, not only reset

Arbin's MITS software team (T. D. Khanh) confirmed that the four accumulator fields (PV23-PV26) are governed by two schedule controls: "Set variable(s)", which resets selected fields to zero (with increment/decrement options for counters), and "Set value", which can assign an arbitrary value or a formula result to a field mid-test. The original decision's reset invariant ("a value decreases only at a reset, and only to zero") therefore over-claimed: it held for all ten surveyed exports but is not guaranteed by the instrument. The term definitions were generalized to "schedule-defined assignment" semantics (typically a reset to zero; any value may be assigned) in the 1.3.0 release. Consequence for validation: the planned decreases-only-to-zero validity rule weakens to monotonic-between-discontinuities, with any discontinuity attributed to the schedule; the verified-upgrade path to test-scoped terms must check for the absence of any discontinuity, not only drops.
