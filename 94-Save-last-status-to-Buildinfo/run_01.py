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
errormsg = ''

# ==================================================
# Get and check required milestone(s)
# --------------------------------------------------
def milestones_get(name, default=None):
    result = milestones.get(name, default)
    loglist.append((name, result))
    return result

if exitcode == CONTINUE:
    tools_exitcodes = facts.get('tools_exitcodes')
    TheProjectResultBuildinfo = milestones_get('TheProjectResultBuildinfo')

if not (TheProjectResultBuildinfo and tools_exitcodes):
    CONTINUE = -1

# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    TheProjectResultBuildinfoExitcodesFile = os.path.join(TheProjectResultBuildinfo, 'exitcodes.json')
    tct.writejson(tools_exitcodes, TheProjectResultBuildinfoExitcodesFile)



# ==================================================
# Set MILESTONE
# --------------------------------------------------

if exitcode == CONTINUE:
    result['MILESTONES'].append({
        'TheProjectResultBuildinfoExitcodesFile': TheProjectResultBuildinfoExitcodesFile})

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
