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

def lookup(D, *keys, **kwdargs):
    result = tct.deepget(D, *keys, **kwdargs)
    loglist.append((keys, result))
    return result


# ==================================================
# define
# --------------------------------------------------

# use 0 or 1
debug_always_make_milestones_snapshot = 1

import time

talk = None
time_started_at_unixtime = time.time()
time_started_at = tct.logstamp_finegrained(unixtime=time_started_at_unixtime, fmt='%Y-%m-%d %H:%M:%S %f')
configset = lookup(facts, 'run_command', 'configset', default='Default')


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

if configset:
    result['MILESTONES'].append({'configset': configset})

if talk is not None:
    result['MILESTONES'].append({'talk': talk})

if time_started_at:
    result['MILESTONES'].append({'time_started_at': time_started_at})

if time_started_at_unixtime:
    result['MILESTONES'].append({'time_started_at_unixtime': time_started_at_unixtime})

if 'always':
    result['MILESTONES'].append({'debug_always_make_milestones_snapshot': debug_always_make_milestones_snapshot})




# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)


# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
