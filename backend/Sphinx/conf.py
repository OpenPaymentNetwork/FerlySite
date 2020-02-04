# -*- coding: utf-8 -*-
#
# OPN API documentation build configuration file, created by
# sphinx-quickstart on Fri Oct 25 14:51:03 2013.
#
# This file is execfile()d with the current directory set to its containing
# dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
import os.path
import sys

here = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(here, '_themes'))

_preconf = {}

# -- General configuration ----------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
# NOTE: buildout.d/base.cfg depends on a specific version of
# sphinxcontrib.httpdomain.
extensions = [
    'sphinxcontrib.httpdomain',
    'opn_sphinx_theme',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The encoding of source files.
#source_encoding = 'utf-8-sig'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'Ferly API'
copyright = u'2020'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = '1.01'
# The full version, including alpha/beta/rc tags.
release = '1.01'

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#language = None

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
#today = ''
# Else, today_fmt is used as the format for a strftime call.
#today_fmt = '%B %d, %Y'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build']

# The reST default role (used for this markup: `text`) to use for all
# documents.
#default_role = None

# If true, '()' will be appended to :func: etc. cross-reference text.
#add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
#add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
#show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# A list of ignored prefixes for module index sorting.
#modindex_common_prefix = []

# rst_epilog is added to the source of every page.
rst_epilog = """
.. |authorize_url| replace:: ``[=public_url=]/authorize``
.. |app_create_url| replace:: [=public_url=]/app/create
.. |app_url| replace:: [=public_url=]/app
.. |my_example_url| replace:: ``[=public_url=]/app/my.example``
.. |sample_paycode_url| replace:: ``[=public_url=]/t/987654321/code``
.. |sample_profile_url1| replace:: ``[=public_url=]/feWill``
.. |sample_profile_url2| replace:: ``[=public_url=]/p/5638122909/``
.. |api_url| replace:: ``[=api_url=]``
.. |wallet_info_api_url| replace:: ``[=api_url=]/wallet/info``
.. |token_api_url| replace:: ``[=api_url=]/token``
.. |stream_bd_url| replace:: ``[=stream_url=]/bd/sockjs``
"""


# -- Options for HTML output --------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
import opn_sphinx_theme
html_theme_path = opn_sphinx_theme.html_theme_path()
html_theme = 'opn_sphinx_theme'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
html_theme_options = {
    # 'headerbg': '#2f3d57',
    # 'footerbg': '#2f3d57',
}

# Add any paths that contain custom themes here, relative to this directory.
#html_theme_path = []

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
html_title = "FERLY API Documentation"

# A shorter title for the navigation bar.  Default is the same as html_title.
html_short_title = "FERLY OPN API"

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
#html_logo = '_static/logo.png'

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
#html_favicon = None

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
#html_last_updated_fmt = '%b %d, %Y'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
#html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
html_sidebars = {
    '**': [
        'logo-text.html',
        'globaltoc.html',
        'searchbox.html',
    ],
}

# Additional templates that should be rendered to pages, maps page names to
# template names.
#html_additional_pages = {}

# If false, no module index is generated.
#html_domain_indices = True

# If false, no index is generated.
#html_use_index = True

# If true, the index is split into individual pages for each letter.
#html_split_index = False

# If true, links to the reST sources are added to the pages.
html_show_sourcelink = False

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
#html_show_sphinx = True

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
#html_show_copyright = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
#html_use_opensearch = ''

# This is the file name suffix for HTML files (e.g. ".xhtml").
#html_file_suffix = None

# Output file base name for HTML help builder.
htmlhelp_basename = 'OPNAPIdoc'


# -- Options for LaTeX output -------------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #'papersize': 'letterpaper',

    # The font size ('10pt', '11pt' or '12pt').
    #'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    #'preamble': '',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass
# [howto/manual]).
latex_documents = [
    ('index', 'OPTAPI.tex', u'API Documentation',
     u'OPN', 'manual'),
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
#latex_logo = None

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
#latex_use_parts = False

# If true, show page references after internal links.
#latex_show_pagerefs = False

# If true, show URL addresses after external links.
#latex_show_urls = False

# Documents to append as an appendix to all manuals.
#latex_appendices = []

# If false, no module index is generated.
#latex_domain_indices = True


# -- Options for manual page output -------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    ('index', 'opnapi', u'API Documentation',
     [u'OPN'], 1)
]

# If true, show URL addresses after external links.
#man_show_urls = False


# -- Options for Texinfo output -----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    ('index', 'OPNAPI', u'API Documentation',
     u'OPN', 'OPNAPI', '',
     'Miscellaneous'),
]

# Documents to append as an appendix to all manuals.
#texinfo_appendices = []

# If false, no module index is generated.
#texinfo_domain_indices = True

# How to display URL addresses: 'footnote', 'no', or 'inline'.
#texinfo_show_urls = 'footnote'




# Substitute variables early so they work in code examples.
# https://github.com/sphinx-doc/sphinx/issues/4054

def early_substitute(app, docname, source):
    result = source[0]
    for key in app.config.early_substitutions:
        result = result.replace(key, app.config.early_substitutions[key])
    source[0] = result


early_substitutions = {
    "{{example_client_id}}": "4954253560",
    "{{example_client_secret}}": "S3krit4TestApp",
    "{{example_device_uuid}}": "907fb623-a4a9-4b59-b952-ad783bea7246",

    "{{example1_attempt_id}}": "8025915877",
    "{{example1_attempt_secret}}": "GQJ6lBJONnrByb2BQl0Xe0jOMRE",
    "{{example1_factor_id_1}}": "7cce202b",
    "{{example1_code_1}}": "623652",
    "{{example1_factor_id_2}}": "7963b341",
    "{{example1_code_2}}": "559258",

    "{{example2_attempt_id}}": "4399844113",
    "{{example2_attempt_secret}}": "b5JmjbEwYBtit9raLEJhj0LukIM",
    "{{example2_factor_id_1}}": "99b1f585",
    "{{example2_code_1}}": "146847",

    "{{example3_attempt_id}}": "5618911532",
    "{{example3_attempt_secret}}": "q9ieEMNt0G3RbgTBjlOWy5C7vhY",
    "{{example3_factor_id}}": "fb546e07",
    "{{example3_code}}": "073467126",
}


def setup(app):
    app.add_config_value('early_substitutions', {}, True)
    app.connect('source-read', early_substitute)
