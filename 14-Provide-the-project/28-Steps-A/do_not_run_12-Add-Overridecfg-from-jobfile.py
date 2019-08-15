#!/usr/bin/env python

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
from __future__ import absolute_import
import os
import tct
import sys

# specific
import codecs
import six.moves.configparser
import shutil

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
    jobfile_data = lookup(milestones, 'jobfile_data')
    if not (TheProjectMakedir and jobfile_data):
        CONTINUE = -2

if exitcode == CONTINUE:
    override_data = jobfile_data.get('Overrides_cfg')
    if not override_data:
        CONTINUE = -2

if exitcode == CONTINUE:
    loglist.append('PARAMS are good')
else:
    loglist.append('Bad PARAMS or nothing to do')


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:

    loglist.append('Start with empty config object')
    override_data_result = six.moves.configparser.RawConfigParser()

    destfile = os.path.join(TheProjectMakedir, 'Overrides.cfg')
    if os.path.exists(destfile):
        shutil.copy(destfile, destfile + '.original')
        loglist.append('Add data from existing TheProjectMakedir/Overrides.cfg')
        with codecs.open(destfile, 'r', 'utf-8') as f1:
            override_data_result.readfp(f1)

    loglist.append('Overwrite with data from jobfile')
    for k_section, v_section in sorted(override_data.items()):
        if not override_data_result.has_section(k_section):
            override_data_result.add_section(k_section)
        for k in sorted(v_section.keys()):
            v = v_section[k]
            override_data_result.set(k_section, k, v)

    loglist.append('Save as TheProjectMakedir/Overrides.cfg')
    with codecs.open(destfile, 'w', 'utf-8') as f2:
        override_data_result.write(f2)

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if 0:
    result['MILESTONES'].append({'name': 'value'})


# ==================================================
# save result
# --------------------------------------------------

tct.save_the_result(result, resultfile, params, facts, milestones, exitcode, CONTINUE)


# ==================================================
# Return with proper exitcode
# --------------------------------------------------
sys.exit(exitcode)
