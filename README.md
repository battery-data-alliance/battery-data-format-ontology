# Battery Data Format (BDF) Ontology

The BDF Ontology is an application ontology designed to help machines work with BDF-compliant data.  

## Documentation

Build the docs locally:

```
python -m pip install -r requirements-docs.txt
BDF_ONLY_LOCAL_IMPORTS=1 python .github/scripts/ontology_toolkit.py --generate-rst
python -m sphinx -c docs -b html -d docs/_build/doctrees docs docs/_build/html
```

The HTML output is available at `docs/_build/html/index.html`.

## Reference IRIs

The table below contains a quick cheat sheet of IRIs for accessing different files from the ontology
The import structure is summarized in the following table:

| IRI                                                                                  | Description                   |
| ------------------------------------------------------------------------------------ | ----------------------------- |
| `https://w3id.org/battery-data-alliance/ontology/battery-data-format`                | Base Asserted Ontology*       |
| `https://w3id.org/battery-data-alliance/ontology/battery-data-format/inferred`       | Base Pre-Inferred Ontology*   |
| `https://w3id.org/battery-data-alliance/ontology/battery-data-format/latest`         | Latest Asserted Ontology*     |
| `https://w3id.org/battery-data-alliance/ontology/battery-data-format/source`         | Source of Asserted Ontology*  |
| `https://w3id.org/battery-data-alliance/ontology/battery-data-format/context`        | Latest JSON-LD Context File   |
| `https://w3id.org/battery-data-alliance/ontology/battery-data-format/schema`         | Latest CSVW Table Schema File |
| `https://w3id.org/battery-data-alliance/ontology/battery-data-format/{VERSION}`      | Version of Asserted Ontology* |
| `https://w3id.org/battery-data-alliance/ontology/battery-data-format/{VERSION}/...`  | ... follows same logic above  |

*IRI directs to human readable documentation if called from the web browser and to the source .ttl file if called from an application.

## Contributing

See `./.github/CONTRIBUTING.md`. Please follow the code of conduct in `./CODE_OF_CONDUCT.md`.

## License

Apache-2.0. See `./LICENSE`.
