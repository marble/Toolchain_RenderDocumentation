#!/usr/bin/env python

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
from __future__ import absolute_import
import os
import tct
import sys

params = tct.readjson(sys.argv[1])
facts = tct.readjson(params['factsfile'])
milestones = tct.readjson(params['milestonesfile'])
resultfile = params['resultfile']
result = tct.readjson(resultfile)
toolname = params['toolname']
toolname_pure = params['toolname_pure']
toolchain_name = facts['toolchain_name']
workdir = params['workdir']
loglist = result['loglist'] = result.get('loglist', [])
exitcode = CONTINUE = 0


# ==================================================
# Make a copy of milestones for later inspection?
# --------------------------------------------------

if 0 or milestones.get('debug_always_make_milestones_snapshot'):
    tct.make_snapshot_of_milestones(params['milestonesfile'], sys.argv[1])


# ==================================================
# Helper functions
# --------------------------------------------------

deepget = tct.deepget

def lookup(D, *keys, **kwdargs):
    result = deepget(D, *keys, **kwdargs)
    loglist.append((keys, result))
    return result


# ==================================================
# define
# --------------------------------------------------
xeq_name_cnt = 0
TheProjectMakedir = None

# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    makedir = lookup(milestones, 'makedir')
    TheProject = lookup(milestones, 'TheProject')

    if not (makedir and TheProject):
        CONTINUE = -2

if exitcode == CONTINUE:
    loglist.append('Good PARAMS - I can work with these')
else:
    loglist.append('Bad PARAMS - I cannot work with these')


# ==================================================
# work
# --------------------------------------------------

import shutil

if exitcode == CONTINUE:
    TheProjectMakedir = TheProject + 'Makedir'
    if os.path.exists(TheProjectMakedir):
        loglist.append(('Error: TheProjectMakdir should not exist', TheProjectMakedir))
        exitcode = 22

if exitcode == CONTINUE:
    srcdir = makedir.rstrip('/')
    destdir = TheProjectMakedir.rstrip('/')
    # we better only copy the top level files, no subdirs
    for top, dirs, files in os.walk(srcdir):
        dirs[:] = []
        files.sort()
        if not os.path.exists(destdir):
            os.mkdir(destdir)
        for afile in files:
            srcfile = os.path.join(top, afile)
            destfile = destdir + srcfile[len(srcdir):]
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
