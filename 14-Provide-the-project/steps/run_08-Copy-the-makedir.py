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

xeq_name_cnt = 0
TheProjectMakedir = None

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
    makedir = milestones_get('makedir')
    TheProject = milestones_get('TheProject')

    if not (makedir and TheProject):
        loglist.append('SKIPPING')
        CONTINUE = -1

# ==================================================
# work
# --------------------------------------------------

from shutil import copytree

if exitcode == CONTINUE:
    TheProjectMakedir = TheProject + 'Makedir'
    if os.path.exists(TheProjectMakedir):
        loglist.append(('Error: TheProjectMakdir should not exist', TheProjectMakedir))
        exitcode = 2

if exitcode == CONTINUE:
    source = makedir
    destination = TheProjectMakedir
    copytree(source, destination)

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if TheProjectMakedir:
    result['MILESTONES'].append({'TheProjectMakedir': TheProjectMakedir})

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
