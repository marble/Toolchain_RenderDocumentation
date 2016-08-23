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
toolfolderabspath = params["toolfolderabspath"]
loglist = result['loglist'] = result.get('loglist', [])
exitcode = CONTINUE = 0

# ==================================================
# Check required milestone(s)
# --------------------------------------------------
def milestones_get(name, default=None):
    result = milestones.get(name, default)
    loglist.append((name, result))
    return result

if exitcode == CONTINUE:
    TheProjectResultVersion = milestones_get('TheProjectResultVersion')

if not (TheProjectResultVersion):
    exitcode = 2

# ==================================================
# work
# --------------------------------------------------

import shutil

if exitcode == CONTINUE:
    TheProjectResultBuildinfo = os.path.join(TheProjectResultVersion, '_buildinfo')
    if not os.path.exists(TheProjectResultBuildinfo):
        os.makedirs(TheProjectResultBuildinfo)

if exitcode == CONTINUE:
    src = os.path.join(toolfolderabspath, '_htaccess.to-be-copied.txt')
    dest = os.path.join(TheProjectResultBuildinfo, '.htaccess')
    shutil.copy(src, dest)

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if exitcode == CONTINUE:
    result['MILESTONES'].append({'TheProjectResultBuildinfo': TheProjectResultBuildinfo})

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
