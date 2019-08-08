#!/usr/bin/env python
# coding: utf-8

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
from __future__ import absolute_import

import os
import shutil
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
toolchain_name = facts['toolchain_name']
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

included_files_check_logfile = None
sitemap_files_html_jsonfile = None
sitemap_files_singlehtml_jsonfile = None
TheProjectResultBuildinfoCheckIncludesFile = None
TheProjectResultBuildinfoSitemapFilesHtmlJson = None
TheProjectResultBuildinfoSitemapFilesHtmlTxt = None
TheProjectResultBuildinfoSitemapFilesSinglehtmlJson = None
TheProjectResultBuildinfoSitemapFilesSinglehtmlTxt = None
xeq_name_cnt = 0

# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    TheProjectResultBuildinfo = lookup(milestones, 'TheProjectResultBuildinfo')

    if not TheProjectResultBuildinfo:
        CONTINUE = -2

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('Nothing to do for these params')


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    included_files_check_logfile = lookup(milestones, 'included_files_check_logfile')
    if included_files_check_logfile:
        dummy, fname = os.path.split(included_files_check_logfile)
        fname = 'includedFilesCheck.txt'
        TheProjectResultBuildinfoCheckIncludesFile = os.path.join(TheProjectResultBuildinfo, fname)
        shutil.copy(included_files_check_logfile, TheProjectResultBuildinfoCheckIncludesFile)

if 0 and exitcode == CONTINUE:
    sitemap_files_html_jsonfile = lookup(milestones, 'sitemap_files_html_jsonfile')
    if sitemap_files_html_jsonfile:
        dummy, fname = os.path.split(sitemap_files_html_jsonfile)
        TheProjectResultBuildinfoSitemapFilesHtmlJson = os.path.join(TheProjectResultBuildinfo, fname)
        shutil.copy(sitemap_files_html_jsonfile, TheProjectResultBuildinfoSitemapFilesHtmlJson)

if 0 and exitcode == CONTINUE:
    sitemap_files_singlehtml_jsonfile = lookup(milestones, 'sitemap_files_singlehtml_jsonfile')
    if sitemap_files_singlehtml_jsonfile:
        dummy, fname = os.path.split(sitemap_files_singlehtml_jsonfile)
        TheProjectResultBuildinfoSitemapFilesSinglehtmlJson = os.path.join(TheProjectResultBuildinfo, fname)
        shutil.copy(sitemap_files_singlehtml_jsonfile, TheProjectResultBuildinfoSitemapFilesSinglehtmlJson)

if exitcode == CONTINUE:
    sitemap_files_html_txtfile = lookup(milestones, 'sitemap_files_html_txtfile')
    if sitemap_files_html_txtfile:
        dummy, fname = os.path.split(sitemap_files_html_txtfile)
        TheProjectResultBuildinfoSitemapFilesHtmlTxt = os.path.join(TheProjectResultBuildinfo, fname)
        shutil.copy(sitemap_files_html_txtfile, TheProjectResultBuildinfoSitemapFilesHtmlTxt)

if exitcode == CONTINUE:
    sitemap_files_singlehtml_txtfile = lookup(milestones, 'sitemap_files_singlehtml_txtfile')
    if sitemap_files_singlehtml_txtfile:
        dummy, fname = os.path.split(sitemap_files_singlehtml_txtfile)
        TheProjectResultBuildinfoSitemapFilesSinglehtmlTxt = os.path.join(TheProjectResultBuildinfo, fname)
        shutil.copy(sitemap_files_singlehtml_txtfile, TheProjectResultBuildinfoSitemapFilesSinglehtmlTxt)


# ==================================================
# Set MILESTONE
# --------------------------------------------------
if TheProjectResultBuildinfoCheckIncludesFile:
    result['MILESTONES'].append({
        'TheProjectResultBuildinfoCheckIncludesFile':
        TheProjectResultBuildinfoCheckIncludesFile})

if TheProjectResultBuildinfoSitemapFilesHtmlJson:
    result['MILESTONES'].append({
        'TheProjectResultBuildinfoSitemapFilesHtmlJson':
        TheProjectResultBuildinfoSitemapFilesHtmlJson})

if TheProjectResultBuildinfoSitemapFilesSinglehtmlJson:
    result['MILESTONES'].append({
        'TheProjectResultBuildinfoSitemapFilesSinglehtmlJson':
        TheProjectResultBuildinfoSitemapFilesSinglehtmlJson})

if TheProjectResultBuildinfoSitemapFilesHtmlTxt:
    result['MILESTONES'].append({
        'TheProjectResultBuildinfoSitemapFilesHtmlTxt':
        TheProjectResultBuildinfoSitemapFilesHtmlTxt})

if TheProjectResultBuildinfoSitemapFilesSinglehtmlTxt:
    result['MILESTONES'].append({
        'TheProjectResultBuildinfoSitemapFilesSinglehtmlTxt':
        TheProjectResultBuildinfoSitemapFilesSinglehtmlTxt})


# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)


# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
