"""
One-shot script: adds bdf:latexSymbol and bdf:latexFormula annotations to
battery-data-format.ttl via text manipulation (preserves existing formatting).

Run from the BDAOntology root:
    python scripts/add_latex_annotations.py
"""
from __future__ import annotations
import pathlib, re, sys

TTL = pathlib.Path("battery-data-format.ttl")

# ---------------------------------------------------------------------------
# Symbol and formula data
# (Python strings — backslashes are single here; the script doubles them
#  when writing Turtle literals so that rdflib reads back the correct LaTeX.)
# ---------------------------------------------------------------------------

SYMBOLS: dict[str, str] = {
    # Base measured quantities
    "test_time_second":               "t",
    "voltage_volt":                   "V",
    "current_ampere":                 "I",
    "step_time_second":               r"\Delta t_\mathrm{step}",
    "frequency_hertz":                "f",
    "cycle_count":                    "n",
    # Electrical derived
    "power_watt":                     "P",
    "charging_capacity_ah":           r"Q_\mathrm{chg}",
    "discharging_capacity_ah":        r"Q_\mathrm{dchg}",
    "cumulative_capacity_ah":         r"Q_\mathrm{cum}",
    "net_capacity_ah":                r"Q_\mathrm{net}",
    "step_charging_capacity_ah":      r"Q_\mathrm{chg}^\mathrm{step}",
    "step_discharging_capacity_ah":   r"Q_\mathrm{dchg}^\mathrm{step}",
    "step_cumulative_capacity_ah":    r"Q_\mathrm{cum}^\mathrm{step}",
    "step_net_capacity_ah":           r"Q_\mathrm{net}^\mathrm{step}",
    "charging_energy_wh":             r"E_\mathrm{chg}",
    "discharging_energy_wh":          r"E_\mathrm{dchg}",
    "cumulative_energy_wh":           r"E_\mathrm{cum}",
    "net_energy_wh":                  r"E_\mathrm{net}",
    "step_charging_energy_wh":        r"E_\mathrm{chg}^\mathrm{step}",
    "step_discharging_energy_wh":     r"E_\mathrm{dchg}^\mathrm{step}",
    "step_cumulative_energy_wh":      r"E_\mathrm{cum}^\mathrm{step}",
    "step_net_energy_wh":             r"E_\mathrm{net}^\mathrm{step}",
    "internal_resistance_ohm":        r"R_0",
    # EIS
    "real_impedance_ohm":             r"Z'",
    "imaginary_impedance_ohm":        r"Z''",
    "absolute_impedance_ohm":         r"|Z|",
    "phase_degree":                   r"\phi",
    # Temperature / pressure
    "ambient_temperature_celsius":    r"T_\mathrm{amb}",
    "surface_temperature_celsius":    r"T_\mathrm{surf}",
    "temperature_t1_celsius":         r"T_1",
    "temperature_t2_celsius":         r"T_2",
    "temperature_t3_celsius":         r"T_3",
    "temperature_t4_celsius":         r"T_4",
    "temperature_t5_celsius":         r"T_5",
    "ambient_pressure_pa":            r"p_\mathrm{amb}",
    "applied_pressure_pa":            r"p_\mathrm{app}",
    "surface_pressure_pa":            r"p_\mathrm{surf}",
}

