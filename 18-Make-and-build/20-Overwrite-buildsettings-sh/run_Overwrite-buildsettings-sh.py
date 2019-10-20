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

buildsettings = {}
buildsettings_file = ''
xeq_name_cnt = 0

# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    buildsettings_file = lookup(milestones, 'buildsettings_file')
    buildsettings = lookup(milestones, 'buildsettings')

    if not buildsettings_file and buildsettings:
        exitcode = 99
        reason = 'Bad params or nothing to do'

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('Bad PARAMS or nothing to do')


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    with open(buildsettings_file, 'wb') as f2:
        for k in sorted(buildsettings.keys()):
            f2.write('%s=%s\n' % (k.upper(), buildsettings[k]))


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
