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
# Get and check required milestone(s)
# --------------------------------------------------

def milestones_get(name, default=None):
    result = milestones.get(name, default)
    loglist.append((name, result))
    return result

def facts_get(name, default=None):
    result = facts.get(name, default)
    loglist.append((name, result))
    return result

def params_get(name, default=None):
    result = params.get(name, default)
    loglist.append((name, result))
    return result


# ==================================================
# define
# --------------------------------------------------

xeq_name_cnt = 0
TheProjectResultBuildinfoPdfLogFile = None
TheProjectResultBuildinfoPdfFilesCnt = 0

# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    # required milestones
    requirements = []

    # just test
    for requirement in requirements:
        v = milestones_get(requirement)
        if not v:
            loglist.append("'%s' not found" % requirement)
            exitcode = 22

    # fetch
    TheProjectResult = milestones_get('TheProjectResult')
    TheProjectResultBuildinfo = milestones_get('TheProjectResultBuildinfo')
    build_latex_folder = milestones_get('build_latex_folder')

    # test
    if not (TheProjectResult and TheProjectResultBuildinfo and build_latex_folder):
        CONTINUE = -2

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('PROBLEMS with params')

if CONTINUE != 0:
    loglist.append({'CONTINUE': CONTINUE})
    loglist.append('NOTHING to do')


# ==================================================
# work
# --------------------------------------------------

import glob
import shutil

if exitcode == CONTINUE:
    files = glob.glob(build_latex_folder.rstrip('/') + '/PROJECT*.*')
    for file in files:
        filename = os.path.split(file)[1]
        src = os.path.join(build_latex_folder, file)
        dest = os.path.join(TheProjectResultBuildinfo, 'PDF' + filename)
        fileext = os.path.splitext(dest)[1]
        if fileext.lower() in ['.tex', '.log']:
            dest = dest + '.txt'
            shutil.copy(src, dest)
            TheProjectResultBuildinfoPdfFilesCnt += 1
            if dest.endswith('.log.txt'):
                TheProjectResultBuildinfoPdfLogFile = dest


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if TheProjectResultBuildinfoPdfLogFile:
    result['MILESTONES'].append({
        'TheProjectResultBuildinfoPdfLogFile': TheProjectResultBuildinfoPdfLogFile,
        'TheProjectResultBuildinfoPdfFilesCnt': TheProjectResultBuildinfoPdfFilesCnt
    })


# ==================================================
# save result
# --------------------------------------------------

tct.save_the_result(result, resultfile, params, facts, milestones, exitcode, CONTINUE)


# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
