#!/usr/bin/env python

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
import tct
import os
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
    toolchain_name = params.get('toolchain_name')
    toolchain_temp_home = params.get('toolchain_temp_home')
    loglist.append(('toolchain_name', toolchain_name))
    loglist.append(('toolchain_temp_home', toolchain_temp_home))
    if not (toolchain_name and toolchain_temp_home):
        exitcode = 2

if exitcode == CONTINUE:
    lockfile_name = tct.deepget(facts, 'tctconfig', toolchain_name, 'lockfile_name')
    loglist.append(('lockfile_name', lockfile_name))
    if not lockfile_name:
        exitcode = 2

if exitcode == CONTINUE:
    lockfile = os.path.join(toolchain_temp_home, lockfile_name)
    loglist.append(('lockfile', lockfile))

# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    if os.path.exists(lockfile):
        loglist.append('lockfile already exists!')
        exitcode = 2

if exitcode == CONTINUE:
    tct.writejson(facts, lockfile)


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if exitcode == CONTINUE:
    result['MILESTONES'].append({'lockfile': lockfile})

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
