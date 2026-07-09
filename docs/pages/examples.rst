Examples
========

This page shows concrete worked examples of using the BDF Ontology.

.. contents:: On this page
   :local:
   :depth: 1

Dataset Metadata
----------------

The most common use of the ontology is to annotate a BDF dataset with machine-readable metadata. The JSON-LD document below links a dataset to the BDF schema, describes its creators and license, and makes it discoverable by data catalogues and AI tools.

See the :doc:`Quick Start </pages/quick_start>` page for a template you can complete for your own dataset.

.. code-block:: json

   {
     "@context": "https://w3id.org/battery-data-alliance/ontology/battery-data-format/context",
     "@type": "dcat:Dataset",
     "dc:title": "Rate-Test Cycling of Lithium-Polymer Cells for Road Racing",
     "dc:description": "Results from rate-test cycling of Melasta lithium-polymer cells used in electric road racing vehicles.",
     "dc:creator": [
       {
         "@type": "schema:Person",
         "@id": "https://orcid.org/0000-0003-0934-4515",
         "schema:name": "Julian Tolchard"
       }
     ],
     "dc:license": "https://creativecommons.org/licenses/by/4.0/",
     "dc:issued": "2025-03-24",
     "dcat:keyword": ["lithium-polymer", "rate test", "battery cycling"],
     "dcat:distribution": {
       "@type": "dcat:Distribution",
       "dcat:mediaType": "text/csv",
       "dcat:downloadURL": "https://example.com/data.csv",
       "csvw:tableSchema": {
         "@id": "https://w3id.org/battery-data-alliance/ontology/battery-data-format/schema"
       }
     }
   }

Expressing a BDF Row as SOSA Observations
------------------------------------------

Because every BDF quantity class is a subclass of ``sosa:ObservableProperty``, a single data row can be lifted to a set of SOSA observations. This is useful for integrating BDF data with sensor data infrastructure or knowledge graphs.

Given a BDF row:

.. code-block:: text

   test_time_second  voltage_volt  current_ampere  cycle_count
   3600.0            3.712         -2.000          1

The equivalent SOSA representation in Turtle is:

.. code-block:: turtle

   @prefix bdf:  <https://w3id.org/battery-data-alliance/ontology/battery-data-format#> .
   @prefix sosa: <http://www.w3.org/ns/sosa/> .
   @prefix ex:   <https://example.org/> .
   @prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .

   ex:obs_V a sosa:Observation ;
       sosa:observedProperty bdf:voltage_volt ;
       sosa:hasFeatureOfInterest ex:cell_A001 ;
       sosa:resultTime "2025-03-01T15:00:00Z"^^xsd:dateTime ;
       sosa:hasSimpleResult "3.712"^^xsd:decimal .

   ex:obs_I a sosa:Observation ;
       sosa:observedProperty bdf:current_ampere ;
       sosa:hasFeatureOfInterest ex:cell_A001 ;
       sosa:resultTime "2025-03-01T15:00:00Z"^^xsd:dateTime ;
       sosa:hasSimpleResult "-2.000"^^xsd:decimal .

   ex:obs_t a sosa:Observation ;
       sosa:observedProperty bdf:test_time_second ;
       sosa:hasFeatureOfInterest ex:cell_A001 ;
       sosa:resultTime "2025-03-01T15:00:00Z"^^xsd:dateTime ;
       sosa:hasSimpleResult "3600.0"^^xsd:decimal .

SPARQL: Query the Ontology
---------------------------

The following SPARQL queries can be run against the BDF ontology. Load ``battery-data-format.ttl`` into any SPARQL endpoint or use a local rdflib graph.

**List all BDF quantity classes with their UCUM unit codes:**

.. code-block:: sparql

   PREFIX bdf:    <https://w3id.org/battery-data-alliance/ontology/battery-data-format#>
   PREFIX skos:   <http://www.w3.org/2004/02/skos/core#>
   PREFIX schema: <https://schema.org/>

   SELECT ?label ?notation ?unitCode
   WHERE {
     ?class a owl:Class ;
            skos:prefLabel ?label ;
            skos:notation  ?notation .
     OPTIONAL { ?class schema:unitCode ?unitCode . }
     FILTER(STRSTARTS(STR(?class), STR(bdf:)))
     FILTER(LANG(?label) = "en")
   }
   ORDER BY ?notation

**Find all derived quantities and their inputs:**

.. code-block:: sparql

   PREFIX bdf:  <https://w3id.org/battery-data-alliance/ontology/battery-data-format#>
   PREFIX prov: <http://www.w3.org/ns/prov#>
   PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

   SELECT ?derivedLabel ?sourceLabel
   WHERE {
     ?derived prov:wasDerivedFrom ?source ;
              skos:prefLabel      ?derivedLabel .
     ?source  skos:prefLabel      ?sourceLabel .
     FILTER(LANG(?derivedLabel) = "en")
     FILTER(LANG(?sourceLabel)  = "en")
   }
   ORDER BY ?derivedLabel

**Find what base measurements are needed to compute net energy:**

.. code-block:: sparql

   PREFIX bdf:  <https://w3id.org/battery-data-alliance/ontology/battery-data-format#>
   PREFIX prov: <http://www.w3.org/ns/prov#>
   PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

   SELECT DISTINCT ?baseLabel
   WHERE {
     # Walk the prov:wasDerivedFrom graph transitively
     bdf:net_energy_wh (prov:wasDerivedFrom)+ ?base .
     ?base skos:prefLabel ?baseLabel .
     # Keep only quantities with no further derivation (base measurements)
     FILTER NOT EXISTS { ?base prov:wasDerivedFrom ?_ }
     FILTER(LANG(?baseLabel) = "en")
   }

Running Queries with Python
----------------------------

.. code-block:: python

   from rdflib import Graph, Namespace
   from rdflib.namespace import OWL, SKOS

   BDF    = Namespace("https://w3id.org/battery-data-alliance/ontology/battery-data-format#")
   SCHEMA = Namespace("https://schema.org/")

   g = Graph()
   g.parse("battery-data-format.ttl", format="turtle")

   # List all BDF classes with their UCUM unit codes
   for cls in g.subjects(None, OWL.Class):
       if not str(cls).startswith(str(BDF)):
           continue
       label = g.value(cls, SKOS.prefLabel)
       ucum  = g.value(cls, SCHEMA.unitCode)
       if label:
           print(f"{str(label):<35}  {str(ucum) if ucum else '—'}")

Vendor Normalisation
---------------------

The following example shows how a Novonix UHPC CSV file is normalised to BDF canonical columns using the BDF Python package. The vendor schema provides the header mappings; the ``schema:unitCode`` annotation drives the unit conversion from hours to seconds.

.. code-block:: python

   from battery_data_format import read_file

   # The normaliser detects the Novonix format automatically,
   # loads the novonix_csv vendor schema, maps headers, and
   # converts time from hours to seconds (schema:unitCode "h" → × 3600).
   df = read_file("novonix_experiment.csv")

   print(df.columns.tolist())
   # ['test_time_second', 'step_time_second', 'voltage_volt',
   #  'current_ampere', 'cycle_count', 'step_id', ...]

   print(df["test_time_second"].dtype)
   # float64  (values in seconds)
