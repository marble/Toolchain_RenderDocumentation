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
# define
# --------------------------------------------------

lockfile = ''
lockfile_planned = ''
lockfile_create_logstamp = ''

# ==================================================
# Get and check required milestone(s)
# --------------------------------------------------

def milestones_get(name, default=None):
    result = milestones.get(name, default)
    loglist.append((name, result))
    return result

def params_get(name, default=None):
    result = params.get(name, default)
    loglist.append((name, result))
    return result

if exitcode == CONTINUE:
    loglist.append(('CHECK PARAMS'))
    toolchain_name = params_get('toolchain_name')
    toolchain_temp_home = params_get('toolchain_temp_home')
    if not (toolchain_name and toolchain_temp_home):
        exitcode = 2

if exitcode == CONTINUE:
    lockfile_name = tct.deepget(facts, 'tctconfig', toolchain_name, 'lockfile_name')
    loglist.append(('lockfile_name', lockfile_name))
    if not lockfile_name:
        exitcode = 2

if exitcode == CONTINUE:
    lockfile_planned = os.path.join(toolchain_temp_home, lockfile_name)
    loglist.append(('lockfile_planned', lockfile_planned))

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('PROBLEMS with params')

# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    if os.path.exists(lockfile_planned):
        loglist.append('lockfile already exists!')
        exitcode = 2

if exitcode == CONTINUE:
    tct.writejson(facts, lockfile_planned)
    lockfile_create_logstamp = tct.logstamp_finegrained()
    lockfile = lockfile_planned

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if exitcode == CONTINUE:
    result['MILESTONES'].append({
        'lockfile': lockfile,
        'lockfile_create_logstamp': lockfile_create_logstamp,
    })

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
