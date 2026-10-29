# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'ZhangLab Docs'
copyright = '2025, Johannes L. Hörmann'
author = 'Johannes L. Hörmann'

import jotelha_docs
version = jotelha_docs.__version__
release = jotelha_docs.__version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinxcontrib.spelling',
    'sphinxcontrib.bibtex',
    'myst_parser'
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# -- Extension configuration -------------------------------------------------

# spell check with sphinxcontrib.spelling
spelling_lang = 'en_US'
spelling_show_suggestions = True

# bibliography with sphinxcontrib.bibtex
bibtex_bibfiles = ['refs.bib']
bibtex_default_style = 'unsrt'
bibtex_reference_style = 'label'

# Custom path note in README files

from pathlib import Path

from pathlib import Path

def is_root_index(app, doc_path: Path) -> bool:
    return doc_path.resolve() == Path(app.srcdir, "index.rst").resolve()


def inject_index_title(app, docname, source):
    """
    Automatically add a top-level heading to index.md
    based on the containing folder name.
    """
    doc_path = Path(app.env.doc2path(docname))

    if doc_path.name != "index.rst":
        return
    if is_root_index(app, doc_path):
        return

    folder_name = doc_path.parent.name

    title = (
        f"{folder_name}\n"
        f"{'=' * len(folder_name)}\n\n"
    )

    source[0] = title + source[0]


def add_path_note(app, docname, source):
    """
    Prepend a note showing the path relative to the Sphinx source directory
    for every index.rst file.
    """
    # Absolute path to the source file
    doc_path = Path(app.env.doc2path(docname))

    # Only apply to README.md files
    if doc_path.name.lower() != "index.rst":
        return
    if is_root_index(app, doc_path):
        return

    # Path relative to the Sphinx source directory
    rel_path = doc_path.parent.relative_to(app.srcdir)

    note = (
        ".. note::\n"
        f"   **Path:** ``{rel_path}``\n\n"
    )


    source[0] = note + source[0]


def setup(app):
    app.connect("source-read", inject_index_title)
    app.connect("source-read", add_path_note)


