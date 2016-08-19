#!/usr/bin/env python
# coding: utf-8

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
import os
import tct
import sys

params = tct.readjson(sys.argv[1])
facts = tct.readjson(params['factsfile'])
milestones = tct.readjson(params['milestonesfile'])
resultfile = params['resultfile']
result = tct.readjson(resultfile)
toolname = params["toolname"]
loglist = result['loglist'] = result.get('loglist', [])
exitcode = CONTINUE = 0

# ==================================================
# Get and check required milestone(s)
# --------------------------------------------------

def milestones_get(name, default=None):
    result = milestones.get(name, default)
    loglist.append((name, result))
    return result

if exitcode == CONTINUE:
    TheProjectResult = milestones_get('TheProjectResult')
    TheProjectResultBuildinfo = milestones_get('TheProjectResultBuildinfo')
    build_latex_folder = milestones_get('build_latex_folder')

if not (TheProjectResult and TheProjectResultBuildinfo and build_latex_folder):
    exitcode = 2

if exitcode == CONTINUE:
    TheProjectResultBuildinfoPdfLogFile = None
    TheProjectResultBuildinfoPdfFilesCnt = 0

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
        shutil.copy(src, dest)
        TheProjectResultBuildinfoPdfFilesCnt += 1
        if dest.endswith('.log'):
            TheProjectResultBuildinfoPdfLogFile = dest

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if exitcode == CONTINUE:
    result['MILESTONES'].append({
        'TheProjectResultBuildinfoPdfFilesCnt': TheProjectResultBuildinfoPdfFilesCnt})

    if TheProjectResultBuildinfoPdfLogFile:
        result['MILESTONES'].append({
            'TheProjectResultBuildinfoPdfLogFile': TheProjectResultBuildinfoPdfLogFile})

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
