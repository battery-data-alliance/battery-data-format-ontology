Battery Data Format Specification
=================================

.. note::
   This page is generated from the ontology file ``battery-data-format.ttl``.

Status
------
- Title: Battery Data Format Ontology
- Version: 1.0.0
- Issued: 2026-01-21
- Modified: 2026-01-21
- Publisher: Battery Data Alliance
- License: http://www.apache.org/licenses/LICENSE-2.0

Scope
-----
An application ontology for the Battery Data Format (BDF) from the Battery Data Alliance (BDA)

Normative References
--------------------
- https://w3id.org/emmo/domain/battery/0.18.6/battery

Identifiers
-----------
Base IRI: https://w3id.org/battery-data-alliance/ontology/battery-data-format#
Full term IRIs are formed by concatenating the base IRI with the notation.

Terms and Definitions
---------------------

.. list-table::
   :widths: 20 15 45 20
   :header-rows: 1

   * - Term
     - Notation
     - Definition
     - Unit
   * - Ambient Pressure / Pa
     - ambient_pressure_pa
     - Ambient air pressure recorded during testing, in Pascal.
     - Pascal
   * - Ambient Temperature / degC
     - ambient_temperature_celsius
     - Ambient temperature recorded during testing, in degree Celsius.
     - DegreeCelsius
   * - Applied Pressure / Pa
     - applied_pressure_pa
     - External pressure applied to the test object, in Pascal.
     - Pascal
   * - Charging Capacity / Ah
     - charging_capacity_ah
     - Electric charge transferred into the test object during charging, in ampere hour.
     - AmpereHour
   * - Charging Energy / Wh
     - charging_energy_wh
     - Energy transferred into the test object during charging, in watt hour.
     - WattHour
   * - Cumulative Capacity / Ah
     - cumulative_capacity_ah
     - Total electric charge that has passed through the test object since the start of the test, in ampere hour.
     - AmpereHour
   * - Cumulative Energy / Wh
     - cumulative_energy_wh
     - Total energy transferred through the test object since the start of the test, in watt hour.
     - WattHour
   * - Current / A
     - current_ampere
     - Instantaneous current recorded in ampere.
     - Ampere
   * - Cycle Count / 1
     - cycle_count
     - The cycle number here is used to segregate data into smaller quasi-periodic subsets, and is typically used to track evolution of performance metrics over the course of aging.
     - EMMO_5ebd5e01_0ed3_49a2_a30d_cd05cbe72978
   * - Discharging Capacity / Ah
     - discharging_capacity_ah
     - Electric charge transferred out of the test object during discharging, in ampere hour.
     - AmpereHour
   * - Discharging Energy / Wh
     - discharging_energy_wh
     - Energy transferred out of the test object during discharging, in watt hour.
     - WattHour
   * - Internal Resistance / Ohm
     - internal_resistance_ohm
     - Direct current internal resistance recorded in ohm.
     - Ohm
   * - Net Capacity / Ah
     - net_capacity_ah
     - Net capacity difference between charge and discharge within a defined step or cycle, in ampere hour.
     - AmpereHour
   * - Net Energy / Wh
     - net_energy_wh
     - Net energy difference between charge and discharge within a defined step or cycle, in watt hour.
     - WattHour
   * - Power / W
     - power_watt
     - Instantaneous power calculated as the product of voltage and current, in watt.
     - Watt
   * - Step Capacity / Ah
     - step_capacity_ah
     - Electric charge transferred during the current test step, in ampere hour.
     - AmpereHour
   * - Step Count / 1
     - step_count
     - Step number, with unit one.
     - EMMO_5ebd5e01_0ed3_49a2_a30d_cd05cbe72978
   * - Step Energy / Wh
     - step_energy_wh
     - Energy transferred during the current test step, in watt hour.
     - WattHour
   * - Step Index / 1
     - step_index
     - Index indicating the position of the data point within a step, with unit one.
     - One
   * - Surface Pressure / Pa
     - surface_pressure_pa
     - Surface pressure recorded in Pascal.
     - Pascal
   * - Surface Temperature / degC
     - surface_temperature_celsius
     - Surface temperature recorded in degree Celsius.
     - DegreeCelsius
   * - Surface Temperature T1 / degC
     - temperature_t1_celsius
     - For tests with multiple temperature measurements, the measured temperature of the test object (e.g., surface or internal), in degrees Celsius.
     - DegreeCelsius
   * - Surface Temperature T2 / degC
     - temperature_t2_celsius
     - For tests with multiple temperature measurements, the measured temperature of the test object (e.g., surface or internal), in degrees Celsius.
     - DegreeCelsius
   * - Surface Temperature T3 / degC
     - temperature_t3_celsius
     - For tests with multiple temperature measurements, the measured temperature of the test object (e.g., surface or internal), in degrees Celsius.
     - DegreeCelsius
   * - Surface Temperature T4 / degC
     - temperature_t4_celsius
     - For tests with multiple temperature measurements, the measured temperature of the test object (e.g., surface or internal), in degrees Celsius.
     - DegreeCelsius
   * - Surface Temperature T5 / degC
     - temperature_t5_celsius
     - For tests with multiple temperature measurements, the measured temperature of the test object (e.g., surface or internal), in degrees Celsius.
     - DegreeCelsius
   * - Test Time / ms
     - test_time_millisecond
     - Test time recorded in millisecond.
     - MilliSecond
   * - Test Time / s
     - test_time_second
     - Test time recorded in second.
     - Second
   * - Unix Time / ms
     - unix_time_millisecond
     - Unix time recorded in millisecond.
     - MilliSecond
   * - Unix Time / s
     - unix_time_second
     - Unix time recorded in second.
     - Second
   * - Voltage / V
     - voltage_volt
     - Instantaneous voltage recorded in volt.
     - Volt

See :doc:`BDF Ontology Terms </battery-data-format>` for full term metadata.

