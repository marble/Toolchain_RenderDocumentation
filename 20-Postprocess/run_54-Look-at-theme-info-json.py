#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function
from __future__ import absolute_import

import codecs
import glob
import json
import os
import re
import six
import sys
import tct

from tct import deepget

params = tct.readjson(sys.argv[1])
binabspath = sys.argv[2]
facts = tct.readjson(params['factsfile'])
milestones = tct.readjson(params['milestonesfile'])
reason = ''
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

theme_info = None
theme_info_json_file = None
xeq_name_cnt = 0

# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    build_html_folder = lookup(milestones, 'build_html_folder')

    if not (1
            and build_html_folder
            and 1):
        CONTINUE = -2
        reason = 'Bad PARAMS or nothing to do'

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append(reason)


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:

    f1path = os.path.join(build_html_folder, '_static/_version_info_GENERATED.json')
    if not os.path.exists(f1path):
        CONTINUE = -2
        reason = "'_static/_version_info_GENERATED.json' not found"

if exitcode == CONTINUE:
    with open(f1path) as f1:
        theme_info = json.load(f1)

    theme_info_json_file = f1path


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if theme_info_json_file:
    result['MILESTONES'].append(
        {'theme_info_json_file': theme_info_json_file})

if theme_info:
    result['MILESTONES'].append(
        {'theme_info': theme_info})



# ==================================================
# save result
# --------------------------------------------------

tct.save_the_result(result, resultfile, params, facts, milestones, exitcode, CONTINUE, reason)


# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
