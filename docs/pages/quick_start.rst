Quick Start
===========

The Battery Data Format (BDF) recommends standardized column names for time-series battery data, making it easier for developers to build digital tools. But BDF goes further: to unlock its full potential for AI-ready, machine-readable data, users are encouraged to include metadata alongside their BDF files.

The example below shows how a JSON-LD metadata file can:

- Specify the license under which the data is shared  
- Credit the data creators  
- Include bibliographic information  
- Most importantly, link to:  
    - The URL where the data is accessible  
    - The BDF table schema, which connects the data to the ontology and the semantic web  


.. code-block:: json

    {
        "@context": "https://w3id.org/battery-data-alliance/ontology/battery-data-format/context",
        "@type": "dcat:Dataset",
        "dc:title": "Rate-Test Cycling of Lithium-Polymer Cells for Road Racing",
        "dc:description": "Results from rate-test cycling of Melasta lithium-polymer cells used in electric road racing vehicles.",
        "dcat:distribution": {
            "@type": "dcat:Distribution",
            "dcat:mediaType": "application/vnd.apache.parquet",
            "dcat:downloadURL": "REPLACE_WITH_YOUR_DATA_FILE_URL",
            "csvw:tableSchema": {
                "@id": "https://w3id.org/battery-data-alliance/ontology/battery-data-format/schema",
                "@type": "csvw:TableSchema"
            }
        },
        "dc:creator": [
            {
                "@type": "schema:Person",
                "@id": "https://orcid.org/0000-0003-0934-4515",
                "schema:name": "Julian Tolchard",
                "schema:email": "mailto:JulianRichard.Tolchard@sintef.no"
            },
            {
                "@type": "schema:Person",
                "@id": "https://orcid.org/0009-0005-4059-7715",
                "schema:name": "Julie Cathrine Guldahl",
                "schema:email": "mailto:julie.guldahl@sintef.no"
            }
        ],
        "dc:contributor": {
            "@type": "schema:Person",
            "@id": "https://orcid.org/0000-0002-8758-6109",
            "schema:name": "Simon Clark",
            "schema:email": "mailto:simon.clark@sintef.no"
        },
        "dc:license": "https://creativecommons.org/licenses/by/4.0/",
        "dc:issued": "2025-03-24",
        "dc:modified": "2025-03-24",
        "dcat:keyword": [
            "lithium-polymer battery",
            "battery cycling",
            "battery rate testing",
            "lithium cobalt oxide",
            "graphite"
        ]
    }



Here is a template that you can complete and share with your BDF dataset to make it fully compliant with the best practices for sharing data. 

.. code-block:: json

    {
        "@context": "https://w3id.org/battery-data-alliance/ontology/battery-data-format/context",
        "@type": "dcat:Dataset",

        "dc:title": "REPLACE_WITH_YOUR_DATASET_TITLE",
        "dc:description": "REPLACE_WITH_A_SHORT_DESCRIPTION_OF_YOUR_DATA",
        
        "dc:creator": {
            "@type": "schema:Person",
            "schema:name": "REPLACE_WITH_YOUR_NAME",
            "schema:email": "mailto:REPLACE_WITH_YOUR_EMAIL"
        },

        "dc:license": "REPLACE_WITH_LICENSE_URL (e.g. https://creativecommons.org/licenses/by/4.0/)",

        "dc:issued": "REPLACE_WITH_PUBLICATION_DATE (e.g. 2025-03-21)",
        "dc:modified": "REPLACE_WITH_LAST_MODIFIED_DATE (e.g. 2025-03-21)",

        "dcat:keyword": [
            "REPLACE_WITH_KEYWORDS", 
            "REPLACE_WITH_KEYWORDS", 
            "REPLACE_WITH_KEYWORDS",
            "REPLACE_WITH_KEYWORDS", 
            "REPLACE_WITH_KEYWORDS"
        ],

        "dcat:distribution": {
            "@type": "dcat:Distribution",
            "dcat:mediaType": "REPLACE_WITH_YOUR_DATA_MEDIA_TYPE (e.g. text/csv or application/vnd.apache.parquet or application/json)",
            "dcat:downloadURL": "REPLACE_WITH_YOUR_DATA_FILE_URL (e.g. https://example.com/data.csv)",

            "csvw:dialect": {
                "@type": "csvw:Dialect",
                "csvw:skipRows": "REPLACE_WITH_INTEGER_NUMBER_OF_ROWS_TO_SKIP",
                "csvw:delimiter": "\\t"
            },

            "csvw:tableSchema": {
                "@id": "https://w3id.org/battery-data-alliance/ontology/battery-data-format/schema",
                "@type": "csvw:TableSchema"
            }
        }
    }
