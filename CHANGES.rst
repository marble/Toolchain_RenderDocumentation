Release v2.7.0 (to be released)
===============================

* 70ef40f Neutralize images with src scheme 'javascript:' or 'data:'
* 80f62b3 Neutralize hyperlinks that would start like 'data:'
* 74f469e [BUGFIX] Do not pretty print postprocessed html code


Release v2.6.1 (Jun 23, 2019)
=============================

* 75abf03 [BUGFIX] Use the correct formatter="minimal" with BeautifulSoup
* 6dbb907 [BUGFIX] Dump the right sitemap-files list for singlehtml


Release v2.6.0 (Jun 22, 2019)
=============================

* ffbd087 Dump info to stdout if there are forbidden include files
* f68ebf0 Dump warnings.txt to stdout if not in _buildinfo
* 4606616 Add rel="nofollow noopener" to external + foreign links
* ee6533e Return sitemap-files in .txt format and not .json as result
* ec9fb21 Provide sitemap-files as .txt file too
* 4d65da1 v2.6.0 Set new version number


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

* work in progress

Release v2.2.0
==============

* work in progress




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
