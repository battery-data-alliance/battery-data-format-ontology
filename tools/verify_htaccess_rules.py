import re

# ---------------------------------------------------------------------------
# Minimal mod_rewrite simulator
# ---------------------------------------------------------------------------

RULES = [
    # Non-versioned — specific patterns first to avoid catch-all swallowing them
    ("R1",  [],
             r"^ontology/([^/]+)-inferred/?$",
             "https://battery-data-alliance.github.io/$1-ontology/$1-inferred.ttl"),
    # Main ontology IRI — content-negotiated
    ("R2",  [("text/html", True), (r"application/xhtml\+xml", False)],
             r"^ontology/([^/]+)/?$",
             "https://battery-data-alliance.github.io/$1-ontology/$1.html"),
    ("R3",  [(r"application/ld\+json", False)],
             r"^ontology/([^/]+)/?$",
             "https://battery-data-alliance.github.io/$1-ontology/context/context.json"),
    ("R4",  [],
             r"^ontology/([^/]+)/?$",
             "https://battery-data-alliance.github.io/$1-ontology/$1.ttl"),
    ("R5",  [],
             r"^ontology/([^/]+)/inferred/?$",
             "https://battery-data-alliance.github.io/$1-ontology/$1-inferred.ttl"),
    ("R6",  [],
             r"^ontology/([^/]+)/latest/?$",
             "https://raw.githubusercontent.com/battery-data-alliance/$1-ontology/main/$1.ttl"),
    ("R7",  [],
             r"^ontology/([^/]+)/source/?$",
             "https://raw.githubusercontent.com/battery-data-alliance/$1-ontology/main/$1.ttl"),
    ("R8",  [],
             r"^ontology/([^/]+)/context/?$",
             "https://battery-data-alliance.github.io/$1-ontology/context/context.json"),
    ("R9",  [],
             r"^ontology/([^/]+)/schema/vendors/([^/]+)/?$",
             "https://battery-data-alliance.github.io/$1-ontology/schema/vendors/$2.json"),
    ("R10", [],
             r"^ontology/([^/]+)/schema/?$",
             "https://battery-data-alliance.github.io/$1-ontology/schema/schema.json"),
    # Versioned — specific pattern first
    ("R11", [],
             r"^ontology/([^/]+)/([0-9]+\.[0-9]+\.[0-9]+)/\1-inferred/?$",
             "https://battery-data-alliance.github.io/$1-ontology/versions/$2/$1-inferred.ttl"),
    # Versioned short form /1.0.0 — content-negotiated
    ("R12", [("text/html", True), (r"application/xhtml\+xml", False)],
             r"^ontology/([^/]+)/([0-9]+\.[0-9]+\.[0-9]+)/?$",
             "https://battery-data-alliance.github.io/$1-ontology/versions/$2/$1.html"),
    ("R13", [(r"application/ld\+json", False)],
             r"^ontology/([^/]+)/([0-9]+\.[0-9]+\.[0-9]+)/?$",
             "https://battery-data-alliance.github.io/$1-ontology/versions/$2/context/context.json"),
    ("R14", [],
             r"^ontology/([^/]+)/([0-9]+\.[0-9]+\.[0-9]+)/?$",
             "https://battery-data-alliance.github.io/$1-ontology/versions/$2/$1.ttl"),
    # Versioned versionIRI form /1.0.0/name — content-negotiated
    ("R15", [("text/html", True), (r"application/xhtml\+xml", False)],
             r"^ontology/([^/]+)/([0-9]+\.[0-9]+\.[0-9]+)/\1/?$",
             "https://battery-data-alliance.github.io/$1-ontology/versions/$2/$1.html"),
    ("R16", [(r"application/ld\+json", False)],
             r"^ontology/([^/]+)/([0-9]+\.[0-9]+\.[0-9]+)/\1/?$",
             "https://battery-data-alliance.github.io/$1-ontology/versions/$2/context/context.json"),
    ("R17", [],
             r"^ontology/([^/]+)/([0-9]+\.[0-9]+\.[0-9]+)/\1/?$",
             "https://battery-data-alliance.github.io/$1-ontology/versions/$2/$1.ttl"),
    ("R18", [],
             r"^ontology/([^/]+)/([0-9]+\.[0-9]+\.[0-9]+)/inferred/?$",
             "https://battery-data-alliance.github.io/$1-ontology/versions/$2/$1-inferred.ttl"),
    ("R19", [],
             r"^ontology/([^/]+)/([0-9]+\.[0-9]+\.[0-9]+)/latest/?$",
             "https://raw.githubusercontent.com/battery-data-alliance/$1-ontology/$2/$1.ttl"),
    ("R20", [],
             r"^ontology/([^/]+)/([0-9]+\.[0-9]+\.[0-9]+)/source/?$",
             "https://raw.githubusercontent.com/battery-data-alliance/$1-ontology/$2/$1.ttl"),
    ("R21", [],
             r"^ontology/([^/]+)/([0-9]+\.[0-9]+\.[0-9]+)/context/?$",
             "https://battery-data-alliance.github.io/$1-ontology/versions/$2/context/context.json"),
    ("R22", [],
             r"^ontology/([^/]+)/([0-9]+\.[0-9]+\.[0-9]+)/schema/vendors/([^/]+)/?$",
             "https://battery-data-alliance.github.io/$1-ontology/versions/$2/schema/vendors/$3.json"),
    ("R23", [],
             r"^ontology/([^/]+)/([0-9]+\.[0-9]+\.[0-9]+)/schema/?$",
             "https://battery-data-alliance.github.io/$1-ontology/versions/$2/schema/schema.json"),
]


