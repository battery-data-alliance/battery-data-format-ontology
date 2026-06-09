from __future__ import annotations

import os
import subprocess
import sys

sys.path.insert(0, os.path.abspath(".."))

# -- Project information -----------------------------------------------------

project = "Battery Data Format Ontology"
author = "Battery Data Alliance"
copyright = "2024–2025, Battery Data Alliance"
version = "1.1"
release = "1.1.0"

# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.intersphinx",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.mathjax",
    "sphinx_design",
    "nbsphinx",
    "sphinx_copybutton",
]

autosectionlabel_prefix_document = True
source_suffix = ".rst"
master_doc = "index"
exclude_patterns = ["_build"]

# -- HTML output -------------------------------------------------------------

html_theme = "pydata_sphinx_theme"

html_theme_options = {
    "primary_sidebar_end": [],
    "show_nav_level": 0,
    "show_toc_level": 0,
    "navbar_center": ["navbar-nav"],
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/BatteryDataAlliance/BDAOntology",
            "icon": "fab fa-github-square",
        },
        {
            "name": "BDA Homepage",
            "url": "https://lfenergy.org/projects/battery-data-alliance/",
            "icon": "fas fa-globe",
        },
    ],
    "search_bar_text": "Search the ontology...",
    "show_prev_next": False,
    "footer_start": ["copyright"],
    "footer_center": ["sphinx-version"],
    "pygments_light_style": "friendly",
    "pygments_dark_style": "lightbulb",
}

html_title = "Battery Data Format Ontology"
html_logo = "assets/img/logo/battery-data-alliance-horizontal-color-2.svg"
html_favicon = "assets/img/logo/battery-data-alliance-horizontal-color-2.svg"
html_static_path = ["_static"]
html_css_files = ["css/custom.css"]
# The per-term tables on battery-data-format.rst embed LaTeX as raw HTML \(...\),
# which sphinx.ext.mathjax does not auto-detect; this force-loads MathJax there.
html_js_files = ["js/ensure-mathjax.js"]

html_sidebars = {
    "battery-data-format": [
        "search-field.html",
        "page-toc.html",
        "edit-this-page.html",
    ],
}

add_module_names = False


# -- Sphinx app hooks --------------------------------------------------------

def _generate_specification(app):
    script = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "scripts", "generate_specification.py")
    )
    if os.path.isfile(script):
        subprocess.run([sys.executable, script], check=True)


def setup(app):
    app.connect("builder-inited", _generate_specification)
