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
# define
# --------------------------------------------------

xeq_name_cnt = 0

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
    masterdocs_initial = milestones_get('masterdocs_initial')
    gitdir = tct.deepget(milestones, 'buildsettings', 'gitdir')
    if not (workdir_home and masterdocs_initial and gitdir):
        exitcode = 2

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('PROBLEMS with params')

# ==================================================
# work
# --------------------------------------------------


from shutil import copytree, ignore_patterns, copyfile

if exitcode == CONTINUE:
    TheProject = os.path.join(workdir_home, 'TheProject')
    if os.path.exists(TheProject):
        loglist.append("TheProject already exists: %s" % TheProject)
        exitcode = 2

if exitcode == CONTINUE:
    os.mkdir(TheProject)

if exitcode == CONTINUE:
    for top, dirs, files in os.walk(gitdir):
        for afile in files:
            copyfile(os.path.join(top, afile), os.path.join(TheProject, afile))
        for adir in dirs:
            if adir in ['docs', 'Documentation']:
                copytree(os.path.join(top, adir), os.path.join(TheProject, adir))
        break

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if exitcode == CONTINUE:
    result['MILESTONES'].append({'TheProject': TheProject})

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
