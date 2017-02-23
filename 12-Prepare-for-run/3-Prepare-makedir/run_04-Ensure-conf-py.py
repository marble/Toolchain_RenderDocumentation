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
workdir = params['workdir']
loglist = result['loglist'] = result.get('loglist', [])
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

xeq_name_cnt = 0
conf_py_file = None
conf_py_masterfile = None


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')
    makedir_abspath = milestones_get('makedir_abspath')
    if not makedir_abspath:
        CONTINUE = -1

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('PROBLEM with params')

if exitcode == CONTINUE:
    conf_py_masterfile = milestones_get('conf_py_masterfile')


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    conf_py_file = os.path.join(makedir_abspath, 'conf.py')
    loglist.append(('conf_py_file', conf_py_file))
    if os.path.exists(conf_py_file):
        loglist.append('Ok, conf.py exists')
        CONTINUE = -1
    else:
        loglist.append('Oops, conf.py is missing')

if exitcode == CONTINUE:
    if conf_py_masterfile:
        try:
            os.link(conf_py_masterfile, conf_py_file)
            loglist.append('create symlink to masterfile')
        except OSError:
            loglist.append('OSError on create symlink')

if exitcode == CONTINUE:
    if not os.path.exists(conf_py_file):
        printerror = print
        printerror('conf.py is missing')
        exitcode = 2


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if conf_py_file:
    result['MILESTONES'].append({'conf_py_file': conf_py_file})

if conf_py_masterfile:
    result['MILESTONES'].append({'conf_py_masterfile': conf_py_masterfile})

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
