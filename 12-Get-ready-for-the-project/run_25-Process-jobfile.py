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
    result = tct.deepget(D, *keys, **kwdargs)
    loglist.append((keys, result))
    return result


# ==================================================
# define
# --------------------------------------------------

buildsettings_changed = False
initial_working_dir = None
jobfile_abspath = None
jobfile_data = None
xeq_name_cnt = 0


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    buildsettings = lookup(milestones, 'buildsettings')
    if not buildsettings:
        CONTINUE = -2

if exitcode == CONTINUE:
    jobfile_abspath = lookup(milestones, 'jobfile_abspath')
    jobfile = lookup(facts, 'run_command', 'jobfile')
    initial_working_dir = lookup(facts, 'initial_working_dir')
    if not (jobfile_abspath or jobfile):
        CONTINUE = -2

if exitcode == CONTINUE:
    if not jobfile_abspath:
        if os.path.isabs(jobfile):
            jobfile_abspath = jobfile
        elif initial_working_dir:
            jobfile_abspath = os.path.abspath(os.path.join(initial_working_dir, jobfile))
        else:
            CONTINUE = -2

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('PROBLEM with required params')

if CONTINUE != 0:
    loglist.append({'CONTINUE': CONTINUE})
    loglist.append('NOTHING to do')


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    jobfile_data = tct.readjson(jobfile_abspath)
    for k, v in jobfile_data.get('buildsettings', {}).items():
        buildsettings[k] = v
        buildsettings_changed = True

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if buildsettings_changed:
    result['MILESTONES'].append({'buildsettings': buildsettings})

if jobfile_data is not None:
    result['MILESTONES'].append({'jobfile_data': jobfile_data})

if jobfile_abspath is not None:
    result['MILESTONES'].append({'jobfile_abspath': jobfile_abspath})



# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
