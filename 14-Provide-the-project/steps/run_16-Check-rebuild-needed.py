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
exitcode = CONTINUE = 0

# ==================================================
# define
# --------------------------------------------------

xeq_name_cnt = 0
checksum_new = None
talk = milestones.get('talk', 1)
age = None

rebuild_needed = None


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

rebuild_needed = tct.deepget(facts, 'run_command', 'rebuild_needed')
if rebuild_needed == {}:
    rebuild_needed = tct.deepget(facts, 'tctconfig', facts['toolchain_name'], 'rebuild_needed')
if rebuild_needed == {}:
    rebuild_needed = 0
rebuild_needed = int(rebuild_needed)


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

    if checksum_time and not rebuild_needed:
        now = int(time.time())
        age = now - checksum_time
        if age > checksum_ttl_seconds:
            rebuild_needed = 1
            loglist.append('Rebuild is needed. Age %s is greater than checksum_ttl_seconds %s' % (age, checksum_ttl_seconds))

    if checksum_old and checksum_new and not rebuild_needed:
        if checksum_new != checksum_old:
            rebuild_needed = 1
            loglist.append('Rebuild is needed. Checksums are different.')

    if not checksum_old:
        rebuild_needed = 1
        loglist.append('Rebuild is needed. There is no previous checksum.')

    if not checksum_new and not rebuild_needed:
        rebuild_needed = 1
        loglist.append('Rebuild is needed. There is no new checksum (Strange!?.')

    if checksum_file and checksum_new:
        if checksum_old and checksum_old == checksum_new:
            loglist.append('checksums are equal')
        if rebuild_needed:
            with file(checksum_file, 'wb') as f2:
                f2.write(checksum_new)
            loglist.append('rebuild is needed, so new checksum is written')


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if rebuild_needed:
    result['MILESTONES'].append({'rebuild_needed': rebuild_needed})
if checksum_new:
    result['MILESTONES'].append({'checksum_new': checksum_new})

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

