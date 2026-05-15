About the Battery Data Format Ontology
======================================

The Battery Data Alliance
--------------------------

The `Battery Data Alliance (BDA) <https://lfenergy.org/projects/battery-data-alliance/>`_ is a Linux Foundation Energy project whose mission is to accelerate battery research and development by making battery data more accessible, interoperable, and reusable. Members include research institutions, national laboratories, and industry partners across the battery value chain.

The Battery Data Format
-----------------------

The **Battery Data Format (BDF)** is a community standard for time-series battery cycling data. It defines a canonical set of column names — ``test_time_second``, ``voltage_volt``, ``current_ampere``, and so on — that cycler software, data pipelines, and analysis tools can agree on. By standardising column names and units, BDF eliminates the fragile, instrument-specific parsers that currently make battery data difficult to share and reuse.

BDF files are plain CSV or Parquet: the format imposes no new file type, only a naming convention and a unit system (SI throughout). A converter plugin translates each instrument's native headers into BDF canonical columns at ingest time.

The BDF Ontology
----------------

The BDF Ontology gives every BDF column a stable, web-resolvable identity. Where the format says "name this column ``voltage_volt``", the ontology says "this column represents instantaneous voltage measurements, in volts, aligned to these international standards".

Each BDF quantity class is:

- An **OWL class** in the EMMO class hierarchy, with a formal unit restriction
- A **SOSA observable property** (``rdfs:subClassOf sosa:ObservableProperty``), enabling integration with sensor data frameworks
- Aligned to a **QUDT quantity kind** via ``skos:exactMatch`` and to a **QUDT unit** via ``qudt:hasUnit``
- Annotated with a **UCUM unit code** (``schema:unitCode``) for tool-agnostic unit handling
- Linked to **PROV-O derivation relationships** (``prov:wasDerivedFrom``) for derived quantities such as power and energy

This layered design means that a software agent encountering a BDF column can resolve its meaning through any of several well-known vocabularies, without requiring BDF-specific knowledge.

Vocabulary Alignments
---------------------

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Vocabulary
     - Namespace prefix
     - Role in BDF
   * - `EMMO <https://emmo.info>`_
     - ``emmo:``
     - Primary class hierarchy; unit restrictions via ``hasMeasurementUnit``
   * - `QUDT <https://qudt.org>`_
     - ``quantitykind:``, ``unit:``
     - Quantity kind and unit alignments (``skos:exactMatch``, ``qudt:hasUnit``)
   * - `SOSA/SSN <https://www.w3.org/TR/vocab-ssn/>`_
     - ``sosa:``
     - Each BDF class is a subclass of ``sosa:ObservableProperty``
   * - `PROV-O <https://www.w3.org/TR/prov-o/>`_
     - ``prov:``
     - Derivation graph for computed quantities (power, energy, capacity integrals)
   * - `schema.org <https://schema.org>`_
     - ``schema:``
     - ``schema:unitCode`` (UCUM), ``schema:unitText``, ``schema:measurementTechnique``
   * - `SKOS <https://www.w3.org/2004/02/skos/core>`_
     - ``skos:``
     - Labels, definitions, notations, and cross-vocabulary alignments

Design Principles
-----------------

**Stable IRIs.**
All term IRIs are minted under ``https://w3id.org/battery-data-alliance/`` and are resolved via the w3id.org persistent identifier service. IRIs will not change between versions; deprecated terms are marked with ``owl:deprecated`` rather than removed.

**SI units throughout.**
All BDF canonical quantities are in SI base or derived units. Vendor-specific unit variants (mAh, hours) are handled by converter plugins using ``schema:unitCode`` annotations in the vendor schema files; the canonical ontology always reflects the normalised SI value.

**Separation of concerns.**
The ontology describes *what quantities are*. The CSVW canonical schema describes *what a valid BDF file looks like*. Vendor schemas describe *how each instrument's output maps to canonical BDF*. These three layers are independently versioned and resolvable.

**Multi-vocabulary coverage.**
Rather than choosing a single vocabulary, BDF aligns to several. An EMMO-aware reasoner, a QUDT-based unit converter, a SOSA observation processor, and a schema.org crawler can all extract meaningful information from the same ontology file without any of them being the "primary" consumer.

How to Cite
-----------

If you use the BDF Ontology in a publication, please cite it as:

.. code-block:: text

   Battery Data Alliance (2026). Battery Data Format Ontology, version 1.0.0.
   https://w3id.org/battery-data-alliance/ontology/battery-data-format/1.0.0

The DOI is pending. The ontology is licensed under the `Apache License 2.0 <https://www.apache.org/licenses/LICENSE-2.0>`_.

Contributing
------------

Contributions are welcome. Please see the `contributing guide <https://github.com/BatteryDataAlliance/BDAOntology/blob/main/.github/CONTRIBUTING.md>`_ and `code of conduct <https://github.com/BatteryDataAlliance/BDAOntology/blob/main/CODE_OF_CONDUCT.md>`_ before opening a pull request.
