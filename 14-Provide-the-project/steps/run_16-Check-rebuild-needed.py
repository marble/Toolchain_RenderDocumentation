#!/usr/bin/env python

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
toolchain_name = facts['toolchain_name']
exitcode = CONTINUE = 0

# ==================================================
# define
# --------------------------------------------------

age = None
checksum_new = None
rebuild_needed = None
rebuild_needed_because_of_age = None
rebuild_needed_because_of_change = None
rebuild_needed_run_command = None
rebuild_needed_tctconfig = None
talk = milestones.get('talk', 1)
xeq_name_cnt = 0

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
    toolname = params_get('toolname')
    workdir = params_get('workdir')
    documentation_folder = milestones_get('documentation_folder')
    if not (workdir and toolname and documentation_folder):
        exitcode = 2

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('PROBLEM with params')

if exitcode == CONTINUE:
    checksum_old = milestones_get('checksum_old', '')
    checksum_time = milestones_get('checksum_time')
    checksum_file = milestones_get('checksum_file')
    checksum_ttl_seconds = milestones_get('checksum_ttl_seconds', 86400)

# ==================================================
# work
# --------------------------------------------------

import codecs
import subprocess
import time

rebuild_needed_run_command = tct.deepget(facts, 'run_command', 'rebuild_needed', default=None)
rebuild_needed_tctconfig = tct.deepget(facts, 'tctconfig', toolchain_name, 'rebuild_needed', default=None)

def cmdline(cmd, cwd=None):
    if cwd is None:
        cwd = os.getcwd()
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=cwd)
    out, err = process.communicate()
    exitcode = process.returncode
    return exitcode, cmd, out, err

if exitcode == CONTINUE:
    if documentation_folder:

        # This one isn't stable, it seems.
        # # http://unix.stackexchange.com/questions/35832/how-do-i-get-the-md5-sum-of-a-directorys-contents-as-one-sum
        # theCmd = u"find . -type f | LC_ALL=C sort | cpio -o --quiet | md5sum | awk '{ print $1 }'"

        # what we used in the old 'cron_rebuild.sh'
        theCmd = u"""find . -type f -exec md5sum {} \; | md5sum | awk '{ print $1 }'"""

        exitcode, cmd, out, err = cmdline(theCmd, cwd=documentation_folder)
        loglist.append([exitcode, cmd, out, err])
        checksum_new = out.strip()
        loglist.append('checksum_old: ' + checksum_old)
        loglist.append('checksum_new: ' + checksum_new)

        xeq_name_cnt += 1
        filename_cmd = 'xeq-%s-%d-%s.txt' % (toolname_pure, xeq_name_cnt, 'cmd')
        filename_err = 'xeq-%s-%d-%s.txt' % (toolname_pure, xeq_name_cnt, 'err')
        filename_out = 'xeq-%s-%d-%s.txt' % (toolname_pure, xeq_name_cnt, 'out')
        with codecs.open(os.path.join(workdir, filename_cmd), 'w', 'utf-8') as f2:
            f2.write(theCmd)
        with codecs.open(os.path.join(workdir, filename_out), 'w', 'utf-8') as f2:
            f2.write(unicode(out))
        with codecs.open(os.path.join(workdir, filename_err), 'w', 'utf-8') as f2:
            f2.write(unicode(err))

if exitcode == CONTINUE:

    if checksum_time:
        now = int(time.time())
        age = now - checksum_time
        if age > checksum_ttl_seconds:
            rebuild_needed_because_of_age = 1

    if checksum_new == checksum_old:
        rebuild_needed_because_of_change = 0
    else:
        rebuild_needed_because_of_change = 1

    if any([rebuild_needed_because_of_change, rebuild_needed_because_of_age,
           rebuild_needed_run_command, rebuild_needed_tctconfig]):
        rebuild_needed = 1
    else:
        rebuild_needed = 0

    if checksum_new:
        if checksum_new != checksum_old or rebuild_needed:
            with file(checksum_file, 'wb') as f2:
                f2.write(checksum_new)


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if checksum_new is not None:
    result['MILESTONES'].append({'checksum_new': checksum_new})

if rebuild_needed is not None:
    result['MILESTONES'].append({'rebuild_needed': rebuild_needed})

if rebuild_needed_because_of_age is not None:
    result['MILESTONES'].append({'rebuild_needed_because_of_age': rebuild_needed_because_of_age})

if rebuild_needed_because_of_change is not None:
    result['MILESTONES'].append({'rebuild_needed_because_of_change': rebuild_needed_because_of_change})

if rebuild_needed_run_command is not None:
    result['MILESTONES'].append({'rebuild_needed_run_command': rebuild_needed_run_command})

if rebuild_needed_tctconfig is not None:
    result['MILESTONES'].append({'rebuild_needed_tctconfig': rebuild_needed_tctconfig})


# ==================================================
# talk
# --------------------------------------------------

if talk > 1:
    if rebuild_needed:
        print('rebuild_needed: yes')
    else:
        agestr = ''
        if age:
            agestr = ', age: %s seconds' % age
        print('rebuild_needed: no%s' % agestr)

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)

