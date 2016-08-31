#!/usr/bin/env python
# coding: utf-8

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
# define
# --------------------------------------------------

final_exitcode = None
makedir_lastrun_folder = None

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

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')
    workdir_home = params_get('workdir_home')
    makedir = milestones_get('makedir')
    if not (workdir_home and makedir):
        exitcode = 2

# ==================================================
# work
# --------------------------------------------------

import shutil

if exitcode == CONTINUE:
    srcdir = workdir_home.rstrip('/')
    makedir_lastrun_folder = os.path.join(makedir, 'temp_lastrun_' + facts['toolchain_name'])
    if os.path.isdir(makedir_lastrun_folder):
        shutil.rmtree(makedir_lastrun_folder)
    for top, dirs, files in os.walk(srcdir):
        current_dir = makedir_lastrun_folder + top[len(srcdir):]
        for afile in files:
            fext = os.path.splitext(afile)[1]
            if not fext in ['.json', '.txt']:
                continue
            if afile.startswith('params_'):
                continue
            srcfile = os.path.join(top, afile)
            destfile = makedir_lastrun_folder + srcfile[len(srcdir):]
            if not os.path.exists(current_dir):
                os.makedirs(current_dir)
            shutil.copy(srcfile, destfile)

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if makedir_lastrun_folder:
    result['MILESTONES'].append({'makedir_lastrun_folder': makedir_lastrun_folder})

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
