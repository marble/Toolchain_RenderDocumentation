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
    gitdir_ready = milestones.get('gitdir_ready', '')
    if not gitdir_ready:
        errormsg = "Error: milestone 'gitdir_ready' not found."
        loglist.append(errormsg)
        exitcode = 2

# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    makedir = milestones.get('makedir')
    buildsettings = milestones.get('buildsettings')

    gitdir = buildsettings['gitdir']
    locations = [
        'Documentation/Index.rst',
        'Documentation/index.rst',
        'Documentation/Index.md',
        'Documentation/index.md',
        'README.rst',
        'README.md',
    ]
    loglist.append({'locations': locations})
    masterdocs = {}
    for location in locations:
        fpath = os.path.join(gitdir, location)
        if os.path.exists(fpath):
            masterdocs[location] = True
    loglist.append({'masterdocs':masterdocs})


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if exitcode == CONTINUE:
    if len(masterdocs):
        result['MILESTONES'].append({'has_documentation': 1})

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
