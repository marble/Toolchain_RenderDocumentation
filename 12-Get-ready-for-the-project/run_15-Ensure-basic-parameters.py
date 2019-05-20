#!/usr/bin/env python

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
from __future__ import absolute_import
import tct
import os
import sys

params = tct.readjson(sys.argv[1])
facts = tct.readjson(params['factsfile'])
milestones = tct.readjson(params['milestonesfile'])
resultfile = params['resultfile']
result = tct.readjson(resultfile)
toolname = params['toolname']
toolname_pure = params['toolname_pure']
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

makedir = ''
makedir_abspath = ''
makedir_missing = ''
talk = milestones.get('talk', 1)


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')
    toolchain_name = lookup(facts, 'toolchain_name')
    initial_working_dir = lookup(facts, 'initial_working_dir')
    if not (toolchain_name and initial_working_dir):
        exitcode = 22

if exitcode == CONTINUE:
    makedir = lookup(milestones, 'makedir')
    if not makedir:
        msg = 'Usage: tct run %s --config makedir MAKEDIR [--toolchain-help]' % toolchain_name
        loglist.append(msg)
        print(msg)
        exitcode = 22

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('PROBLEMS with params')


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    if not os.path.isabs(makedir):
        makedir = os.path.join(initial_working_dir, makedir)
    makedir = os.path.abspath(os.path.normpath(makedir))
    if not os.path.isdir(makedir):
        makedir_missing = makedir
        makedir = None
        msg = "makedir not found: %s" % makedir_missing
        loglist.append(msg)
        print(msg)
        exitcode = 22

if exitcode == CONTINUE:
    makedir_abspath = makedir
    if talk > 1:
        print('makedir:', os.path.split(makedir)[1])
        print('makedir_abspath:', makedir_abspath)

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if makedir:
    result['MILESTONES'].append({'makedir': makedir})

if makedir_abspath:
    result['MILESTONES'].append({'makedir_abspath': makedir_abspath})

if makedir_missing:
    result['MILESTONES'].append({'makedir_missing': makedir_missing})

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
