#!/usr/bin/env python
# coding: utf-8

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
from __future__ import absolute_import

import glob
import os
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

postprocess_cleanup_files = None
xeq_name_cnt = 0

# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    build_html = lookup(milestones, 'build_html', default=None)
    build_singlehtml = lookup(milestones, 'build_singlehtml', default=None)
    TheProject = lookup(milestones, 'TheProject', default=None)

    if not (1
            and TheProject
            and (build_html or build_singlehtml)):
        CONTINUE = -1

if exitcode == CONTINUE:
    build_html_folder = lookup(milestones, 'build_html_folder', default=None)
    build_singlehtml_folder = lookup(milestones, 'build_singlehtml_folder',
                                     default=None)
    if not (build_html_folder or build_singlehtml_folder):
        CONTINUE = -1

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('Bad PARAMS or nothing to do')


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('Here we remove files that are - unfortunately - '
                   'still in the theme but are not needed.')

if exitcode == CONTINUE:
    file_patterns = [
        '.buildinfo',
        '_static/*.map',
        '_static/css/*.map',
        '_static/jquery-*.js',
        '_static/js/t3autocomplete2.js',
        '_static/js/zumklaun.js',
        '_static/searchtools-ORIGINAL.js',
        '_static/underscore-*.js',
    ]

if exitcode == CONTINUE:
    todolist = [item for item in [build_html_folder, build_singlehtml_folder]
                if item]

    for folder in todolist:
        for pattern in file_patterns:
            files = glob.glob(folder + '/' + pattern)
            if files:
                loglist.append(files)
                for fpath in files:
                    os.remove(fpath)
    if build_singlehtml_folder:
        fpath = os.path.join(build_singlehtml_folder, 'objects.inv')
        if os.path.exists(fpath):
            os.remove(fpath)

if exitcode == CONTINUE:
    postprocess_cleanup_files = 'done'

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if postprocess_cleanup_files is not None:
    result['MILESTONES'].append({
        'postprocess_cleanup_files': postprocess_cleanup_files,
    })


# ==================================================
# save result
# --------------------------------------------------

tct.save_the_result(result, resultfile, params, facts, milestones, exitcode, CONTINUE)


# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
