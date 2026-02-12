import os
import sys

sys.path.insert(0, os.path.abspath('../../'))

project = 'ai_slop_gate'
copyright = '2026, Serg'
author = 'Serg'
release = '2'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx_rtd_theme',
    'myst_parser',
    'sphinx_copybutton',
]

html_theme = 'sphinx_rtd_theme'

source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}
