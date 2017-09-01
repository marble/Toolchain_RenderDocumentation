#!/usr/bin/env python
# coding: utf-8

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
import cgi
import os
import shutil
import sys
import tct

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

deepget = tct.deepget

def lookup(D, *keys, **kwdargs):
    result = deepget(D, *keys, **kwdargs)
    loglist.append((keys, result))
    return result

# ==================================================
# define
# --------------------------------------------------

TheProjectLogHtmlmail = ''
TheProjectLogREADMEfile = ''
xeq_name_cnt = 0


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    TheProjectLogHtmlmailMessageHtml = lookup( milestones, 'TheProjectLogHtmlmailMessageHtml')
    # "https://t3docs.local/typo3cms/Project/default/0.0.0/"
    absurl_html_dir = lookup(milestones, 'absurl_html_dir')

    if not (TheProjectLogHtmlmailMessageHtml and absurl_html_dir):
        CONTINUE = -2

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('Cannot work with these PARAMS')


# ==================================================
# work
# --------------------------------------------------

import codecs

if exitcode == CONTINUE:
    TheProjectLogREADMEfile = os.path.join(os.path.split(TheProjectLogHtmlmailMessageHtml)[0], 'README.html')

    with codecs.open(TheProjectLogHtmlmailMessageHtml, 'r', 'utf-8') as f1:
        uhtml = f1.read().decode('utf-8', 'replace')

    replacements = [
        ('href="' + absurl_html_dir + '_buildinfo/',
         'href="./'),
        ('href="' + absurl_html_dir + 'singlehtml/"',
         'href="../singlehtml/Index.html"'),
        ('href="' + absurl_html_dir + '"',
         'href="../Index.html"'),
        ('href="' + absurl_html_dir,
         'href="../') ]

    for a, b in replacements:
        uhtml = uhtml.replace(a, b)

    with codecs.open(TheProjectLogREADMEfile, 'w', 'utf-8') as f2:
        f2.write(uhtml)

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if TheProjectLogREADMEfile:
    result['MILESTONES'].append({'TheProjectLogREADMEfile': TheProjectLogREADMEfile})


# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
