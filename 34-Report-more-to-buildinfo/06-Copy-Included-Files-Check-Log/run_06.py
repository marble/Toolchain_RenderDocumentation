#!/usr/bin/env python
# coding: utf-8

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
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

included_files_check_logfile = None
TheProjectResultBuildinfoCheckIncludesFile = None
xeq_name_cnt = 0


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    included_files_check_logfile = lookup(milestones, 'included_files_check_logfile')
    TheProjectResultBuildinfo = lookup(milestones, 'TheProjectResultBuildinfo')

    if not (included_files_check_logfile and TheProjectResultBuildinfo):
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
    dummy, fname = os.path.split(included_files_check_logfile)
    # Now, we could use 'fname' as name. But:
    # Since the end user is in contact with this name and we have to mention
    # it in documentation we choose a more user friendly name
    fname = 'includedFilesCheck.txt'
    TheProjectResultBuildinfoCheckIncludesFile = os.path.join(TheProjectResultBuildinfo, fname)

    shutil.copy(included_files_check_logfile, TheProjectResultBuildinfoCheckIncludesFile)

# ==================================================
# Set MILESTONE
# --------------------------------------------------
if TheProjectResultBuildinfoCheckIncludesFile:
    result['MILESTONES'].append({
        'TheProjectResultBuildinfoCheckIncludesFile':
        TheProjectResultBuildinfoCheckIncludesFile})


# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)


# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
