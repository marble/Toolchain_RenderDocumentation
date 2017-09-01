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

# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    TheProjectMakedir = lookup(milestones, 'TheProjectMakedir')
    if not (TheProjectMakedir):
        exitcode = 22

if exitcode == CONTINUE:
    loglist.append('Good PARAMS - I can work with these')
else:
    loglist.append('Bad PARAMS - I cannot work with these')

if exitcode == CONTINUE:
    fpath_buildsettings_sh = lookup(facts, 'run_command', 'buildsettings_sh')
    fpath_overrides_cfg = lookup(facts, 'run_command', 'overrides_cfg')
    if not (fpath_buildsettings_sh or fpath_overrides_cfg):
        CONTINUE = -2
        loglist.append('Nothing to do.')

# ==================================================
# work
# --------------------------------------------------

import shutil

if exitcode == CONTINUE:

    if fpath_buildsettings_sh:
        destfile = os.path.join(TheProjectMakedir, 'buildsettings.sh')
        shutil.copy(fpath_buildsettings_sh, destfile)
        loglist.append(('copy file',
                        ('from: %s' % fpath_buildsettings_sh,
                         'to: %s' % destfile)))

    if fpath_overrides_cfg:
        destfile = os.path.join(TheProjectMakedir, 'Overrides.cfg')
        shutil.copy(fpath_overrides_cfg, destfile)
        loglist.append(('copy file',
                        ('from: %s' % fpath_overrides_cfg,
                         'to: %s' % destfile)))

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if 0:
    result['MILESTONES'].append({'name': 'value'})


# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)


# ==================================================
# Return with proper exitcode
# --------------------------------------------------
sys.exit(exitcode)
