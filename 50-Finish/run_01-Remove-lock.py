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
toolname_pure = params['toolname_pure']
workdir = params['workdir']
loglist = result['loglist'] = result.get('loglist', [])
exitcode = CONTINUE = 0

# ==================================================
# define
# --------------------------------------------------

lockfile_removed = ''
lockfile_remove_logstamp = ''

# ==================================================
# Get and check required milestone(s)
# --------------------------------------------------

def milestones_get(name, default=None):
    result = milestones.get(name, default)
    loglist.append((name, result))
    return result

if exitcode == CONTINUE:
    lockfile = milestones_get('lockfile')
    if not (lockfile):
        CONTINUE = -1

# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    if os.path.isfile(lockfile):
        os.remove(lockfile)
        lockfile_removed = lockfile
        lockfile = ''
        lockfile_remove_logstamp = tct.logstamp_finegrained()

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if exitcode == CONTINUE:
    if lockfile_removed:
        result['MILESTONES'].append({
            'lockfile': lockfile,
            'lockfile_removed': lockfile_removed,
            'lockfile_remove_logstamp': lockfile_remove_logstamp,
        })

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
