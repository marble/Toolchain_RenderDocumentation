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
loglist = result['loglist'] = result.get('loglist', [])
exitcode = CONTINUE = 0
errormsg = ''
helpmsg = ''

# ==================================================
# Check required milestone(s)
# --------------------------------------------------

if exitcode == CONTINUE:
    documentation_folder = milestones.get('documentation_folder')
    checksum_old = milestones.get('checksum_old', '')
    checksum_time = milestones.get('checksum_time')
    checksum_new = None
    checksum_file = milestones.get('checksum_file')

# ==================================================
# work
# --------------------------------------------------

import subprocess
import time

def cmdline(cmd, cwd=None):
    if cwd is None:
        cwd = os.getcwd()
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=cwd)
    out, err = process.communicate()
    exitcode = process.returncode
    return exitcode, cmd, out, err

rebuild_needed = False

if exitcode == CONTINUE:
    if documentation_folder:
        # http://unix.stackexchange.com/questions/35832/how-do-i-get-the-md5-sum-of-a-directorys-contents-as-one-sum
        theline = "find . -type f | LC_ALL=C sort | cpio -o --quiet | md5sum | awk '{ print $1 }'"
        exitcode, cmd, out, err = cmdline(theline, cwd=documentation_folder)
        loglist.append([exitcode, cmd, out, err])
        checksum_new = out.strip()
        loglist.append('checksum_old: ' + checksum_old)
        loglist.append('checksum_new: ' + checksum_new)

if exitcode == CONTINUE:

    if params.get('rebuild_needed'):
        rebuild_needed = True
        loglist.append('Rebuild is needed due to commandline parameters.')


    if checksum_time and not rebuild_needed:
        now = int(time.time())
        if (now - checksum_time) > 86400:
            rebuild_needed = True
            loglist.append('Rebuild is needed. Last build is older than a day.')

    if checksum_old and checksum_new and not rebuild_needed:
        if checksum_new != checksum_old:
            rebuild_needed = True
            loglist.append('Rebuild is needed. Checksums do not match.')

    if not checksum_old and not rebuild_needed:
        rebuild_needed = True
        loglist.append('Rebuild is needed. There is now previous checksum.')

    if not checksum_new and not rebuild_needed:
        rebuild_needed = True
        loglist.append('Rebuild is needed. There is no new checksum (Strange!?.')

    if checksum_file and checksum_new:
        if checksum_old and checksum_old == checksum_new:
            loglist.append('The new checksum is equal to the old checksum.')
        else:
            with file(checksum_file, 'wb') as f2:
                f2.write(checksum_new)
            loglist.append('New checksum written to file.')


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if exitcode == CONTINUE:
    result['MILESTONES'].append({'rebuild_needed': rebuild_needed, 'checksum_new': checksum_new})
# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)

