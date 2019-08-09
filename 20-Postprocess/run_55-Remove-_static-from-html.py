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
    result = tct.deepget(D, *keys, **kwdargs)
    loglist.append((keys, result))
    return result


# ==================================================
# define
# --------------------------------------------------

remove_static_folder_from_html_done = None
remove_static_folder_from_html_happened = None
xeq_name_cnt = 0


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    build_html_folder = lookup(milestones, 'build_html_folder', default=None)
    build_singlehtml_folder = lookup(milestones, 'build_singlehtml_folder',
                                     default=None)
    replace_static_in_html_done = lookup(
        milestones, 'replace_static_in_html_done', default=None)

    if not (1
            and (build_html_folder or build_singlehtml_folder)
            and remove_static_folder_from_html_done):
        CONTINUE = -2

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('Bad PARAMS or nothing to do')


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:

    for build_folder in [build_html_folder, build_singlehtml_folder]:
        if not build_folder:
            continue
        fpath = os.path.join(build_folder, '_static')
        if os.path.exists(fpath):
            shutil.rmtree(fpath)
            loglist.append('%s, %s' % ('remove', fpath))
            remove_static_folder_from_html_happened = 1


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if remove_static_folder_from_html_done:
    result['MILESTONES'].append({
        'remove_static_folder_from_html_done':
        remove_static_folder_from_html_done})

if remove_static_folder_from_html_happened:
    result['MILESTONES'].append({
        'remove_static_folder_from_html_happened':
        remove_static_folder_from_html_happened})


# ==================================================
# save result
# --------------------------------------------------

tct.save_the_result(result, resultfile, params, facts, exitcode, CONTINUE)


# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
