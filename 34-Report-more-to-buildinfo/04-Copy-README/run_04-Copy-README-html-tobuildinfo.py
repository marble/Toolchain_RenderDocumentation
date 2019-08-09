#!/usr/bin/env python
# coding: utf-8

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
from __future__ import absolute_import
import os
import tct
import sys

params = tct.readjson(sys.argv[1])
binabspath = sys.argv[2]
facts = tct.readjson(params['factsfile'])
milestones = tct.readjson(params['milestonesfile'])
resultfile = params['resultfile']
result = tct.readjson(resultfile)
loglist = result['loglist'] = result.get('loglist', [])
toolname = params['toolname']
toolname_pure = params['toolname_pure']
toolchain_name = facts['toolchain_name']
workdir = params['workdir']
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

TheProjectResultBuildinfoREADMEfile = None
xeq_name_cnt = 0


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    TheProjectLogREADMEfile = lookup(milestones, 'TheProjectLogREADMEfile')
    TheProjectResultBuildinfo = lookup(milestones, 'TheProjectResultBuildinfo')

    if not (TheProjectLogREADMEfile and TheProjectResultBuildinfo):
        CONTINUE = -2

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('Nothing to do for these params')


# ==================================================
# work
# --------------------------------------------------

import shutil

if exitcode == CONTINUE:
    dummy, fname = os.path.split(TheProjectLogREADMEfile)
    TheProjectResultBuildinfoREADMEfile = os.path.join(TheProjectResultBuildinfo, fname)

    shutil.copy(TheProjectLogREADMEfile, TheProjectResultBuildinfoREADMEfile)

# ==================================================
# Set MILESTONE
# --------------------------------------------------
if TheProjectResultBuildinfoREADMEfile:
    result['MILESTONES'].append({'TheProjectResultBuildinfoREADMEfile': TheProjectResultBuildinfoREADMEfile})


# ==================================================
# save result
# --------------------------------------------------

tct.save_the_result(result, resultfile, params, facts, milestones, exitcode, CONTINUE)


# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
