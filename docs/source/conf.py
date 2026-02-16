import os
import sys

sys.path.insert(0, os.path.abspath('../..'))

project = 'ai-slop_gate'
author = 'Serg'
release = '2'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx_rtd_theme',
    'myst_parser',
    'sphinx_copybutton',
    'sphinxcontrib.mermaid',
]

html_theme = 'sphinx_rtd_theme'

source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

templates_path = ['_templates']
html_static_path = ['_static']

master_doc = "index"

# Do not try to render JSON files
exclude_patterns = ["*.json"]

# MyST improvements
myst_heading_anchors = 3
myst_enable_extensions = [
    "colon_fence",
    "linkify",
    "substitution",
    "deflist",
    "linkify-it-py",
]

