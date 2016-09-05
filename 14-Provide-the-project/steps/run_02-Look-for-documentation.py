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
masterdocs_initial = {}
masterdoc_candidates = [
    'Documentation/Index.rst',
    'Documentation/index.rst',
    'Documentation/Index.md',
    'Documentation/index.md',
    'README.rst',
    'README.md',
    'doc/manual.pdf',
    'doc/manual.sxw',
]

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
    gitdir = tct.deepget(milestones, 'buildsettings', 'gitdir')
    if not gitdir:
        exitcode = 2

# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append({'masterdoc_candidates': masterdoc_candidates})
    for candidate in masterdoc_candidates:
        fpath = os.path.join(gitdir, candidate)
        if os.path.exists(fpath):
            masterdocs_initial[candidate] = True
        else:
            masterdocs_initial[candidate] = False

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if masterdoc_candidates:
    result['MILESTONES'].append({
        'masterdoc_candidates': masterdoc_candidates,
    })

if masterdocs_initial:
    result['MILESTONES'].append({
        'masterdocs_initial': masterdocs_initial,
    })

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------
sys.exit(exitcode)