# t_s denotes the start time of the current step (defined in the formula footnote)
FORMULAS: dict[str, str] = {
    "power_watt": (
        r"P(t) = V(t)\,I(t)"
    ),
    "charging_capacity_ah": (
        r"Q_\mathrm{chg}(t) = \frac{1}{3600}"
        r"\int_0^t \max\!\bigl(I(\tau),\,0\bigr)\,\mathrm{d}\tau"
    ),
    "discharging_capacity_ah": (
        r"Q_\mathrm{dchg}(t) = \frac{1}{3600}"
        r"\int_0^t \max\!\bigl(-I(\tau),\,0\bigr)\,\mathrm{d}\tau"
    ),
    "cumulative_capacity_ah": (
        r"Q_\mathrm{cum}(t) = Q_\mathrm{chg}(t) + Q_\mathrm{dchg}(t)"
        r" = \frac{1}{3600}\int_0^t \bigl|I(\tau)\bigr|\,\mathrm{d}\tau"
    ),
    "net_capacity_ah": (
        r"Q_\mathrm{net}(t) = Q_\mathrm{chg}(t) - Q_\mathrm{dchg}(t)"
        r" = \frac{1}{3600}\int_0^t I(\tau)\,\mathrm{d}\tau"
    ),
    "step_charging_capacity_ah": (
        r"Q_\mathrm{chg}^\mathrm{step}(t) = \frac{1}{3600}"
        r"\int_{t_s}^{t} \max\!\bigl(I(\tau),\,0\bigr)\,\mathrm{d}\tau"
    ),
    "step_discharging_capacity_ah": (
        r"Q_\mathrm{dchg}^\mathrm{step}(t) = \frac{1}{3600}"
        r"\int_{t_s}^{t} \max\!\bigl(-I(\tau),\,0\bigr)\,\mathrm{d}\tau"
    ),
    "step_cumulative_capacity_ah": (
        r"Q_\mathrm{cum}^\mathrm{step}(t) = Q_\mathrm{chg}^\mathrm{step}(t) + Q_\mathrm{dchg}^\mathrm{step}(t)"
        r" = \frac{1}{3600}\int_{t_s}^{t} \bigl|I(\tau)\bigr|\,\mathrm{d}\tau"
    ),
    "step_net_capacity_ah": (
        r"Q_\mathrm{net}^\mathrm{step}(t) = Q_\mathrm{chg}^\mathrm{step}(t) - Q_\mathrm{dchg}^\mathrm{step}(t)"
        r" = \frac{1}{3600}\int_{t_s}^{t} I(\tau)\,\mathrm{d}\tau"
    ),
    "charging_energy_wh": (
        r"E_\mathrm{chg}(t) = \frac{1}{3600}"
        r"\int_0^t \max\!\bigl(P(\tau),\,0\bigr)\,\mathrm{d}\tau"
    ),
    "discharging_energy_wh": (
        r"E_\mathrm{dchg}(t) = \frac{1}{3600}"
        r"\int_0^t \max\!\bigl(-P(\tau),\,0\bigr)\,\mathrm{d}\tau"
    ),
    "cumulative_energy_wh": (
        r"E_\mathrm{cum}(t) = E_\mathrm{chg}(t) + E_\mathrm{dchg}(t)"
        r" = \frac{1}{3600}\int_0^t \bigl|P(\tau)\bigr|\,\mathrm{d}\tau"
    ),
    "net_energy_wh": (
        r"E_\mathrm{net}(t) = E_\mathrm{chg}(t) - E_\mathrm{dchg}(t)"
        r" = \frac{1}{3600}\int_0^t P(\tau)\,\mathrm{d}\tau"
    ),
    "step_charging_energy_wh": (
        r"E_\mathrm{chg}^\mathrm{step}(t) = \frac{1}{3600}"
        r"\int_{t_s}^{t} \max\!\bigl(P(\tau),\,0\bigr)\,\mathrm{d}\tau"
    ),
    "step_discharging_energy_wh": (
        r"E_\mathrm{dchg}^\mathrm{step}(t) = \frac{1}{3600}"
        r"\int_{t_s}^{t} \max\!\bigl(-P(\tau),\,0\bigr)\,\mathrm{d}\tau"
    ),
    "step_cumulative_energy_wh": (
        r"E_\mathrm{cum}^\mathrm{step}(t) = E_\mathrm{chg}^\mathrm{step}(t) + E_\mathrm{dchg}^\mathrm{step}(t)"
        r" = \frac{1}{3600}\int_{t_s}^{t} \bigl|P(\tau)\bigr|\,\mathrm{d}\tau"
    ),
    "step_net_energy_wh": (
        r"E_\mathrm{net}^\mathrm{step}(t) = E_\mathrm{chg}^\mathrm{step}(t) - E_\mathrm{dchg}^\mathrm{step}(t)"
        r" = \frac{1}{3600}\int_{t_s}^{t} P(\tau)\,\mathrm{d}\tau"
    ),
    "absolute_impedance_ohm": (
        r"|Z| = \sqrt{Z_\mathrm{re}^2 + Z_\mathrm{im}^2}"
    ),
    "phase_degree": (
        r"\phi = \arctan\!\left(\frac{Z_\mathrm{im}}{Z_\mathrm{re}}\right)"
        r" \cdot \frac{180}{\pi}"
    ),
}

