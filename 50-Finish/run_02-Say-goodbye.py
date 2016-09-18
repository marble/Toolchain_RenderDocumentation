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

import time

talk = milestones.get('talk', 1)
time_finished_at_unixtime = time.time()
time_finished_at = tct.logstamp_finegrained(unixtime=time_finished_at_unixtime, fmt='%Y-%m-%d %H:%M:%S %f')

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

time_started_at = milestones_get('time_started_at', '')
time_started_at_unixtime = milestones_get('time_started_at_unixtime', 0)
rebuild_needed = milestones_get('rebuild_needed')
achieved = milestones_get('assembled', [])[:]
if milestones_get('package_file'):
    achieved.append('package')
if milestones_get('publish_dir_buildinfo'):
    achieved.append('buildinfo')
achieved.sort()
cmdline_reportlines = milestones_get('cmdline_reportlines', [])

# ==================================================
# work
# --------------------------------------------------

if talk:
    indent = '   '
    print()
    print(tct.deepget(milestones, 'buildsettings', 'project', default='PROJECT'),
          tct.deepget(milestones, 'buildsettings', 'version', default='VERSION'),
          os.path.split(milestones_get('makedir', default='MAKEDIR'))[1],
          sep = ' // ', end = '\n')
    print(indent,
          time_started_at,
          ',  took: ', '%4.2f seconds' % (time_finished_at_unixtime - time_started_at_unixtime),
          ',  toolchain: ', facts_get('toolchain_name', 'TOOLCHAIN_NAME'),
          sep='')
    if rebuild_needed:
        print(indent, 'REBUILD_NEEDED', sep='')
        print(indent, 'OK: ', ', '.join(achieved), sep='')
    else:
        print(indent, 'build is not needed', sep='')

    print()

    if cmdline_reportlines:
        for line in cmdline_reportlines:
            print(indent, line, sep='')
        print()

if talk > 1:

    if exitcode == CONTINUE:

        if talk > 1:
            if achieved:
                s = ', '.join(sorted(achieved))
            else:
                s = 'nothing'
            print("Produced: %s" % s)


    if exitcode == CONTINUE:
        if talk > 1:
            duration = ''
            if time_started_at_unixtime and time_finished_at_unixtime:
                duration = 'duration: %4.2f seconds' % (time_finished_at_unixtime - time_started_at_unixtime)
            print(time_finished_at, duration)

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if time_finished_at:
    result['MILESTONES'].append({'time_finished_at': time_finished_at})

if time_finished_at_unixtime:
    result['MILESTONES'].append({'time_finished_at_unixtime': time_finished_at_unixtime})

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
