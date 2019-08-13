#!/usr/bin/env python

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
from __future__ import absolute_import

import os
import shutil
import sys
import tct

from os.path import exists as ospe, join as ospj
from tct import deepget

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

def lookup(D, *keys, **kwdargs):
    result = deepget(D, *keys, **kwdargs)
    loglist.append((keys, result))
    return result


# ==================================================
# define
# --------------------------------------------------

TheProjectMakedir = None
xeq_name_cnt = 0


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    makedir = lookup(milestones, 'makedir')
    TheProject = lookup(milestones, 'TheProject')

    if not (1
            and makedir
            and TheProject):
        CONTINUE = -2

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('Bad PARAMS or nothing to do')


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    TheProjectMakedir = TheProject + 'Makedir'

if exitcode == CONTINUE:
    srcdir = makedir.rstrip('/')
    destdir = TheProjectMakedir.rstrip('/')

    # we better only copy the top level files, no subdirs
    for top, dirs, files in os.walk(srcdir):
        dirs[:] = []
        files.sort()
        if not ospe(destdir):
            os.mkdir(destdir)
        for afile in files:
            srcfile = ospj(top, afile)
            destfile = destdir + srcfile[len(srcdir):]
            if not os.path.islink(srcfile):
                shutil.copy2(srcfile, destfile)


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if TheProjectMakedir:
    result['MILESTONES'].append({'TheProjectMakedir': TheProjectMakedir})


# ==================================================
# save result
# --------------------------------------------------

tct.save_the_result(result, resultfile, params, facts, milestones, exitcode, CONTINUE)


# ==================================================
# Return with proper exitcode
# --------------------------------------------------
sys.exit(exitcode)
