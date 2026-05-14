How the Ontology Works
======================

This page explains the architecture of the BDF Ontology — how the pieces fit together and what a machine agent can do with them.

Overview
--------

The BDF semantic stack has three layers:

.. code-block:: text

   ┌─────────────────────────────────────────────────────────┐
   │  Vendor schemas (schema/vendors/*.json)                  │
   │  Header synonyms + unit conversion hints per instrument  │
   └────────────────────┬────────────────────────────────────┘
                        │ csvw:name maps to
   ┌────────────────────▼────────────────────────────────────┐
   │  Canonical CSVW schema (schema/schema.json)              │
   │  One column per BDF quantity · csvw:propertyUrl → IRI    │
   └────────────────────┬────────────────────────────────────┘
                        │ IRI resolves to
   ┌────────────────────▼────────────────────────────────────┐
   │  BDF Ontology (battery-data-format.ttl)                  │
   │  OWL class · EMMO · QUDT · SOSA · PROV · schema.org      │
   └─────────────────────────────────────────────────────────┘

Each layer is independently resolvable and versioned. You can use any layer in isolation, or follow the chain from a raw CSV file all the way to a formal semantic description.

The ``csvw:propertyUrl`` Pattern
---------------------------------

The canonical CSVW schema connects each column to the ontology via ``csvw:propertyUrl``. For example, the voltage column entry looks like this:

.. code-block:: json

   {
     "csvw:name": "voltage_volt",
     "csvw:titles": "Voltage / V",
     "csvw:propertyUrl": "bdf:voltage_volt",
     "csvw:datatype": { "csvw:base": "xsd:decimal" },
     "hasMeasurementUnit": { "@id": "emmo:Volt" },
     "qudt:hasUnit": { "@id": "unit:VLT" },
     "schema:unitCode": "V",
     "csvw:required": true
   }

The ``csvw:propertyUrl`` value ``bdf:voltage_volt`` expands to the full IRI
``https://w3id.org/battery-data-alliance/ontology/battery-data-format#voltage_volt``.

When a CSVW processor converts a BDF file to RDF, each data row produces triples of the form:

.. code-block:: turtle

   _:row123 bdf:voltage_volt "3.712"^^xsd:decimal .

The property IRI is the BDF class IRI — so the predicate *is* the observable property class, which is exactly what SOSA expects.

What an Agent Finds at a BDF Class IRI
---------------------------------------

When an agent dereferences ``https://w3id.org/battery-data-alliance/ontology/battery-data-format#voltage_volt``
(via content negotiation, receiving Turtle), it finds:

.. code-block:: turtle

   @prefix bdf:          <https://w3id.org/battery-data-alliance/ontology/battery-data-format#> .
   @prefix emmo:         <https://w3id.org/emmo#> .
   @prefix owl:          <http://www.w3.org/2002/07/owl#> .
   @prefix quantitykind: <http://qudt.org/vocab/quantitykind/> .
   @prefix qudt:         <http://qudt.org/schema/qudt/> .
   @prefix rdfs:         <http://www.w3.org/2000/01/rdf-schema#> .
   @prefix schema:       <https://schema.org/> .
   @prefix skos:         <http://www.w3.org/2004/02/skos/core#> .
   @prefix sosa:         <http://www.w3.org/ns/sosa/> .
   @prefix unit:         <http://qudt.org/vocab/unit/> .

   bdf:voltage_volt a owl:Class ;
       rdfs:subClassOf sosa:ObservableProperty,
           emmo:EMMO_17b031fb_4695_49b6_bb69_189ec63df3ee ;
       rdfs:subClassOf [ a owl:Restriction ;
           owl:onProperty emmo:EMMO_bed1d005_b04e_4a90_94cf_02bc678a8569 ;
           owl:someValuesFrom emmo:Volt ] ;
       skos:prefLabel "Voltage / V"@en ;
       skos:definition "Instantaneous voltage recorded in volt."@en ;
       skos:exactMatch quantitykind:Voltage ;
       qudt:hasUnit unit:VLT ;
       schema:unitCode "V" ;
       schema:unitText "volt"@en .

From this single node the agent can determine:

- **What kind of quantity** — ``skos:exactMatch quantitykind:Voltage`` (QUDT)
- **What unit** — ``qudt:hasUnit unit:VLT``, ``schema:unitCode "V"`` (UCUM), ``hasMeasurementUnit emmo:Volt`` (EMMO)
- **Where in the EMMO hierarchy** — ``rdfs:subClassOf emmo:EMMO_17b031fb...`` (ElectricPotential)
- **SOSA role** — ``rdfs:subClassOf sosa:ObservableProperty``

No BDF-specific knowledge is required. Any agent that understands QUDT, SOSA, or EMMO can extract meaningful information.

SOSA Observation Pattern
-------------------------

Because every BDF class is a subclass of ``sosa:ObservableProperty``, BDF data can be expressed as SOSA observations. A single row from a BDF file maps naturally to:

.. code-block:: turtle

   ex:obs_456 a sosa:Observation ;
       sosa:observedProperty bdf:voltage_volt ;
       sosa:hasFeatureOfInterest ex:cell_A001 ;
       sosa:resultTime "2025-03-01T14:23:01Z"^^xsd:dateTime ;
       sosa:hasSimpleResult "3.712"^^xsd:decimal .

   ex:obs_457 a sosa:Observation ;
       sosa:observedProperty bdf:current_ampere ;
       sosa:hasFeatureOfInterest ex:cell_A001 ;
       sosa:resultTime "2025-03-01T14:23:01Z"^^xsd:dateTime ;
       sosa:hasSimpleResult "-2.000"^^xsd:decimal .

A full BDF time-series becomes a set of linked SOSA observations sharing a ``sosa:FeatureOfInterest`` (the cell under test) and timestamped via ``sosa:resultTime``.

Derivation Graph
-----------------

Quantities that are computed rather than directly measured are annotated with ``prov:wasDerivedFrom`` to express their input dependencies. This lets agents determine which base measurements are required to reproduce a derived column.

**Tier 1 — derived from direct measurements:**

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Quantity
     - Derived from
   * - ``power_watt``
     - ``voltage_volt``, ``current_ampere``
   * - ``step_capacity_ah``
     - ``current_ampere``, ``step_time_second``
   * - ``charging_capacity_ah``
     - ``current_ampere``, ``test_time_second``
   * - ``discharging_capacity_ah``
     - ``current_ampere``, ``test_time_second``
   * - ``cumulative_capacity_ah``
     - ``current_ampere``, ``test_time_second``
   * - ``charging_energy_wh``
     - ``power_watt``, ``test_time_second``
   * - ``discharging_energy_wh``
     - ``power_watt``, ``test_time_second``
   * - ``cumulative_energy_wh``
     - ``power_watt``, ``test_time_second``

**Tier 2 — derived from derived quantities:**

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Quantity
     - Derived from
   * - ``net_capacity_ah``
     - ``charging_capacity_ah``, ``discharging_capacity_ah``
   * - ``step_energy_wh``
     - ``power_watt``, ``step_time_second``
   * - ``net_energy_wh``
     - ``charging_energy_wh``, ``discharging_energy_wh``

**EIS computed components:**

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Quantity
     - Derived from
   * - ``absolute_impedance_ohm``
     - ``real_impedance_ohm``, ``imaginary_impedance_ohm``
   * - ``phase_degree``
     - ``real_impedance_ohm``, ``imaginary_impedance_ohm``

These relationships are encoded as ``prov:wasDerivedFrom`` triples in the ontology and can be queried directly with SPARQL. See :doc:`Examples </pages/examples>` for a worked query.

Content Negotiation
--------------------

All BDF IRIs support content negotiation via w3id.org:

.. list-table::
   :widths: 35 65
   :header-rows: 1

   * - ``Accept`` header
     - Response
   * - ``text/html``
     - Human-readable HTML documentation
   * - ``text/turtle``
     - Turtle serialisation of the ontology
   * - ``application/ld+json``
     - JSON-LD context document
   * - *(any other)*
     - Turtle (default)

This means that the same IRI serves a browser, an RDF library, and a JSON-LD processor without any client-side configuration.
