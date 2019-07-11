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
# from pygments.lexer import RegexLexer
# from pygments import token
# from sphinx.highlighting import lexers


# -- Project information -----------------------------------------------------

project = 'eecalpy'
copyright = '2019, Sebastian Werner'
author = 'Sebastian Werner'

# The full version, including alpha/beta/rc tags
release = '0.9.0'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
# extensions = [
# ]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'
html_theme_path =["_themes",]

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# -- Syntax highlighting for Eecalpy scripts ----------------------------------
# class EecalpyLexer(RegexLexer):
#     name = 'eecalpy'

#     tokens = {
#         'root': [
#             (r'[a-zA-Z][a-zA-Z_0-9]*', token.Name),
#             (r'\?', token.Keyword),
#             (r'\s', token.Text)
#         ]
#     }

# lexers['eecalpy'] = EecalpyLexer(startinline=True)