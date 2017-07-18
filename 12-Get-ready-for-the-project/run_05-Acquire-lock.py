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
# Make a copy of milestones for later inspection?
# --------------------------------------------------

if 0 or milestones.get('debug_always_make_milestones_snapshot'):
    tct.make_snapshot_of_milestones(params['milestonesfile'], sys.argv[1])


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

# ==================================================
# define
# --------------------------------------------------

talk = milestones.get('talk', 1)
lockfile = None
lockfile_time = None
lockfile_planned = None
lockfile_planned_time = None
lockfile_planned_age = None
lockfile_removed = None
lockfile_create_logstamp = None
unixtime = None


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')
    configset = milestones_get('configset')
    toolchain_temp_home = params_get('toolchain_temp_home')
    if not (configset and toolchain_temp_home):
        exitcode = 22

if exitcode == CONTINUE:
    lockfile_ttl_seconds = milestones.get('lockfile_ttl_seconds', 3600)
    lockfile_name = tct.deepget(facts, 'tctconfig', configset, 'lockfile_name')
    loglist.append(('lockfile_name', lockfile_name))
    if not lockfile_name:
        exitcode = 22

if exitcode == CONTINUE:
    lockfile_planned = os.path.join(toolchain_temp_home, lockfile_name)
    loglist.append(('lockfile_planned', lockfile_planned))

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('PROBLEM with params')


# ==================================================
# work
# --------------------------------------------------

import time

if exitcode == CONTINUE:

    if os.path.exists(lockfile_planned):
        loglist.append('lockfile_planned exists')
        lockfile_planned_time = int(os.path.getmtime(lockfile_planned))
        loglist.append(('lockfile_planned_time', lockfile_planned_time))
        unixtime = int(time.time())
        loglist.append(('unixtime', unixtime))
        lockfile_planned_age = unixtime - lockfile_planned_time
        loglist.append(('lockfile_planned_age', lockfile_planned_age))

        if talk:
            print('is locked since %s seconds, will wait until %s' % (lockfile_planned_age, lockfile_ttl_seconds))

        # seconds
        if lockfile_planned_age >= lockfile_ttl_seconds:
            os.remove(lockfile_planned)
            if os.path.exists(lockfile_planned):
                exitcode = 22
            else:
                lockfile_removed = lockfile_planned
                if talk:
                    print('unlock because of age')

if exitcode == CONTINUE:
    if os.path.exists(lockfile_planned):
        loglist.append('lockfile_planned still exists')
        exitcode = 22

if exitcode == CONTINUE:
    tct.writejson(facts, lockfile_planned)
    lockfile_create_logstamp = tct.logstamp_finegrained()
    lockfile = lockfile_planned
    lockfile_time = int(os.path.getmtime(lockfile))
    loglist.append(('lockfile_time', lockfile_time))


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if lockfile:
    result['MILESTONES'].append({'lockfile': lockfile})

if lockfile_time:
    result['MILESTONES'].append({'lockfile_time': lockfile_time})

if lockfile_planned:
    result['MILESTONES'].append({'lockfile_planned': lockfile_planned})

if lockfile_planned_age:
    result['MILESTONES'].append({'lockfile_planned_age': lockfile_planned_age})

if lockfile_planned_time:
    result['MILESTONES'].append({'lockfile_planned_time': lockfile_planned_time})

if lockfile_removed:
    result['MILESTONES'].append({'lockfile_removed':lockfile_removed})

if lockfile_create_logstamp:
    result['MILESTONES'].append({'lockfile_create_logstamp': lockfile_create_logstamp})


# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
