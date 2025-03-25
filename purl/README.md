# battery-data-alliance

Persistent Uniform Resource Locators (PURLs) for ontologies and semantic resources developed by the [Battery Data Alliance](https://lfenergy.org/projects/battery-data-alliance/), a Linux Foundation Energy project.

This `.htaccess` file currently defines redirects for the **Battery Data Format** ontology under:

```
https://w3id.org/battery-data-alliance/ontology/battery-data-format
```

Other resources (e.g., test method ontologies, equipment vocabularies, data model schemas) are expected to be added under the broader `battery-data-alliance` namespace in the future.

---

## Purpose

This PURL namespace provides stable, long-term IRIs for:

- Asserted ontology files
- Inferred variants
- JSON-LD context documents
- CSVW table schemas
- Human-readable documentation
- Versioned variants and GitHub source references

It ensures compliance with FAIR and linked data principles, enabling machine-readable and human-readable resolution of resources.

---

## Redirect Logic

### Non-Versioned (Main Branch)

| IRI                                                                                   | Description                           |
| ------------------------------------------------------------------------------------- | ------------------------------------- |
| `/ontology/battery-data-format`                                                      | Asserted ontology (HTML/TTL redirect) |
| `/ontology/battery-data-format/inferred`                                             | Pre-inferred ontology (TTL)           |
| `/ontology/battery-data-format/latest`                                               | Latest asserted version (raw TTL)     |
| `/ontology/battery-data-format/source`                                               | Editable GitHub source (view on GitHub) |
| `/ontology/battery-data-format/context`                                              | JSON-LD context                       |
| `/ontology/battery-data-format/schema`                                               | CSVW schema                           |

### Versioned (Semantic Versioning: `MAJOR.MINOR.PATCH`)

Resources follow this pattern:

```
/ontology/battery-data-format/{VERSION}/battery-data-format
                                           ├── /latest
                                           ├── /inferred
                                           ├── /source
                                           ├── /context
                                           └── /schema
```

| Example IRI                                                                                          | Description                                  |
| ---------------------------------------------------------------------------------------------------- | -------------------------------------------- |
| `/ontology/battery-data-format/0.1.0/battery-data-format`                                           | Ontology HTML or TTL depending on Accept     |
| `/ontology/battery-data-format/0.1.0/battery-data-format/latest`                                    | Latest asserted TTL (raw)                    |
| `/ontology/battery-data-format/0.1.0/battery-data-format/inferred`                                  | Inferred TTL                                 |
| `/ontology/battery-data-format/0.1.0/battery-data-format/source`                                    | GitHub source                                |
| `/ontology/battery-data-format/0.1.0/battery-data-format/context`                                   | JSON-LD context                              |
| `/ontology/battery-data-format/0.1.0/battery-data-format/schema`                                    | CSVW schema                                  |

---

## Repository Structure (GitHub)

This redirect scheme assumes the following layout in your GitHub repository:

```
BDAOntology/
├── battery-data-format.ttl
├── battery-data-format.html
├── context/
│   └── context.json
├── schema/
│   └── schema.json
└── versions/
    └── 0.1.0/
        ├── battery-data-format.ttl
        ├── battery-data-format.html
        ├── battery-data-format-inferred.ttl
        ├── context/
        │   └── context.jsonld
        └── schema/
            └── schema.json
```

---

## GitHub Repositories

All redirects currently point to this repository:

- Ontology files: https://github.com/battery-data-alliance/BDAOntology
- GitHub Pages: https://battery-data-alliance.github.io/BDAOntology/

As additional ontologies are developed, new entries may be added under this namespace or in new repositories under the `battery-data-alliance` GitHub organization.

---

## Contacts

This PURL space is maintained by the [Battery Data Alliance](https://lfenergy.org/projects/battery-data-alliance/).

Current maintainers:

- [Gabe Hege](https://github.com/pghege) – LF Energy  
- [Simon Clark](https://github.com/jsimonclark) – SINTEF

To request changes, open an issue or pull request on the [BDAOntology repository](https://github.com/battery-data-alliance/BDAOntology).
