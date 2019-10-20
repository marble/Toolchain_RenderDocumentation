#!/usr/bin/env python

from __future__ import print_function
from __future__ import absolute_import
import tct
import sys

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
    result = tct.deepget(D, *keys, **kwdargs)
    loglist.append((keys, result))
    return result


# ==================================================
# define
# --------------------------------------------------

pass

# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    # fetch
    requirements = [
        "TheProject",
        "TheProjectMakedir",
        "documentation_folder",
        "masterdoc",
        "rebuild_needed",
    ]

    for requirement in requirements:
        v = lookup(milestones, requirement)
        if v is None:
            loglist.append("'%s' not found" % requirement)
            exitcode = 22
            reason = 'Bad PARAMS or nothing to do'
            break

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('PROBLEM with required params')


# ==================================================
# work
# --------------------------------------------------

pass


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if 0:
    result['MILESTONES'].append({'dummy': 0})

# ==================================================
# save result
# --------------------------------------------------

tct.save_the_result(result, resultfile, params, facts, milestones, exitcode, CONTINUE, reason)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
