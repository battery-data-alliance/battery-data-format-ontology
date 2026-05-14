# Documentation

This directory contains the Sphinx source for the BDF Ontology documentation site.

## Building locally

Install the docs dependencies from the project root:

```bash
pip install ".[docs]"
```

Generate the RST term reference from the ontology (requires the `ontopy` optional group):

```bash
ONLY_LOCAL_IMPORTS=1 python .github/scripts/ontology_toolkit.py --generate-rst
```

Build the HTML site:

```bash
sphinx-build -b html -W --keep-going docs/ docs/_build/html/
```

Open `docs/_build/html/index.html` in a browser to review the output.

The specification page (`pages/specification.rst`) is regenerated automatically from
`battery-data-format.ttl` at the start of every Sphinx build via the `builder-inited` hook
in `conf.py`. You do not need to regenerate it manually.

## Deployment

Documentation is built and deployed to GitHub Pages automatically by the
`.github/workflows/docs-build-and-deploy.yml` CI workflow on every push to `main`
and for each tagged release. The live site is at:

<https://battery-data-alliance.github.io/BDAOntology/>

## Directory structure

```
docs/
├── conf.py                        # Sphinx configuration
├── index.rst                      # Landing page
├── battery-data-format.rst        # Auto-generated term reference (ontopy)
├── pages/
│   ├── about.rst                  # Project background and vocabulary alignments
│   ├── concepts.rst               # Architecture: CSVW → SOSA → EMMO pattern
│   ├── examples.rst               # Worked examples and SPARQL queries
│   ├── faq.rst                    # Frequently asked questions
│   ├── quick_start.rst            # Dataset metadata quick start
│   ├── specification.rst          # Auto-generated from TTL (do not edit)
│   └── vendor_schemas.rst         # Supported instruments reference
├── scripts/
│   └── generate_specification.py  # Generates specification.rst from TTL
├── assets/
│   └── img/logo/                  # BDA logo files
└── _static/
    └── css/custom.css             # Theme overrides
```
