#!/usr/bin/env python
# coding: utf-8

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
from __future__ import absolute_import
import codecs
import json
import os
import tct
import sys
from bs4 import BeautifulSoup
from urlparse import urlparse

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

all_html_files_sanitized = None
all_singlehtml_files_sanitized = None
neutralized_links = []
neutralized_links_jsonfile = None
sitemap_files_html = []
sitemap_files_singlehtml = []
xeq_name_cnt = 0


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    build_html_folder = lookup(milestones, 'build_html_folder')
    sitemap_files_html_jsonfile = lookup(milestones, 'sitemap_files_html_jsonfile')
    if not (build_html_folder and sitemap_files_html_jsonfile):
        CONTINUE = -2

if exitcode == CONTINUE:
    build_singlehtml_folder = lookup(milestones, 'build_singlehtml_folder')
    sitemap_files_singlehtml_jsonfile = lookup(milestones,
                                         'sitemap_files_singlehtml_jsonfile')
    if (not build_html_folder) != (not sitemap_files_html_jsonfile):
        CONTINUE = -2
        loglist.append('Either have none or both')

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('Bad PARAMS or nothing to do')


# ==================================================
# work
# --------------------------------------------------

def process_html_file(folder, relpath):
    soup_modified = False
    builder = os.path.split(folder)[1]
    abspath = folder + '/' + relpath
    with codecs.open(abspath, 'r', 'utf-8') as f1:
        soup = BeautifulSoup(f1, 'lxml')

    for link in soup.find_all('a'):
        href = link.get('href')
        if href is not None:
            if (href.lower().startswith('javascript:') or
                    href.lower().startswith('data:')):
                logname = builder + '/' + fpath
                neutralized_links.append((logname, href))
                link['href'] = '#'
                soup_modified = True
            else:
                o = urlparse(href)
                if o.hostname:
                    if o.hostname.split('.')[-2:] not in (['typo3','org'], ['typo3', 'com']):
                        rel = link.get('rel', '')
                        parts = rel.split()
                        if 'nofollow' not in parts:
                            parts.append('nofollow')
                        if 'noopener' not in parts:
                            parts.append('noopener')
                        link['rel'] = ' '.join(parts)
                        soup_modified = True

    if soup_modified:
        with open(abspath, 'wb') as f2:
            print(soup, file=f2)



if exitcode == CONTINUE:

    if sitemap_files_html_jsonfile:
        with codecs.open(sitemap_files_html_jsonfile, 'r', 'utf-8') as f1:
            sitemap_files_html = json.load(f1)

        for fpath in sitemap_files_html:
            process_html_file(build_html_folder.rstrip('/'), fpath)

        all_html_files_sanitized = 1

    if sitemap_files_singlehtml_jsonfile:
        with codecs.open(sitemap_files_singlehtml_jsonfile, 'r', 'utf-8') as f1:
            sitemap_files_singlehtmlfiles_html = json.load(f1)

        for fpath in sitemap_files_singlehtml:
            process_html_file(build_singlehtml_folder.rstrip('/'), fpath)

        all_singlehtml_files_sanitized = 1

if exitcode == CONTINUE:
    if neutralized_links:
        neutralized_links_jsonfile = os.path.join(workdir, 'neutralized_links.json')
        with codecs.open(neutralized_links_jsonfile, 'w', 'utf-8') as f2:
            json.dump(neutralized_links, f2)


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if neutralized_links_jsonfile:
    result['MILESTONES'].append(
        {'neutralized_links_jsonfile': neutralized_links_jsonfile})

if all_html_files_sanitized:
    result['MILESTONES'].append(
        {'all_html_files_sanitized': all_html_files_sanitized})

if all_singlehtml_files_sanitized:
    result['MILESTONES'].append(
        {'all_singlehtml_files_sanitized': all_singlehtml_files_sanitized})


# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)


# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
