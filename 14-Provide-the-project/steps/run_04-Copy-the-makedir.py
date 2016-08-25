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
    makedir = milestones.get('makedir')
    loglist.append(['makedir', makedir])
    TheProject = milestones.get('TheProject')
    loglist.append(['TheProject', TheProject])

    if not (makedir and TheProject):
        CONTINUE = -1

# ==================================================
# work
# --------------------------------------------------

from shutil import copytree

if exitcode == CONTINUE:
    TheProjectMakedir = TheProject + 'Makedir'
    if os.path.exists(TheProjectMakedir):
        errormsg = "Error: Unexpected. Folder 'TheProjectMakdir' should not exist ('%s')." % TheProjectMakedir
        loglist.append(errormsg)
        exitcode = 2

if exitcode == CONTINUE:

    from shutil import copytree

    source = makedir
    destination = TheProjectMakedir
    copytree(source, destination)

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if exitcode == CONTINUE:
    result['MILESTONES'].append({'TheProjectMakedir': TheProjectMakedir})

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
