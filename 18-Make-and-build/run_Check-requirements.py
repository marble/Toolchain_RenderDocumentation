#!/usr/bin/env python

from __future__ import print_function
from __future__ import absolute_import

import sys
import tct

from tct import deepget

params = tct.readjson(sys.argv[1])
binabspath = sys.argv[2]
facts = tct.readjson(params['factsfile'])
milestones = tct.readjson(params['milestonesfile'])
reason = ''
resultfile = params['resultfile']
result = tct.readjson(resultfile)
loglist = result['loglist'] = result.get('loglist', [])
toolname = params['toolname']
toolname_pure = params['toolname_pure']
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

def lookup(D, *keys, **kwdargs):
    result = deepget(D, *keys, **kwdargs)
    loglist.append((keys, result))
    return result


# ==================================================
# define
# --------------------------------------------------

xeq_name_cnt = 0


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    ready_for_build = lookup(milestones, 'ready_for_build')
    rebuild_needed = lookup(milestones, 'rebuild_needed')

    if not(1
            and ready_for_build
            and rebuild_needed
    ):
        exitcode = 22
        reason = 'Bad params or nothing to do'

if exitcode == CONTINUE:
    disable_include_files_check = lookup(milestones,
                                         'disable_include_files_check')
    included_files_check_is_ok = lookup(milestones,
                                        'included_files_check_is_ok')

    if not (0
            or disable_include_files_check
            or included_files_check_is_ok
    ):
        exitcode = 22
        reason = 'Bad params or nothing to do'

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('Bad PARAMS')


# ==================================================
# work
# --------------------------------------------------

pass

# ==================================================
# Set MILESTONE
# --------------------------------------------------

pass


# ==================================================
# save result
# --------------------------------------------------

tct.save_the_result(result, resultfile, params, facts, milestones, exitcode, CONTINUE, reason)


# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
