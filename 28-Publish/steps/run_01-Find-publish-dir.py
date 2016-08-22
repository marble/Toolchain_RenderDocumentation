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

known_target_folders = ['typo3cms', 'extensions']
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
    toolchain_name = facts.get('toolchain_name')
    loglist.append(('toolchain_name', toolchain_name))
    if not toolchain_name:
        exitcode = 2

if exitcode == CONTINUE:
    TheProjectResult = milestones_get('TheProjectResult')
    buildsettings_builddir = tct.deepget(milestones, 'buildsettings', 'builddir')
    loglist.append(('buildsettings_builddir', buildsettings_builddir))
    webroot_part_of_builddir = tct.deepget(facts, 'tctconfig', toolchain_name, 'webroot_part_of_builddir')
    loglist.append(('webroot_part_of_builddir', webroot_part_of_builddir))
    webroot_abspath = tct.deepget(facts, 'tctconfig', toolchain_name, 'webroot_abspath')
    loglist.append(('webroot_abspath', webroot_abspath))
    if not (TheProjectResult and buildsettings_builddir and
        webroot_part_of_builddir and webroot_abspath):
        exitcode = 2

if exitcode == CONTINUE:
    loglist.append('REQUIREMENTS satisfied')


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    if not buildsettings_builddir.startswith(webroot_part_of_builddir):
        loglist.append('target path does not start with webroot')
        exitcode = 2

if exitcode == CONTINUE:
    publish_dir_planned = webroot_abspath + buildsettings_builddir[len(webroot_part_of_builddir):]
    loglist.append(('publish_dir_planned', publish_dir_planned))
    parts = publish_dir_planned.split('/')
    if not len(parts) >= 4:
        loglist.append('publish_dir_planned too short')
        exitcode = 2

if exitcode == CONTINUE:
    if not parts[-3]  in known_target_folders:
        loglist.append('can only install to known target folders')
        loglist.append(('known_target_folders', known_target_folders))
        exitcode = 2

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
