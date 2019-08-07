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

copied_latex_resources = []
xeq_name_cnt = 0


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    make_latex = lookup(milestones, 'make_latex', default=None)
    if not make_latex:
        CONTINUE == -2

if exitcode == CONTINUE:
    build_latex = lookup(milestones, 'build_latex', default=None)
    build_latex_folder = lookup(milestones, 'build_latex_folder', default=None)
    latex_contrib_typo3_folder = tct.deepget(facts, 'tctconfig', 'configset', 
                                             'latex_contrib_typo3_folder', default=None)
    if not (1
            and build_latex
            and build_latex_folder
            and latex_contrib_typo3_folder):
        CONTINUE = -2

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('Bad PARAMS or nothing to do')


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    if not os.path.isdir(latex_contrib_typo3_folder):
        loglist.append(('is not a directory', latex_contrib_typo3_folder))
        CONTINUE = -2

if exitcode == CONTINUE:

    for thing in os.listdir(latex_contrib_typo3_folder):
        if thing in ['.', '..', 'Makefile']:
            continue
        srcpath = os.path.join(latex_contrib_typo3_folder, thing)
        destpath = os.path.join(build_latex_folder, thing)
        if os.path.isdir(srcpath):
            shutil.copytree(srcpath, destpath)
        else:
            shutil.copy(srcpath, destpath)
        copied_latex_resources.append(thing)


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if copied_latex_resources:
    result['MILESTONES'].append({'copied_latex_resources':
                                 copied_latex_resources})


# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)


# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
