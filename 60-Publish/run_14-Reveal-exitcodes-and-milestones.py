#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function
from __future__ import absolute_import

import os
import shutil
import sys
import tct

from os.path import join as ospj
from tct import deepget, writejson

params = tct.readjson(sys.argv[1])
facts = tct.readjson(params['factsfile'])
milestones = tct.readjson(params['milestonesfile'])
reason = ''
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

reveal_exitcodes_file = None
reveal_milestones_file = None


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    TheProjectWebroot = lookup(milestones, 'TheProjectWebroot')
    if not TheProjectWebroot:
        exitcode = 22
        reason = 'Bad PARAMS or nothing to do'

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('Bad PARAMS or nothing to do')


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:

    reveal_exitcodes = lookup(milestones, 'reveal_exitcodes')
    if reveal_exitcodes and milestones.get('tool_exitcodes_2'):
        reveal_exitcodes_file = ospj(TheProjectWebroot, 'exitcodes.json')
        writejson(milestones.get('tool_exitcodes_2'), reveal_exitcodes_file)

    reveal_milestones = lookup(milestones, 'reveal_milestones')
    if reveal_milestones:
        reveal_milestones_file = ospj(TheProjectWebroot, 'milestones.json')
        shutil.copy2(params['milestonesfile'], reveal_milestones_file)


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if reveal_exitcodes_file:
    result['MILESTONES'].append({'reveal_exitcodes_file':
                                 reveal_exitcodes_file})

if reveal_milestones_file:
    result['MILESTONES'].append({'reveal_milestones_file':
                                 reveal_milestones_file})


# ==================================================
# save result
# --------------------------------------------------

tct.save_the_result(result, resultfile, params, facts, milestones, exitcode, CONTINUE, reason)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
