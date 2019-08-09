#!/usr/bin/env python
# coding: utf-8

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
from __future__ import absolute_import

import codecs
import os
import six
import sys
import tct

from tct import deepget

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

def lookup(D, *keys, **kwdargs):
    result = deepget(D, *keys, **kwdargs)
    loglist.append((keys, result))
    return result

# ==================================================
# define
# --------------------------------------------------

sitemap_files_html = []
sitemap_files_html_count = None
sitemap_files_html_jsonfile = None
sitemap_files_html_txtfile = None
sitemap_files_singlehtml = []
sitemap_files_singlehtml_count = None
sitemap_files_singlehtml_jsonfile = None
sitemap_files_singlehtml_txtfile = None
xeq_name_cnt = 0

# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    build_html_folder = lookup(milestones, 'build_html_folder')
    if not build_html_folder:
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
    for build_folder, sitemap_files in [
            (build_html_folder, sitemap_files_html),
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

    sitemap_files_html.sort()
    sitemap_files_singlehtml.sort()

if 1 and sitemap_files_html and 'to json':
    sitemap_files_html_jsonfile = os.path.join(
        workdir, 'sitemap_files_html.json')
    tct.writejson(sitemap_files_html, sitemap_files_html_jsonfile)

if 1 and sitemap_files_singlehtml and 'to json':
    sitemap_files_singlehtml_jsonfile = os.path.join(
        workdir, 'sitemap_files_singlehtml.json')
    tct.writejson(sitemap_files_singlehtml, sitemap_files_singlehtml_jsonfile)

if 1 and sitemap_files_html and 'to txt':
    sitemap_files_html_txtfile = os.path.join(
        workdir, 'sitemap_files_html.txt')
    with codecs.open(sitemap_files_html_txtfile, 'w', 'utf-8') as f2:
        for line in sitemap_files_html:
            f2.write('%s\n' % line)


if 1 and sitemap_files_singlehtml and 'to txt':
    sitemap_files_singlehtml_txtfile = os.path.join(
        workdir, 'sitemap_files_singlehtml.txt')
    with codecs.open(sitemap_files_singlehtml_txtfile, 'w', 'utf-8') as f2:
        for line in sitemap_files_singlehtml:
            f2.write('%s\n' % line)

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if sitemap_files_html_count is not None:
    result['MILESTONES'].append(
        {'sitemap_files_html_count': sitemap_files_html_count})

if sitemap_files_html_jsonfile:
    result['MILESTONES'].append(
        {'sitemap_files_html_jsonfile': sitemap_files_html_jsonfile})

if sitemap_files_singlehtml_count is not None:
    result['MILESTONES'].append(
        {'sitemap_files_singlehtml_count': sitemap_files_singlehtml_count})

if sitemap_files_singlehtml_jsonfile:
    result['MILESTONES'].append({
        'sitemap_files_singlehtml_jsonfile':
        sitemap_files_singlehtml_jsonfile})

if sitemap_files_html_txtfile:
    result['MILESTONES'].append({
        'sitemap_files_html_txtfile': sitemap_files_html_txtfile})

if sitemap_files_singlehtml_txtfile:
    result['MILESTONES'].append({
        'sitemap_files_singlehtml_txtfile': sitemap_files_singlehtml_txtfile})


# ==================================================
# save result
# --------------------------------------------------

tct.save_the_result(result, resultfile, params, facts, milestones, exitcode, CONTINUE)


# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
