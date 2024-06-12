import sys
import os

# Добавьте путь к корневой директории проекта
sys.path.insert(0, os.path.abspath('../..'))
# Добавьте путь к директории src
sys.path.insert(0, os.path.abspath('../../src'))

project = 'address book'
copyright = '2024, Artem'
author = 'Artem'
release = '1.0'

# -- General configuration ---------------------------------------------------
extensions = ['sphinx.ext.autodoc']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
html_theme = 'nature'
html_static_path = ['_static']
