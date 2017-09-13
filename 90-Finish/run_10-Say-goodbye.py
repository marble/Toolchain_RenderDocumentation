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
binabspath = sys.argv[2]
facts = tct.readjson(params['factsfile'])
milestones = tct.readjson(params['milestonesfile'])
resultfile = params['resultfile']
result = tct.readjson(resultfile)
loglist = result['loglist'] = result.get('loglist', [])
toolname = params['toolname']
toolname_pure = params['toolname_pure']
workdir = params['workdir']
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

import time

talk = milestones.get('talk', 1)

# This is the time that we really finish
time_finished_at_2_unixtime = time.time()
time_finished_at_2 = tct.logstamp_finegrained(unixtime=time_finished_at_2_unixtime, fmt='%Y-%m-%d %H:%M:%S %f')

age_message = ''
xeq_name_cnt = 0


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    # required milestones
    requirements = []

    # just test
    for requirement in requirements:
        v = milestones_get(requirement)
        if not v:
            loglist.append("'%s' not found" % requirement)
            exitcode = 22

    # fetch
    checksum_ttl_seconds = milestones_get('checksum_ttl_seconds', 1)

    # test
    if not (checksum_ttl_seconds):
        exitcode = 22

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('PROBLEMS with params')

if CONTINUE != 0:
    loglist.append({'CONTINUE': CONTINUE})
    loglist.append('NOTHING to do')


# ==================================================
# work
# --------------------------------------------------

checksum_time = milestones_get('checksum_time', 0)
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


if talk:
    indent = '   '
    print()
    print(tct.deepget(milestones, 'buildsettings', 'project', default='PROJECT'),
          tct.deepget(milestones, 'buildsettings', 'version', default='VERSION'),
          os.path.split(milestones_get('makedir', default='MAKEDIR'))[1],
          sep = ' : ', end = '\n')
    print(indent,
          'makedir ',
          milestones_get('makedir', default='MAKEDIR'),
          sep = '', end = '\n')
    print(indent,
          time_started_at,
          ',  took: ', '%4.2f seconds' % (time_finished_at_2_unixtime - time_started_at_unixtime),
          ',  toolchain: ', facts_get('toolchain_name', 'TOOLCHAIN_NAME'),
          sep='')

    age_seconds = time_finished_at_2_unixtime - checksum_time
    age_message = "age %3.1f of %3.1f hours" % (age_seconds / 3600., checksum_ttl_seconds / 3600.)
    age_message += ",  %3.1f of %3.1f days" % (age_seconds / 3600. / 24., checksum_ttl_seconds / 3600. / 24.)

    if rebuild_needed:
        cause = 'because of '
        if milestones.get('rebuild_needed_because_of_change'):
            cause += 'change'
        elif milestones.get('rebuild_needed_because_of_age'):
            cause += 'age'
        elif milestones.get('rebuild_needed_run_command'):
            cause += 'parameter'
        elif milestones.get('rebuild_needed_tctconfig'):
            cause += 'config'
        else:
            cause += '???'
        print(indent, 'REBUILD_NEEDED ', cause, ',  ', age_message, sep='')
        print(indent, 'OK: ', ', '.join(achieved), sep='')
    else:
        print(indent, 'still ok, ', age_message, sep='')

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
            if time_started_at_unixtime and time_finished_at_2_unixtime:
                duration = 'duration: %4.2f seconds' % (time_finished_at_2_unixtime - time_started_at_unixtime)
            print(time_finished_at_2, duration)


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if time_finished_at_2:
    result['MILESTONES'].append({'time_finished_at_2': time_finished_at_2})

if time_finished_at_2_unixtime:
    result['MILESTONES'].append({'time_finished_at_2_unixtime': time_finished_at_2_unixtime})


# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
