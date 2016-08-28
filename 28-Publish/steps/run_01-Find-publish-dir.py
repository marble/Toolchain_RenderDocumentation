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

known_target_folders = ['/typo3cms']
publish_dir_planned = ''
publish_package_dir_planned = ''
publish_parent_dir_planned = ''
publish_parent_parent_dir = None

# ==================================================
# Get and check required milestone(s)
# --------------------------------------------------

def milestones_get(name, default=None):
    result = milestones.get(name, default)
    loglist.append((name, result))
    return result

if exitcode == CONTINUE:
    publish_dir = None
    publish_parent_dir = None

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')
    toolchain_name = facts.get('toolchain_name')
    loglist.append(('toolchain_name', toolchain_name))
    if not toolchain_name:
        exitcode = 2

if exitcode == CONTINUE:
    TheProjectResult = milestones_get('TheProjectResult')
    buildsettings_builddir = milestones_get('buildsettings_builddir')
    webroot_part_of_builddir = milestones_get('webroot_part_of_builddir')
    webroot_abspath = milestones_get('webroot_abspath')
    relative_part_of_builddir = milestones_get('relative_part_of_builddir')
    if not (TheProjectResult and buildsettings_builddir and
        webroot_part_of_builddir and webroot_abspath and relative_part_of_builddir):
        exitcode = 2

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('PROBLEM with params')

# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    if not buildsettings_builddir.startswith(webroot_abspath):
        loglist.append('target path does not start with webroot_abspath')
        exitcode = 2

if exitcode == CONTINUE:
    publish_dir_planned = webroot_abspath + relative_part_of_builddir
    loglist.append(('publish_dir_planned', publish_dir_planned))

if exitcode == CONTINUE:
    publish_parent_dir_planned = os.path.split(publish_dir_planned)[0]
    loglist.append(('publish_parent_dir_planned', publish_parent_dir_planned))
    publish_package_dir_planned = os.path.join(publish_parent_dir_planned, 'packages')
    loglist.append(('publish_package_dir_planned', publish_package_dir_planned))

if exitcode == CONTINUE:
    publish_parent_parent_dir = os.path.split(publish_parent_dir_planned)[0]
    if not os.path.exists(publish_parent_parent_dir):
        loglist.append(('publish_parent_parent_dir does not exist', publish_parent_parent_dir))
        exitcode = 2

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if exitcode == CONTINUE:
    publish_dir_buildinfo_planned = publish_dir_planned + '/_buildinfo'
    publish_dir_pdf_planned = publish_dir_planned + '/_pdf'
    result['MILESTONES'].append({
        'publish_dir_buildinfo_planned': publish_dir_buildinfo_planned,
        'publish_dir_pdf_planned': publish_dir_pdf_planned,
        'publish_dir_planned': publish_dir_planned,
        'publish_package_dir_planned': publish_package_dir_planned,
        'publish_parent_dir_planned': publish_parent_dir_planned,
        'publish_parent_parent_dir': publish_parent_parent_dir,
    })

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------
sys.exit(exitcode)
