Vendor Schemas
==============

BDF supports data from commercial battery cyclers through **vendor schemas** — machine-readable CSVW documents that map each instrument's native column headers to BDF canonical column names.

Vendor schemas live under ``schema/vendors/`` in the repository and are resolvable as linked data at IRIs of the form:

.. code-block:: text

   https://w3id.org/battery-data-alliance/ontology/battery-data-format/schema/vendors/{name}

Supported Instruments
---------------------

.. list-table::
   :widths: 22 22 12 44
   :header-rows: 1

   * - Schema ID
     - Manufacturer
     - Columns
     - Notes
   * - ``arbin_csv``
     - Arbin Instruments
     - 14
     - CSV exports from MITS Pro / DataPro. Supports both space-separated and underscore-separated header dialects.
   * - ``arbin_xlsx``
     - Arbin Instruments
     - 16
     - Multi-sheet XLSX workbooks (Global_Info / Channel_* / ACIM / statistics sheets); maps the Channel_* time-series columns. The Charge/Discharge Capacity and Energy accumulators map to the schedule-scoped BDF terms (their reset windows are schedule-authored). Full per-column and per-sheet semantics are in the Arbin ontology module (``vendors/arbin``).
   * - ``basytec_txt``
     - Basytec GmbH
     - 4
     - Headers prefixed with ``~`` (stripped during parsing). Time, current, and voltage may each appear in multiple units depending on the instrument configuration; the normaliser selects the appropriate conversion per file.
   * - ``biologic_mpt``
     - Bio-Logic Science Instruments
     - 15
     - EC-Lab / BT-Lab MPT ASCII export. Current is in milliamperes; capacities in mA·h. File encoding is typically latin-1; decimal separator may be a comma.
   * - ``digatron_csv``
     - Digatron Power Electronics
     - 20
     - Broadest BDF column coverage of any vendor schema, including EIS quantities. The accumulated charge/energy columns (AhAccu, AhBal, AhStep) do not align 1:1 with the BDF cumulative/net/step definitions; the divergences are documented per-column in the schema. Note also that the ``#s`` duration columns are emitted in milliseconds despite the ``s`` label.
   * - ``landt_ccs``
     - LANDT Instruments
     - 9
     - CCS (Cloud Cycler System) export format. All values in SI units; no unit conversion required.
   * - ``landt_csv``
     - LANDT Instruments
     - 8
     - Modern CSV export with snake_case headers and SI units embedded in the column name (e.g. ``voltage_v``, ``current_a``).
   * - ``landt_txt``
     - LANDT Instruments
     - 7
     - Older TXT export with abbreviated English headers (``Volts``, ``Amps``, ``Test(sec)``). Tab-delimited, SI units throughout.
   * - ``neware_csv``
     - Neware Technology
     - 13
     - Supports both English and Simplified Chinese (GB18030) header variants. Capacity exported in mAh, energy in mWh; both divided by 1000 during normalisation.
   * - ``neware_nda``
     - Neware Technology
     - 10
     - Binary NDA/NDAX format, parsed via the ``NewareNDA`` or ``fastnda`` library. Column names are the DataFrame column names produced by the parser, not the binary file headers. Current in mA; capacity/energy in mAh/mWh.
   * - ``novonix_csv``
     - Novonix
     - 13
     - UHPC CSV export with an INI-style ``[Summary]``/``[Data]`` preamble. Time columns are in **hours** (``schema:unitCode "h"``); the normaliser multiplies by 3600.

How Vendor Schemas Work
-----------------------

Each vendor schema is a JSON-LD document typed as ``csvw:TableSchema``. It contains a ``csvw:columns`` array where each entry maps one or more vendor header names to a BDF canonical column:

.. code-block:: json

   {
     "@context": "https://w3id.org/battery-data-alliance/ontology/battery-data-format/context",
     "@id": "https://w3id.org/battery-data-alliance/ontology/battery-data-format/schema/vendors/novonix_csv",
     "@type": "csvw:TableSchema",
     "dcterms:title": "Novonix UHPC CSV — BDF column mapping",
     "schema:producer": { "@type": "schema:Organization", "schema:name": "Novonix" },
     "dcterms:conformsTo": {
       "@id": "https://w3id.org/battery-data-alliance/ontology/battery-data-format/1.0.0/schema"
     },
     "csvw:columns": [
       {
         "csvw:name": "test_time_second",
         "csvw:titles": ["Run Time (h)", "Run-Time (h)", "Runtime (h)"],
         "schema:unitCode": "h"
       }
     ]
   }

The key fields are:

``csvw:name``
  The BDF canonical column name. This links the vendor column to the full BDF schema entry, which carries ``csvw:propertyUrl``, datatype, unit annotations, and required flags.

``csvw:titles``
  An array of header strings that this vendor instrument may produce for this column. The BDF normaliser matches any of these against the actual file header.

``schema:unitCode``
  Present only when the vendor exports the column in a non-SI unit. The value is a UCUM code indicating the as-exported unit. The normaliser applies the appropriate conversion factor. If ``schema:unitCode`` is absent, the values are already in BDF canonical SI units.

``skos:note``
  Present when there is a semantic subtlety — for example, where a vendor's column does not map cleanly to the BDF canonical definition (accumulated vs. step-level capacity, column that doubles as step time vs. test time, etc.).

Unit Conversion Summary
-----------------------

.. list-table::
   :widths: 20 20 20 40
   :header-rows: 1

   * - Vendor
     - Column
     - Source unit
     - Conversion
   * - Bio-Logic MPT
     - ``current_ampere``
     - mA
     - ÷ 1000
   * - Bio-Logic MPT
     - ``*_capacity_ah``
     - mA·h
     - ÷ 1000
   * - Neware CSV / NDA
     - ``*_capacity_ah``
     - mAh
     - ÷ 1000
   * - Neware CSV / NDA
     - ``*_energy_wh``
     - mWh
     - ÷ 1000
   * - Neware NDA
     - ``current_ampere``
     - mA
     - ÷ 1000
   * - Novonix CSV
     - ``test_time_second``, ``step_time_second``
     - h
     - × 3600
   * - Basytec TXT
     - ``test_time_second``
     - s / min / h (per file)
     - × 1 / × 60 / × 3600

Adding a New Vendor Schema
--------------------------

To add support for a new instrument:

1. Create ``schema/vendors/{manufacturer}_{format}.json`` following the structure above.
2. List only the columns that the instrument actually exports; omit columns with no known equivalent.
3. Set ``schema:unitCode`` where the instrument exports in non-SI units.
4. Add a ``skos:note`` for any column where the semantic mapping is non-obvious.
5. Open a pull request against the `BDAOntology repository <https://github.com/BatteryDataAlliance/BDAOntology>`_.

The CI pipeline will validate JSON syntax and check that all ``csvw:name`` values reference canonical BDF columns.
