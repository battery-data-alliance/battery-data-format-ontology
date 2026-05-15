Frequently Asked Questions
==========================

.. contents:: Questions
   :local:
   :depth: 1

What is the Battery Data Format?
---------------------------------

BDF is a community standard for time-series battery cycling data. It defines a canonical set of column names and SI units for the quantities that cycler instruments record — voltage, current, time, capacity, energy, temperature, and so on. A BDF-compliant file uses these canonical names regardless of which instrument produced the data, making it straightforward to build tools that work across instruments and laboratories without custom parsers.

What does the BDF Ontology add on top of BDF?
----------------------------------------------

The format defines *names*. The ontology defines *meaning*. By assigning each column a stable web IRI and linking it to formal definitions in EMMO, QUDT, SOSA, and schema.org, the ontology enables:

- **Machine readability** — software agents can resolve a column name to its physical meaning, unit, and quantity kind without any BDF-specific code.
- **Cross-vocabulary interoperability** — the same quantity is aligned to EMMO, QUDT, and SOSA simultaneously, so tools built on any of those vocabularies can consume BDF data.
- **Dataset discoverability** — JSON-LD metadata linking a dataset to the BDF schema makes it indexable by data catalogues and AI systems that understand linked data.
- **Derivation tracking** — PROV-O annotations record which quantities are derived from which base measurements.

Which cycler instruments are supported?
----------------------------------------

Ten vendor schemas are currently available:

- **Arbin Instruments** — MITS Pro CSV and XLSX exports
- **Basytec GmbH** — TXT and DAT exports
- **Bio-Logic Science Instruments** — EC-Lab / BT-Lab MPT ASCII
- **Digatron Power Electronics** — CSV export
- **LANDT Instruments** — CCS, CSV (modern), and TXT (older) exports
- **Neware Technology** — CSV (English and Chinese headers) and binary NDA/NDAX
- **Novonix** — UHPC CSV export

See :doc:`Vendor Schemas </pages/vendor_schemas>` for full details and column coverage.

My instrument is not listed. Can I add it?
-------------------------------------------

Yes. A vendor schema is a JSON file of around 20–50 lines following a straightforward structure. See the *Adding a New Vendor Schema* section of the :doc:`Vendor Schemas </pages/vendor_schemas>` page for step-by-step instructions and open a pull request against the `BDAOntology repository <https://github.com/BatteryDataAlliance/BDAOntology>`_.

What does ``schema:unitCode`` mean on a vendor column?
-------------------------------------------------------

It signals that the instrument exports that column in a non-SI unit. The value is a UCUM code — for example ``"h"`` for hours, ``"mA"`` for milliamperes, ``"mA.h"`` for milliampere-hours. The BDF normaliser reads this annotation and applies the appropriate conversion factor so that the canonical BDF column always contains SI values.

If ``schema:unitCode`` is absent from a vendor column entry, the values are already in the BDF canonical SI unit and no conversion is applied.

What is the difference between ``test_time_second`` and ``unix_time_second``?
------------------------------------------------------------------------------

``test_time_second`` is elapsed time since the start of the test, in seconds — a relative timestamp that resets to zero at the beginning of each test. ``unix_time_second`` is absolute wall-clock time as a Unix epoch timestamp (seconds since 1970-01-01T00:00:00 UTC). BDF requires at least one of the two to be present; many instruments export both.

How are derived quantities handled?
-------------------------------------

Quantities such as ``power_watt`` (= V × I), ``step_capacity_ah`` (∫ I dt over a step), and ``net_energy_wh`` are annotated with ``prov:wasDerivedFrom`` in the ontology, which records their input dependencies. This is informational — the ontology does not encode the formula, only the dependency graph. The actual computation is performed by the BDF Python package.

Instruments that export these quantities directly are represented in vendor schemas; the normaliser accepts the instrument's value without recomputing it.

Why does the ontology use multiple vocabularies (EMMO, QUDT, SOSA)?
---------------------------------------------------------------------

Different tools speak different vocabularies. An EMMO-aware reasoner, a QUDT unit converter, and a SOSA sensor framework all have legitimate uses for BDF data but expect different entry points. Rather than choosing one, the BDF Ontology aligns to all three, so each tool community gets what it needs from the same IRI without any translation layer.

This is not redundancy — each vocabulary contributes something distinct: EMMO provides the formal class hierarchy with unit restrictions; QUDT provides engineering-grade unit and quantity-kind links; SOSA enables integration with sensor observation data models.

How do I validate that a BDF file is correct?
----------------------------------------------

The BDF Python package (``battery-data-format``) performs column-level validation at read time: it checks that required columns are present, that datatypes are correct, and that values fall within plausible ranges. SHACL shapes for graph-level validation are planned for a future release and will be resolvable at:

.. code-block:: text

   https://w3id.org/battery-data-alliance/ontology/battery-data-format/shapes

How do I reference the BDF Ontology in a publication?
-------------------------------------------------------

.. code-block:: text

   Battery Data Alliance (2026). Battery Data Format Ontology, version 1.0.0.
   https://w3id.org/battery-data-alliance/ontology/battery-data-format/1.0.0

The DOI is pending. The ontology is licensed under the `Apache License 2.0 <https://www.apache.org/licenses/LICENSE-2.0>`_.

Where can I report a bug or request a new feature?
----------------------------------------------------

Please open an issue on the `BDAOntology GitHub repository <https://github.com/BatteryDataAlliance/BDAOntology/issues>`_. For sensitive security disclosures, see ``SECURITY.md`` in the repository root.
