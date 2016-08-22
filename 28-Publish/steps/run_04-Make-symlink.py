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

publish_html_htaccess_copied = None
publish_html_remove_latest_file = False
publish_latest_file_target_old = None
publish_stable_file = None
publish_stable_file_created = False

# ==================================================
# Get and check required milestone(s)
# --------------------------------------------------

def milestones_get(name, default=None):
    result = milestones.get(name, default)
    loglist.append((name, result))
    return result

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')
    toolname_name = facts.get('toolchain_name')
    if not toolname_name:
        exitcode = 2

if exitcode == CONTINUE:
    publish_dir = milestones_get('publish_dir')
    publish_parent_dir = milestones_get('publish_parent_dir')
    publish_html_done = milestones_get('publish_html_done')

    htaccess_template_show_latest = tct.deepget(facts, 'tctconfig', toolname_name, 'htaccess_template_show_latest')
    loglist.append(('htaccess_template_show_latest', htaccess_template_show_latest))

if exitcode == CONTINUE:
    if not (publish_dir and publish_parent_dir and publish_html_done
            and htaccess_template_show_latest):
        exitcode = 2

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')

if exitcode == CONTINUE:
    ter_extension = tct.deepget(milestones, 'buildsettings', 'ter_extension')
    loglist.append(('ter_extension', ter_extension))

# ==================================================
# work
# --------------------------------------------------

import shutil

if exitcode == CONTINUE:
    # provide .htaccess
    htaccess_file = os.path.join(publish_parent_dir, '.htaccess')
    if not os.path.exists(htaccess_file):
        shutil.copy(htaccess_template_show_latest, htaccess_file)
        publish_html_htaccess_copied = htaccess_file

if exitcode == CONTINUE:
    # remove 'latest' if not dir
    latest_file = os.path.join(publish_parent_dir, 'latest')
    if os.path.islink(latest_file):
        publish_latest_file_target_old = os.readlink(latest_file)
    if os.path.isfile(latest_file):
        os.remove(latest_file)
        publish_html_remove_latest_file = True

if exitcode == CONTINUE:
    # find existing versions
    publish_existing_versions = []
    for top, dirs, files in os.walk(publish_parent_dir):
        for dir in dirs:
            if dir[0] in '0123456789':
                publish_existing_versions.append(dir)
        dirs[:] = [] # stop recursion
    publish_existing_versions.sort(key=tct.versiontuple, reverse=True)

if exitcode == CONTINUE:
    if ter_extension:
        # for extensions 'stable' should always point to the highest
        # version denoted by numbers
        publish_stable_file = os.path.join(publish_parent_dir, 'stable')
        if os.path.islink(publish_stable_file):
            os.remove(publish_stable_file)
        if publish_existing_versions:
            os.symlink(publish_existing_versions[0], publish_stable_file)
            publish_stable_file_created = publish_stable_file

if exitcode == CONTINUE:
    if not ter_extension:
        if os.path.islink(publish_stable_file):
            # handled manually
            pass
        else:
            if os.path.exists(latest_file):
                os.symlink('latest', publish_stable_file)
                publish_stable_file_created = publish_stable_file
            elif publish_existing_versions:
                os.symlink(publish_existing_versions[0], publish_stable_file)
                publish_stable_file_created = publish_stable_file


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if publish_html_htaccess_copied:
    result['MILESTONES'].append({'publish_html_htaccess_copied': publish_html_htaccess_copied})

if publish_html_remove_latest_file:
    result['MILESTONES'].append({'publish_html_remove_latest_file': publish_html_remove_latest_file})

if publish_latest_file_target_old:
    result['MILESTONES'].append({'publish_latest_file_target_old': publish_latest_file_target_old})

if publish_stable_file_created:
    result['MILESTONES'].append({'publish_stable_file_created': publish_stable_file_created})


# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
