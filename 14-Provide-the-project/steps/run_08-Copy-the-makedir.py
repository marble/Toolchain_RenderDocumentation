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
TheProjectMakedir = None

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
    makedir = milestones_get('makedir')
    TheProject = milestones_get('TheProject')

    if not (makedir and TheProject):
        loglist.append('SKIPPING')
        CONTINUE = -1

# ==================================================
# work
# --------------------------------------------------

import shutil

if exitcode == CONTINUE:
    TheProjectMakedir = TheProject + 'Makedir'
    if os.path.exists(TheProjectMakedir):
        loglist.append(('Error: TheProjectMakdir should not exist', TheProjectMakedir))
        exitcode = 2

if exitcode == CONTINUE:
    srcdir = makedir.rstrip('/')
    destdir = TheProjectMakedir.rstrip('/')
    # we better only copy the top level files, no subdirs
    for top, dirs, files in os.walk(srcdir):
        dirs[:] = []
        files.sort()
        for afile in files:
            srcfile = os.path.join(top, afile)
            destfile = destdir + '/' + srcfile[len(srcdir):]
            shutil.copy(srcfile, destfile)

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if TheProjectMakedir:
    result['MILESTONES'].append({'TheProjectMakedir': TheProjectMakedir})

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
