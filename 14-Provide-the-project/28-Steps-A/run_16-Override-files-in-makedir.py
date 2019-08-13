#!/usr/bin/env python

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
from __future__ import absolute_import

import codecs
import json
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

fpath_buildsettings_sh = None
fpath_overrides_cfg = None
settings_json_file_2 = None
xeq_name_cnt = 0


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    TheProjectMakedir = lookup(milestones, 'TheProjectMakedir')
    if not TheProjectMakedir:
        exitcode = 22

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('Bad PARAMS or nothing to do')


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:

    # looks like a candidate to be deprecated
    fpath_buildsettings_sh = lookup(facts, 'run_command', 'buildsettings_sh')
    if fpath_buildsettings_sh:
        destfile = ospj(TheProjectMakedir, 'buildsettings.sh')
        shutil.copy2(fpath_buildsettings_sh, destfile)

    fpath_overrides_cfg = lookup(facts, 'run_command', 'overrides_cfg')
    if fpath_overrides_cfg:
        destfile = os.path.join(TheProjectMakedir, 'Overrides.cfg')
        shutil.copy2(fpath_overrides_cfg, destfile)

    # save jobfile_data['Overrides_cfg'] as 'MAKEDIR/Settings.json'
    settings_json_data = lookup(milestones, 'jobfile_data', 'Overrides_cfg')
    if settings_json_data:
        settings_json_data['COMMENT'] = ("This is what we found in"
                                         " jobfile_data['Overrides']")
        settings_json_file_2 = ospj(TheProjectMakedir, 'Settings.json')
        if ospe(settings_json_file_2):
            os.rename(settings_json_file_2, settings_json_file_2 + '.original')
        with codecs.open(settings_json_file_2, 'w', 'utf-8') as f2:
            json.dump(settings_json_data, f2, indent=4, sort_keys=True)


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if fpath_buildsettings_sh: result['MILESTONES'].append(
    {'fpath_buildsettings_sh': 'fpath_buildsettings_sh'})

if fpath_overrides_cfg: result['MILESTONES'].append(
    {'fpath_overrides_cfg': 'fpath_overrides_cfg'})

if settings_json_file_2: result['MILESTONES'].append(
    {'settings_json_file_2': 'settings_json_file_2'})

# ==================================================
# save result
# --------------------------------------------------

tct.save_the_result(result, resultfile, params, facts, milestones, exitcode, CONTINUE)


# ==================================================
# Return with proper exitcode
# --------------------------------------------------
sys.exit(exitcode)