def conditions_pass(conditions, accept):
    if not conditions:
        return True
    return any(re.search(c_re, accept) for c_re, _ in conditions)


def apply_substitution(template, groups):
    result = template
    for i, g in enumerate(groups, start=1):
        result = result.replace(f"${i}", g)
    return result


def simulate(path, accept=""):
    path = path.lstrip("/")
    for label, conds, pattern, subst in RULES:
        if not conditions_pass(conds, accept):
            continue
        m = re.match(pattern, path)
        if m:
            dest = apply_substitution(subst, list(m.groups()))
            return label, dest
    return None, None


BASE_GH  = "https://battery-data-alliance.github.io/battery-data-format-ontology"
BASE_RAW = "https://raw.githubusercontent.com/battery-data-alliance/battery-data-format-ontology"

TESTS = [
    # Non-versioned main ontology IRI
    ("main | browser",       "ontology/battery-data-format", "text/html",           "R2",  f"{BASE_GH}/battery-data-format.html"),
    ("main | JSON-LD agent", "ontology/battery-data-format", "application/ld+json", "R3",  f"{BASE_GH}/context/context.json"),
    ("main | Turtle agent",  "ontology/battery-data-format", "text/turtle",         "R4",  f"{BASE_GH}/battery-data-format.ttl"),
    ("main | RDF/XML agent", "ontology/battery-data-format", "application/rdf+xml", "R4",  f"{BASE_GH}/battery-data-format.ttl"),
    ("main | no Accept",     "ontology/battery-data-format", "",                    "R4",  f"{BASE_GH}/battery-data-format.ttl"),
    ("main | trailing /",    "ontology/battery-data-format/","text/html",           "R2",  f"{BASE_GH}/battery-data-format.html"),
    # Non-versioned utility endpoints
    ("inferred",             "ontology/battery-data-format/inferred",  "", "R5",  f"{BASE_GH}/battery-data-format-inferred.ttl"),
    ("inferred alternate",   "ontology/battery-data-format-inferred",  "", "R1",  f"{BASE_GH}/battery-data-format-inferred.ttl"),
    ("latest",               "ontology/battery-data-format/latest",    "", "R6",  f"{BASE_RAW}/main/battery-data-format.ttl"),
    ("source",               "ontology/battery-data-format/source",    "", "R7",  f"{BASE_RAW}/main/battery-data-format.ttl"),
    ("context",              "ontology/battery-data-format/context",   "", "R8",  f"{BASE_GH}/context/context.json"),
    ("vendor neware_csv",    "ontology/battery-data-format/schema/vendors/neware_csv",    "", "R9",  f"{BASE_GH}/schema/vendors/neware_csv.json"),
    ("vendor biologic_mpt",  "ontology/battery-data-format/schema/vendors/biologic_mpt", "", "R9",  f"{BASE_GH}/schema/vendors/biologic_mpt.json"),
    ("schema",               "ontology/battery-data-format/schema",    "", "R10", f"{BASE_GH}/schema/schema.json"),
    # Versioned short form /1.0.0
    ("v1.0.0 | browser",    "ontology/battery-data-format/1.0.0", "text/html",           "R12", f"{BASE_GH}/versions/1.0.0/battery-data-format.html"),
    ("v1.0.0 | JSON-LD",    "ontology/battery-data-format/1.0.0", "application/ld+json", "R13", f"{BASE_GH}/versions/1.0.0/context/context.json"),
    ("v1.0.0 | Turtle",     "ontology/battery-data-format/1.0.0", "text/turtle",         "R14", f"{BASE_GH}/versions/1.0.0/battery-data-format.ttl"),
    # Versioned versionIRI form /1.0.0/battery-data-format
    ("vIRI | browser",      "ontology/battery-data-format/1.0.0/battery-data-format", "text/html",           "R15", f"{BASE_GH}/versions/1.0.0/battery-data-format.html"),
    ("vIRI | JSON-LD",      "ontology/battery-data-format/1.0.0/battery-data-format", "application/ld+json", "R16", f"{BASE_GH}/versions/1.0.0/context/context.json"),
    ("vIRI | Turtle",       "ontology/battery-data-format/1.0.0/battery-data-format", "text/turtle",         "R17", f"{BASE_GH}/versions/1.0.0/battery-data-format.ttl"),
    ("vIRI | no Accept",    "ontology/battery-data-format/1.0.0/battery-data-format", "",                    "R17", f"{BASE_GH}/versions/1.0.0/battery-data-format.ttl"),
    # Versioned utility endpoints
    ("v inferred",          "ontology/battery-data-format/1.0.0/inferred",                         "", "R18", f"{BASE_GH}/versions/1.0.0/battery-data-format-inferred.ttl"),
    ("v inferred alternate","ontology/battery-data-format/1.0.0/battery-data-format-inferred",      "", "R11", f"{BASE_GH}/versions/1.0.0/battery-data-format-inferred.ttl"),
    ("v latest",            "ontology/battery-data-format/1.0.0/latest",                           "", "R19", f"{BASE_RAW}/1.0.0/battery-data-format.ttl"),
    ("v source",            "ontology/battery-data-format/1.0.0/source",                           "", "R20", f"{BASE_RAW}/1.0.0/battery-data-format.ttl"),
    ("v context",           "ontology/battery-data-format/1.0.0/context",                          "", "R21", f"{BASE_GH}/versions/1.0.0/context/context.json"),
    # These vendor cases exercise the rewrite RULES only (this script is a
    # self-contained mod_rewrite simulator, not a live check). The 1.0.0 form is
    # left hyphenated to match how the 1.0.0 tag named the file. NOTE: the deploy
    # workflow does not currently publish schema/vendors/ into the site, so these
    # redirect targets 404 in practice regardless of casing (tracked separately).
    ("v vendor novonix-csv","ontology/battery-data-format/1.0.0/schema/vendors/novonix-csv",        "", "R22", f"{BASE_GH}/versions/1.0.0/schema/vendors/novonix-csv.json"),
    ("v schema",            "ontology/battery-data-format/1.0.0/schema",                           "", "R23", f"{BASE_GH}/versions/1.0.0/schema/schema.json"),
]

passed = failed = 0
print(f"  {'':4} {'Test':<26} {'Rule':<5}  Destination")
print("  " + "-" * 110)
for desc, path, accept, exp_rule, exp_dest in TESTS:
    rule, dest = simulate(path, accept)
    ok = (rule == exp_rule and dest == exp_dest)
    if ok:
        passed += 1
        short_dest = dest.replace("https://battery-data-alliance.github.io/battery-data-format-ontology", "…gh.io/bdf-ontology")
        short_dest = short_dest.replace("https://raw.githubusercontent.com/battery-data-alliance/battery-data-format-ontology", "…raw/bdf-ontology")
        print(f"  PASS  {desc:<26} {rule:<5}  {short_dest}")
    else:
        failed += 1
        print(f"  FAIL  {desc:<26}")
        print(f"        expected  rule={exp_rule}  dest={exp_dest}")
        print(f"        got       rule={rule}  dest={dest}")

print()
print(f"  {passed}/{passed + failed} passed")
