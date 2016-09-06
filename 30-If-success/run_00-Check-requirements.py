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
loglist = result['loglist'] = result.get('loglist', [])
exitcode = CONTINUE = 0

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
    create_buildinfo = milestones_get('create_buildinfo')
    publish_dir_buildinfo = milestones_get('publish_dir_buildinfo')
    TheProjectResultBuildinfo = milestones_get('TheProjectResultBuildinfo')
    TheProjectResultBuildinfoMessage = milestones_get('TheProjectResultBuildinfoMessage')
    toolchain_name = params_get('toolchain_name')

if exitcode == CONTINUE:
    if not (
        create_buildinfo and
        publish_dir_buildinfo and
        TheProjectResultBuildinfo and
        TheProjectResultBuildinfoMessage and
        toolchain_name):

        exitcode = 2

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('PROBLEMS with params')

# ==================================================
# work
# --------------------------------------------------



# ==================================================
# Set MILESTONE
# --------------------------------------------------

if 0:
    result['MILESTONES'].append({'dummy': 0})

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
