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
toolchain_name = facts['toolchain_name']
workdir = params['workdir']
loglist = result['loglist'] = result.get('loglist', [])
exitcode = CONTINUE = 0


# ==================================================
# Make a copy of milestones for later inspection?
# --------------------------------------------------

if 0 or milestones.get('debug_always_make_milestones_snapshot'):
    tct.make_snapshot_of_milestones(params['milestonesfile'], sys.argv[1])


# ==================================================
# Helper functions
# --------------------------------------------------

deepget = tct.deepget

def lookup(D, *keys, **kwdargs):
    result = deepget(D, *keys, **kwdargs)
    loglist.append((keys, result))
    return result

def firstNotNone(*args):
    for arg in args:
        if arg is not None:
            return arg
    else:
        return None


# ==================================================
# List all settings we handle here
# --------------------------------------------------

configset = None
debug_always_make_milestones_snapshot = None
smtp_host = None
talk = None
time_started_at = None
time_started_at_unixtime = None

# ==================================================
# Set initial values (1)
# --------------------------------------------------
import time

configset = deepget(facts, 'run_command', 'configset', default='Default')
time_started_at_unixtime = time.time()


# ==================================================
# Set initial values (2)
# --------------------------------------------------

# use 0 or 1
debug_always_make_milestones_snapshot = 1

smtp_host = firstNotNone(
    deepget(milestones, 'smtp_host', default=None),
    deepget(facts, 'run_command', 'smtp_host', default=None),
    deepget(facts, 'tctconfig', configset, 'smtp_host', default=None),
    '')

talk = firstNotNone(
    deepget(milestones, 'talk', default=None),
    deepget(facts, 'run_command', 'talk', default=None),
    deepget(facts, 'tctconfig', configset, 'talk', default=None),
    0)

time_started_at = tct.logstamp_finegrained(unixtime=time_started_at_unixtime, fmt='%Y-%m-%d %H:%M:%S %f')

# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')
    if not configset:
        exitcode = 22

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('PROBLEM with params')

if CONTINUE != 0:
    loglist.append({'CONTINUE': CONTINUE})
    loglist.append('NOTHING to do')


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    talk_builtin = 1
    talk_run_command = tct.deepget(facts, 'run_command', 'talk')
    talk_tctconfig = tct.deepget(facts, 'tctconfig', configset, 'talk')
    talk = int(talk_run_command or talk_tctconfig or talk_builtin)

if talk > 1:
    print('# --------', toolchain_name, time_started_at)


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if configset is not None:
    result['MILESTONES'].append({'configset': configset})

if debug_always_make_milestones_snapshot is not None:
    result['MILESTONES'].append({'debug_always_make_milestones_snapshot': debug_always_make_milestones_snapshot})

if smtp_host is not None:
    result['MILESTONES'].append({'smtp_host': smtp_host})

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
