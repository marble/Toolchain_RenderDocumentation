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
toolname_short = os.path.splitext(toolname)[0][4:]  # run_01-Name.py -> 01-Name
workdir = params['workdir']
loglist = result['loglist'] = result.get('loglist', [])
exitcode = CONTINUE = 0

# ==================================================
# define
# --------------------------------------------------

xeq_name_cnt = 0
masterdocs = {}

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
    masterdoc_candidates = [
        'Documentation/Index.rst',
        'Documentation/index.rst',
        'Documentation/Index.md',
        'Documentation/index.md',
        #'README.rst',
        #'README.md',
        #'doc/manual.pdf',
        #'doc/manual.sxw',
    ]
    loglist.append({'masterdoc_candidates': masterdoc_candidates})
    masterdocs = {}
    for candidate in masterdoc_candidates:
        fpath = os.path.join(gitdir, candidate)
        if os.path.exists(fpath):
            masterdocs[candidate] = 'found'

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if exitcode == CONTINUE:
    result['MILESTONES'].append({
        'masterdocs': masterdocs})

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
