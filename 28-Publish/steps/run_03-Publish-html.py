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
loglist = result['loglist'] = result.get('loglist', [])
exitcode = CONTINUE = 0

# ==================================================
# define
# --------------------------------------------------

publish_html_done = False
publish_removed_old = False
publish_dir = ''
publish_dir_buildinfo = ''
publish_parent_dir = ''

# ==================================================
# Get and check required milestone(s)
# --------------------------------------------------

def milestones_get(name, default=None):
    result = milestones.get(name, default)
    loglist.append((name, result))
    return result

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

if exitcode == CONTINUE:
    TheProjectResult = milestones_get('TheProjectResult')
    TheProjectResultVersion = milestones_get('TheProjectResultVersion')
    publish_dir_planned = milestones_get('publish_dir_planned')
    publish_parent_dir_planned = milestones_get('publish_parent_dir_planned')
    publish_parent_parent_dir = milestones_get('publish_parent_parent_dir')

if not (publish_dir_planned and publish_parent_dir_planned and
        publish_parent_parent_dir and
        TheProjectResult and TheProjectResultVersion):
    exitcode = 2
    loglist.append(('PROBLEM with params'))

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')

# ==================================================
# work
# --------------------------------------------------

import shutil

if exitcode == CONTINUE:
    if not os.path.exists(publish_parent_dir_planned):
        os.mkdir(publish_parent_dir_planned)

if exitcode == CONTINUE:
    publish_parent_dir = publish_parent_dir_planned
    if exitcode == CONTINUE:
        if os.path.isdir(publish_dir_planned):
            shutil.rmtree(publish_dir_planned)
            publish_removed_old = True
    elif os.path.exists(publish_dir_planned):
        os.remove(publish_dir_planned)
    if os.path.exists(publish_dir_planned):
        loglist.append('cannot remove old publish_dir_planned')
        publish_removed_old = False
        exitcode = 2

if exitcode == CONTINUE:
    os.rename(TheProjectResultVersion, publish_dir_planned)
    publish_dir = publish_dir_planned
    if not os.path.isdir(publish_dir):
        loglist.append('cannot rename result to publish_dir')
        exitcode = 2

if exitcode == CONTINUE:
    publish_html_done = True
    publish_dir_buildinfo_planned = milestones_get('publish_dir_buildinfo_planned')
    if publish_dir_buildinfo_planned and os.path.isdir(publish_dir_buildinfo_planned):
        publish_dir_buildinfo = publish_dir_buildinfo_planned




# ==================================================
# Set MILESTONE
# --------------------------------------------------

if publish_html_done:
    result['MILESTONES'].append({'publish_html_done': publish_html_done})

if publish_removed_old:
    result['MILESTONES'].append({'publish_removed_old': publish_removed_old})

if publish_parent_dir:
    result['MILESTONES'].append({'publish_parent_dir': publish_parent_dir})

if publish_dir:
    result['MILESTONES'].append({'publish_dir': publish_dir})

if publish_dir_buildinfo:
    result['MILESTONES'].append({'publish_dir_buildinfo': publish_dir_buildinfo})

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------
sys.exit(exitcode)
