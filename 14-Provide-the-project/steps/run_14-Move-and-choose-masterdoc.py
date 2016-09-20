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
masterdoc = None
documentation_folder_created = None
documentation_folder = None

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
    TheProject = milestones_get('TheProject')
    masterdoc_candidates = milestones_get('masterdoc_candidates')
    if not (TheProject and masterdoc_candidates):
        exitcode = 2

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('PROBLEMS with params')

if exitcode == CONTINUE:
    workdir_home = params_get('workdir_home')
    masterdocs_initial = milestones.get('masterdocs_initial')
    gitdir = tct.deepget(milestones, 'buildsettings', 'gitdir', default='GITDIR')
    localization = tct.deepget(milestones, 'buildsettings', 'localization', default='LOCALIZATION')
    documentation_folder = milestones_get('documentation_folder')

# ==================================================
# work
# --------------------------------------------------

import shutil

if exitcode == CONTINUE:
    for candidate in masterdoc_candidates:
        fpath = os.path.join(TheProject, candidate)
        if os.path.exists(fpath):
            masterdoc = fpath
            break
    else:
        candidate = None
        masterdoc = None

if exitcode == CONTINUE and masterdoc and candidate:

    if candidate.lower().startswith('documentation/index.'):
        pass

    elif candidate.lower().startswith('readme.'):
        fpath, fext = os.path.splitext(candidate)
        source = masterdoc
        if not documentation_folder:
            documentation_folder = os.path.join(TheProject, 'Documentation')
            os.mkdir(documentation_folder)
            documentation_folder_created = documentation_folder
        masterdoc = os.path.join(documentation_folder, 'Index' + fext)
        shutil.copyfile(source, masterdoc)

    elif masterdoc.lower().startswith('docs/'):
        # not yet implemented
        masterdoc = None

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if masterdoc:
    result['MILESTONES'].append({'masterdoc': masterdoc})

if documentation_folder_created:
    result['MILESTONES'].append({'documentation_folder_created': documentation_folder_created})

if documentation_folder:
    result['MILESTONES'].append({'documentation_folder': documentation_folder})


# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
