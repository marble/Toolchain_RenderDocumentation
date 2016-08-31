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
toolname_pure = params['toolname_pure']
workdir = params['workdir']
loglist = result['loglist'] = result.get('loglist', [])
exitcode = CONTINUE = 0

# ==================================================
# define
# --------------------------------------------------
import time

talk = None
time_started_at_unixtime = time.time()
time_started_at = tct.logstamp_finegrained(unixtime=time_started_at_unixtime, fmt='%Y-%m-%d %H:%M:%S %f')

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
    toolchain_name = params_get('toolchain_name')
    if not toolchain_name:
        exitcode = 99

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('PROBLEMS with params')

# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    talk_builtin = 1
    talk_run_command = tct.deepget(facts, 'run_command', 'talk')
    talk_tctconfig = tct.deepget(facts, 'tctconfig', facts['toolchain_name'], 'talk')
    talk = int(talk_run_command or talk_tctconfig or talk_builtin)

if talk:
    print('\n# --------', facts['toolchain_name'], time_started_at)

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if talk is not None:
    result['MILESTONES'].append({'talk': talk})
if time_started_at:
    result['MILESTONES'].append({'time_started_at': time_started_at})
if time_started_at_unixtime:
    result['MILESTONES'].append({'time_started_at_unixtime': time_started_at_unixtime})

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------
sys.exit(exitcode)
