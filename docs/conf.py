import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))


# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))

# The master toctree document.
master_doc = "index"

# -- Project information -----------------------------------------------------

project = "Exalted 1e Charms"
copyright = ": All the content belong to White-Wolf. I am not affiliated with them in any way except in my love for their games"
author = "Jules Robichaud-Gagnon"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ["sphinx.ext.autodoc", "sphinxcontrib.mermaid"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]



# Full version
release = "1.0.0"

# Minor version
version = "0"

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "groundwork"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

html_css_files = [
    "css/mermaid.css",
]

html_logo = "_static/logo.webp"
html_show_sphinx = False
html_domain_indices = False
html_sidebars = {
    '**': ['globaltoc.html'],
}
