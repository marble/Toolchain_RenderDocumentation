#!/usr/bin/env python

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
import os
import tct
import sys
import shutil

params = tct.readjson(sys.argv[1])
binabspath = sys.argv[2]
facts = tct.readjson(params['factsfile'])
milestones = tct.readjson(params['milestonesfile'])
resultfile = params['resultfile']
result = tct.readjson(resultfile)
loglist = result['loglist'] = result.get('loglist', [])
toolname = params["toolname"]
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

publish_dir = ''
publish_dir_buildinfo = ''
publish_html_done = False
publish_parent_dir = ''
publish_parent_parent_dir = ''
publish_removed_old = False
xeq_name_cnt = 0


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    # required milestones
    requirements = []

    # just test
    for requirement in requirements:
        v = milestones_get(requirement)
        if not v:
            loglist.append("'%s' not found" % requirement)
            exitcode = 22

    # fetch
    publish_dir_planned = milestones_get('publish_dir_planned')
    publish_parent_dir_planned = milestones_get('publish_parent_dir_planned')
    publish_parent_parent_dir_planned = milestones_get('publish_parent_parent_dir_planned')
    TheProjectResult = milestones_get('TheProjectResult')
    TheProjectResultVersion = milestones_get('TheProjectResultVersion')

    # test
    if not (
        publish_dir_planned and
        publish_parent_dir_planned and
        publish_parent_parent_dir_planned and
        TheProjectResult and
        TheProjectResultVersion):
        exitcode = 22

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('PROBLEMS with params')

if CONTINUE != 0:
    loglist.append({'CONTINUE': CONTINUE})
    loglist.append('NOTHING to do')


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:

    if not os.path.exists(publish_parent_parent_dir_planned):
        os.makedirs(publish_parent_parent_dir_planned)
    publish_parent_parent_dir = publish_parent_parent_dir_planned

    if not os.path.exists(publish_parent_dir_planned):
        os.mkdir(publish_parent_dir_planned)
    publish_parent_dir = publish_parent_dir_planned

    if os.path.isdir(publish_dir_planned):
        shutil.rmtree(publish_dir_planned)
        publish_removed_old = True

    # should not happen
    if os.path.exists(publish_dir_planned):
        os.remove(publish_dir_planned)

    if os.path.exists(publish_dir_planned):
        loglist.append(('cannot remove `publish_dir_planned`', publish_dir_planned))
        publish_removed_old = False
        exitcode = 22

if exitcode == CONTINUE:
    # move our new build in place
    shutil.move(TheProjectResultVersion, publish_dir_planned)
    publish_dir = publish_dir_planned
    if not os.path.isdir(publish_dir):
        loglist.append(('cannot move build to `publish_dir`', publish_dir))
        exitcode = 22

if exitcode == CONTINUE:
    publish_html_done = True
    publish_dir_buildinfo_planned = milestones_get('publish_dir_buildinfo_planned')
    if publish_dir_buildinfo_planned and os.path.isdir(publish_dir_buildinfo_planned):
        publish_dir_buildinfo = publish_dir_buildinfo_planned


# ==================================================
# Set MILESTONE
# --------------------------------------------------

D = {}

if publish_html_done:
    D['publish_html_done'] = publish_html_done

if publish_removed_old:
    D['publish_removed_old'] = publish_removed_old

if publish_parent_dir:
    D['publish_parent_dir'] = publish_parent_dir

if publish_parent_parent_dir:
    D['publish_parent_parent_dir'] = publish_parent_parent_dir

if publish_dir:
    D['publish_dir'] = publish_dir

if publish_dir_buildinfo:
    D['publish_dir_buildinfo'] = publish_dir_buildinfo

if D:
    result['MILESTONES'].append(D)

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)


# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
