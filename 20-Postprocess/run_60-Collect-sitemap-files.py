#!/usr/bin/env python
# coding: utf-8

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
from __future__ import absolute_import
import os
import tct
import sys
import six

params = tct.readjson(sys.argv[1])
binabspath = sys.argv[2]
facts = tct.readjson(params['factsfile'])
milestones = tct.readjson(params['milestonesfile'])
resultfile = params['resultfile']
result = tct.readjson(resultfile)
loglist = result['loglist'] = result.get('loglist', [])
toolname = params['toolname']
toolname_pure = params['toolname_pure']
workdir = params['workdir']
exitcode = CONTINUE = 0


# ==================================================
# Make a copy of milestones for later inspection?
# --------------------------------------------------

if 0 or milestones.get('debug_always_make_milestones_snapshot'):
    tct.make_snapshot_of_milestones(params['milestonesfile'], sys.argv[1])


# ==================================================
# Helper functions
# --------------------------------------------------

deepget = tct.deepget

def lookup(D, *keys, **kwdargs):
    result = deepget(D, *keys, **kwdargs)
    loglist.append((keys, result))
    return result

# ==================================================
# define
# --------------------------------------------------

sitemap_files_html = []
sitemap_files_html_jsonfile = None
sitemap_files_singlehtml = []
sitemap_files_singlehtml_jsonfile = None
xeq_name_cnt = 0

# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    build_html_folder = lookup(milestones, 'build_html_folder')
    if not (build_html_folder):
        CONTINUE = -2

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('Bad PARAMS or nothing to do')


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:

    build_singlehtml_folder = lookup(milestones, 'build_singlehtml_folder')
    for build_folder, sitemap_files in [(build_html_folder, sitemap_files_html),
                                        (build_singlehtml_folder, sitemap_files_singlehtml)]:
        if not build_folder:
            continue
        builder_logname = os.path.split(build_folder)[1]
        toplen = len(build_folder)
        for top, dirs, files in os.walk(build_folder):
            dirs[:] = [d for d in dirs if d != '_static']
            dirs.sort()
            files.sort()
            for fname in files:
                if not fname.endswith('.html'):
                    continue
                fpath = os.path.join(top, fname)
                file_logname = fpath[toplen:].lstrip('/')
                sitemap_files.append(file_logname)
                loglist.append('%s, %s' % (builder_logname, file_logname))

if sitemap_files_html:
    sitemap_files_html_jsonfile = os.path.join(workdir, 'sitemap_files_html.json')
    tct.writejson(sitemap_files_html, sitemap_files_html_jsonfile)

if sitemap_files_singlehtml:
    sitemap_files_singlehtml_jsonfile = os.path.join(workdir, 'sitemap_files_singlehtml.json')
    tct.writejson(sitemap_files_singlehtml, sitemap_files_singlehtml_jsonfile)

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if sitemap_files_html_jsonfile:
    result['MILESTONES'].append(
        {'sitemap_files_html_jsonfile': sitemap_files_html_jsonfile})

if sitemap_files_singlehtml_jsonfile:
    result['MILESTONES'].append(
        {'sitemap_files_singlehtml_jsonfile': sitemap_files_singlehtml_jsonfile})


# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)


# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
