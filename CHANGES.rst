===========
CHANGES.rst
===========

Release v3.0.0 (2022-04-25)
===========================

* small fixes
* switch to v3.x scheme
* bugfix: fetch settings.dump.json from Logdir instead of Makedir


Release v2.12.dev4 (2022-04-22)
===============================

*  Add step run_19-Try-to-derive-scm_version_info.py
*  Insert message "No terms have been indexed yet in this documentation."
   if gendindex.html is empty.
*  Remove the "convert from OpenOffice" stuff


Release v2.12.dev3 (2022-04-06)
===============================

*  Improve messages and saying Good bye
*  Make snapshot of very first step too
*  Add helper tool 'where_was_it_changed.py'


Release v2.12.dev2 (2021-11-05)
===============================

*  Update html post-processing:
   `div.literal-block-wrapper.docutils.container` →
   `div.literal-block-wrapper.docutils.du-container`


Release v2.12.dev1 (2021-10-03)
===============================

*  Port to Python-3, keeping compatibility with Python-2.
*  Requires TCT with version >= v1.2


Release v2.11.1 (2021-01-21)
============================

*  6064e37  [BUGFIX] in run_64-Process-Html.py


Release v2.11.0 (2020-12-10)
============================

*  8033dc4  Improve information in final Good-bye output
*  b4f0fa9  Address only theme files in HTML postprocessing
*  d5eaf5d  Add milestone "theme_module_path"
*  0f112e5  Add -jauto to Sphinx build for parallel build
*  436189d  Add run_70-Create-objects-inv-json.py



Release v2.10.1 (2020-05-09)
===========================

*  [FEATURE] Add option '-c sphinxVerboseLevel n'


Release v2.10.0 (2020-05-08)
===========================

*  Supress pip warnings
*  Add '-c allow_unsafe 1' option
*  Prepare input files for 'sphinxcontrib.gitloginfo' Sphinx extension
*  Use 0 or 255 for FINAL_EXIT_CODE, indication whether html build succeeded


Release v2.9.1 (2020-02-26)
===========================

*  Bugfix: replacing static files


Release v2.9.0 (2020-02-25)
===========================

*  Handle the sphinx_typo3_theme
*  Account for Azure CDN


Release v2.8.0 (Oct 21, 2019)
=============================

Lots of improvements!

Starting with 'reason' strings in the toolchain:

*  b956969 Revamp 'reason' strings and 'exitcode'

Replace the old CheckIncludeFiles code:

*  32a54f6 Revamp run_04-Check-included-files

Start renaming the old variable name and use, for example, 'origproject' (now)
instead of 'gitdir' (previously):

*  ce168d6 Add origproject in run_30-Adjust-the-buildsettings

Allow configuration of which files of the original project
'origproject' (=/PROJECT) shall be available in the copy 'TheProject' that
is used for documentation generation:

*  36e9c6b Add run_22-Get-more-documentation-files
*  e131a6b Use 'get_documentation' in run_03-Copy-the-project.py
*  31e372e Add get_documentation_defaults in run_01-Start-with-everything


Make everything work for every localization as well:

*  9c08fb6 [BUGFIX][FEATURE] Have package result for each localization
*  884f9db [BUGFIX][FEATURE] Have latex result for each localization
*  286e1d2 [BUFGIX] Make localization work again


Allow a mapping for themes:

*  4c0e0b6 Update run_08-Copy-the-makedir.py: Copy /THEMES as MAKEDIR/_themes


Make everything configurable in - superpowered! - jobfile.json:

*  b662d32 [!!!] jobfile.json takes precedence of commandline params


Enhancements, interesting or useful stuff:

*  b3ab839 Set 'nonstopmode' in Makefile for 'make latex'
*  cf5ea9d run_40-Make-html.py: Use 'sphinx-build -v -v -v'



Release v2.7.0 (Aug 15, 2019)
=============================

Lots of changes!
See the few commits in the 'master' branch or all the ugly little changes
done back and forth in the 'develop' branch that both lead to this v2.7.1

Some from 'develop':

*  70ef40f Neutralize images with src scheme 'javascript:' or 'data:'
*  80f62b3 Neutralize hyperlinks that would start like 'data:'
*  74f469e [BUGFIX] Do not pretty print postprocessed html code



Release v2.6.1 (Jun 23, 2019)
=============================

*  75abf03 [BUGFIX] Use the correct formatter="minimal" with BeautifulSoup
*  6dbb907 [BUGFIX] Dump the right sitemap-files list for singlehtml


Release v2.6.0 (Jun 22, 2019)
=============================

*  ffbd087 Dump info to stdout if there are forbidden include files
*  f68ebf0 Dump warnings.txt to stdout if not in _buildinfo
*  4606616 Add rel="nofollow noopener" to external + foreign links
*  ee6533e Return sitemap-files in .txt format and not .json as result
*  ec9fb21 Provide sitemap-files as .txt file too
*  4d65da1 v2.6.0 Set new version number


Release v2.5.1 (Jun 14 29, 2019)
================================

*  Fix logic error
*  For speed reasons rewrite html files only if necessary


Release v2.5.0 (Jun 14 29, 2019)
================================

*  Add CHANGES.rst
*  Don't offer docs/manual.sxw as possibility
*  Solve `issue #64 of t3docs/docker-render-documentation
   <https://github.com/t3docs/docker-render-documentation/issues/64>`__
   "Weird appearance of README" rendering
*  Collect sitemap files `issue #64 of t3docs/docker-render-documentation
   <https://github.com/t3docs/docker-render-documentation/issues/63>`__
*  Postprocess html files: prettify, sanitize neutralize javascript links
   `issue #67 of t3docs/docker-render-documentation
   <https://github.com/t3docs/docker-render-documentation/issues/67>`__


Release v2.4.0 (May 29, 2019)
=============================


*  convert markdown files by pandoc
*  catch all exceptions of Yaml Settings.yml parser
*  processed by python-modernize


Release v2.3.1 (May 22, 2018)
=============================

...

Release v2.3.0 (May 7, 2018)
============================

*  work in progress

Release v2.2.0
==============

*  work in progress




Contributing here
=================

Some recommended headlines:

| Bugs fixed
| Dependencies
| Deprecated
| Features added
| Features removed
| Enhancements
| Incompatible changes
| Significant internal changes

Maximum characters per line: 79 (except longlinks)

         1         2         3         4         5         6         7

1234567890123456789012345678901234567890123456789012345678901234567890123456789

End of CHANGES.
