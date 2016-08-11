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
    has_localization = milestones.get('has_localization', '')
    if not has_localization:
        loglist.append("Info: Nothing to do. No localization present.")
        CONTINUE = -1

# ==================================================
# work
# --------------------------------------------------

import glob
import shutil

if exitcode == CONTINUE:
    TheProject = milestones['TheProject']
    TheProjectLocalization = TheProject + 'Localization'
    if os.path.exists(TheProjectLocalization):
        errormsg = "Error: Unexpected. Folder 'TheProjectLocalization' should not exist ('%s')." % TheProjectLocalization
        loglist.append(errormsg)
        exitcode = 2

if exitcode == CONTINUE:
    if not os.path.exists(TheProjectLocalization):
        os.makedirs(TheProjectLocalization)

    pattern = TheProject + '/Documentation/Localization.*'
    loglist.append({'pattern': pattern})
    folders = glob.glob(pattern)
    loglist.append({'folders': folders})
    for folder in folders:
        shutil.move(folder, TheProjectLocalization)

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if exitcode == CONTINUE:
    result['MILESTONES'].append({'TheProjectLocalization': TheProjectLocalization})
    if folders:
        MAGIC_todolist = milestones.get('MAGIC_todolist', [])
        MAGIC_todolist_done = milestones.get('MAGIC_todolist_done', [])
        MAGIC_todolist_lastrun = milestones.get('MAGIC_todolist_lastrun', [])
        MAGIC_todolist.append({'localizations': folders})
        result['MILESTONES'].append({
            'MAGIC_todolist': MAGIC_todolist,
            'MAGIC_todolist_done': MAGIC_todolist_done,
            'MAGIC_todolist_lastrun': MAGIC_todolist_lastrun,
        })

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
