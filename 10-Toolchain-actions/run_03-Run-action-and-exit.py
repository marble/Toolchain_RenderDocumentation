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
# define
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

lockfiles_removed = []
toolchain_actions = params_get('toolchain_actions', [])
removed_dirs = []

# ==================================================
# Get and check required milestone(s)
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')
    toolchain_name = params_get('toolchain_name')
    toolchain_temp_home = params_get('toolchain_temp_home')
    run_id = facts_get('run_id')

if exitcode == CONTINUE:
    if not (toolchain_name and toolchain_temp_home and run_id):
        exitcode = 2

if exitcode == CONTINUE:
    lockfile_name = tct.deepget(facts, 'tctconfig', toolchain_name, 'lockfile_name')
    loglist.append(('lockfile_name', lockfile_name))

if exitcode == CONTINUE:
    if not (lockfile_name):
        exitcode = 2

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('PROBLEM with params')

# ==================================================
# work
# --------------------------------------------------

import shutil

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

        elif action == 'clean':
            for top, dirs, files in os.walk(toolchain_temp_home):
                dirs.sort()
                for adir in dirs:
                    fpath = os.path.join(top, adir)
                    if not run_id in adir:
                        if os.path.isdir(fpath):
                            shutil.rmtree(fpath)
                dirs[:] = [] # stop recursion
            exitcode = 99
            break


# ==================================================run_01.py
# Set MILESTONE
# --------------------------------------------------

if exitcode == 99:
    result['MILESTONES'].append({'FINAL_EXITCODE': 0})

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
