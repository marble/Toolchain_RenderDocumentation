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
    toolchain_name = params.get('toolchain_name')
    toolchain_temp_home = params.get('toolchain_temp_home')
    loglist.append(('toolchain_name', toolchain_name))
    loglist.append(('toolchain_temp_home', toolchain_temp_home))

if exitcode == CONTINUE:
    if not (toolchain_name and toolchain_temp_home):
        exitcode = 2

if exitcode == CONTINUE:
    toolchain_actions = params.get('toolchain_actions', [])
    lockfile_name = tct.deepget(facts, 'tctconfig', toolchain_name, 'lockfile_name')
    loglist.append(('toolchain_actions', toolchain_actions))
    loglist.append(('lockfile_name', lockfile_name))

if exitcode == CONTINUE:
    if not (lockfile_name):
        exitcode = 2

if 1:
    lockfiles_removed = []

# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    for action in toolchain_actions:
        if action == 'help':
            'Should not occurr'
        elif action == 'unlock':
            for top, dirs, files in os.walk(toolchain_temp_home):
                dirs[:] = [] # stop recursion
                for fname in files:
                    if fname == lockfile_name:
                        lockfile = os.path.join(top, fname)
                        os.remove(lockfile)
                        lockfiles_removed.append(lockfile)
            exitcode = 99
            break

# ==================================================run_01.py
# Set MILESTONE
# --------------------------------------------------

if lockfiles_removed:
    result['MILESTONES'].append({'lockfiles_removed': lockfiles_removed})

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
