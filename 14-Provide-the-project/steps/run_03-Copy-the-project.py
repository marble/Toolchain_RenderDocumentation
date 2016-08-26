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

# ==================================================
# Check required milestone(s)
# --------------------------------------------------

if exitcode == CONTINUE:
    masterdocs = milestones.get('masterdocs')
    if not masterdocs:
        exitcode = 2

# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    buildsettings = milestones['buildsettings']
    gitdir = buildsettings['gitdir']

from shutil import copytree, ignore_patterns

if exitcode == CONTINUE:
    TheProject = os.path.join(params['workdir_home'], 'TheProject')
    if os.path.exists(TheProject):
        errormsg = "Error: Unexpected. Folder 'TheProject' should not exist ('%s')." % TheProject
        loglist.append(errormsg)
        exitcode = 2

if exitcode == CONTINUE:
    source = gitdir
    destination = TheProject
    copytree(source, destination, ignore=ignore_patterns('.git','.idea','*.pyc'))


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if exitcode == CONTINUE:
    result['MILESTONES'].append({'TheProject': TheProject})

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
