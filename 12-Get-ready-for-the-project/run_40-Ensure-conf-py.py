#!/usr/bin/env python

from __future__ import print_function
from __future__ import absolute_import
import os
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
# Get and check required milestone(s)
# --------------------------------------------------

def milestones_get(name, default=None):
    result = milestones.get(name, default)
    loglist.append((name, result))
    return result

def facts_get(name, default=None):
    result = facts.get(name, default)
    loglist.append((name, result))
    return result

def params_get(name, default=None):
    result = params.get(name, default)
    loglist.append((name, result))
    return result

# ==================================================
# define
# --------------------------------------------------

conf_py_file = ''
conf_py_masterfile = milestones_get('conf_py_masterfile')
conf_py_symlink_created = 0
xeq_name_cnt = 0


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    makedir_abspath = milestones_get('makedir_abspath')
    if not makedir_abspath:
        CONTINUE = -2

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('PROBLEM with required params')


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    conf_py_file = os.path.join(makedir_abspath, 'conf.py')
    if os.path.exists(conf_py_file):
        CONTINUE = -2
    else:
        conf_py_file = ''

if exitcode == CONTINUE:
    if conf_py_masterfile:
        conf_py_file = os.path.join(makedir_abspath, 'conf.py')
        try:
            os.link(conf_py_masterfile, conf_py_file)
            conf_py_symlink_created = 1
        except OSError:
            conf_py_file = ''

if exitcode == CONTINUE:
    if not os.path.exists(conf_py_file):
        loglist.append(('conf.py not found in makedir', makedir_abspath))
        printerror = print
        printerror('conf.py is missing in makedir ' + makedir_abspath)
        CONTINUE = -2


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if conf_py_file:
    result['MILESTONES'].append({'conf_py_file': conf_py_file})

if conf_py_symlink_created:
    result['MILESTONES'].append({'conf_py_symlink_created': conf_py_symlink_created})


# ==================================================
# save result
# --------------------------------------------------

tct.save_the_result(result, resultfile, params, facts, milestones, exitcode, CONTINUE, reason)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
