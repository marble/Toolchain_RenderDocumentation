#!/usr/bin/env python

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
toolname_short = os.path.splitext(toolname)[0][4:]  # run_01-Name.py -> 01-Name
workdir = params['workdir']
loglist = result['loglist'] = result.get('loglist', [])
exitcode = CONTINUE = 0

# ==================================================
# define
# --------------------------------------------------

TheProjectLog = None
TheProjectBuild = None

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

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')
    TheProject = milestones_get('TheProject')

    if not (TheProject):
        exitcode = 2

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('PROBLEM with params')

# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:

    TheProjectLog = TheProject + 'Log'
    if not os.path.exists(TheProjectLog):
        os.makedirs(TheProjectLog)

    TheProjectBuild = TheProject + 'Build'
    if not os.path.exists(TheProjectBuild):
        os.makedirs(TheProjectBuild)

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if TheProjectBuild:
    result['MILESTONES'].append({'TheProjectBuild': TheProjectBuild})
if TheProjectLog:
    result['MILESTONES'].append({'TheProjectLog': TheProjectLog})

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