PROPERTY_DECLARATIONS = """\

###  https://w3id.org/battery-data-alliance/ontology/battery-data-format#latexFormula
:latexFormula rdf:type owl:AnnotationProperty ;
              rdfs:label "LaTeX formula"@en ;
              rdfs:comment "Mathematical definition of a derived quantity in LaTeX notation. Backslashes are single (standard LaTeX)."@en ;
              rdfs:range xsd:string .


###  https://w3id.org/battery-data-alliance/ontology/battery-data-format#latexSymbol
:latexSymbol rdf:type owl:AnnotationProperty ;
             rdfs:label "LaTeX symbol"@en ;
             rdfs:comment "LaTeX notation for the variable name used to represent this quantity in mathematical expressions."@en ;
             rdfs:range xsd:string .

"""


def _turtle_escape(s: str) -> str:
    """Escape a Python string for use as a Turtle string literal."""
    return s.replace("\\", "\\\\")


def main() -> None:
    if not TTL.exists():
        sys.exit(f"Cannot find {TTL}. Run from the BDAOntology root directory.")

    text = TTL.read_text(encoding="utf-8")

    # ------------------------------------------------------------------
    # 1. Add property declarations after the last existing annotation
    #    property block (just before the Classes section comment)
    # ------------------------------------------------------------------
    classes_marker = "#################################################################\n#    Classes"
    if ":latexSymbol rdf:type owl:AnnotationProperty" not in text:
        if classes_marker not in text:
            sys.exit("Cannot find Classes section marker in TTL.")
        text = text.replace(classes_marker, PROPERTY_DECLARATIONS + classes_marker)
        print("  + Added property declarations")
    else:
        print("  ~ Property declarations already present, skipping")

    # ------------------------------------------------------------------
    # 2. For each class, insert latexSymbol (and latexFormula if derived)
    #    immediately after the skos:notation triple.
    # ------------------------------------------------------------------
    # Pattern: leading whitespace + skos:notation + quoted value (optional @lang)
    notation_re = re.compile(
        r'^( +)skos:notation\s+"([^"]+)"',
        re.MULTILINE,
    )

    lines = text.splitlines(keepends=True)
    out_lines: list[str] = []
    changed = 0

    for line in lines:
        out_lines.append(line)
        m = notation_re.match(line)
        if not m:
            continue
        indent = m.group(1)
        notation = m.group(2)

        # Skip if already annotated (idempotent)
        # We check the next few lines for presence of :latexSymbol
        idx = len(out_lines) - 1
        already = False
        for look in range(1, 6):
            if idx + look < len(lines) and ":latexSymbol" in lines[idx + look]:
                already = True
                break
        if already:
            continue

        symbol = SYMBOLS.get(notation)
        formula = FORMULAS.get(notation)

        if symbol:
            ts = _turtle_escape(symbol)
            out_lines.append(f'{indent}:latexSymbol "{ts}"^^xsd:string ;\n')
            changed += 1
        if formula:
            tf = _turtle_escape(formula)
            out_lines.append(f'{indent}:latexFormula "{tf}"^^xsd:string ;\n')
            changed += 1

    if changed:
        TTL.write_text("".join(out_lines), encoding="utf-8")
        print(f"  + Added {changed} annotation triples to {TTL}")
    else:
        print("  ~ No new annotations needed")


if __name__ == "__main__":
    main()
