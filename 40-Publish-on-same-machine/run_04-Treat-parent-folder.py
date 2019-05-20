#!/usr/bin/env python

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
from __future__ import absolute_import
import os
import tct
import sys
import shutil

params = tct.readjson(sys.argv[1])
facts = tct.readjson(params['factsfile'])
milestones = tct.readjson(params['milestonesfile'])
resultfile = params['resultfile']
result = tct.readjson(resultfile)
toolname = params['toolname']
toolname_pure = params['toolname_pure']
toolchain_name = facts['toolchain_name']
workdir = params['workdir']
loglist = result['loglist'] = result.get('loglist', [])
exitcode = CONTINUE = 0

# This tool is about creating an .htaccess file.
# We turn that step off.
# This needs to be done by the final publisher.

CONTINUE = -2

# ==================================================
# Make a copy of milestones for later inspection?
# --------------------------------------------------

if 0 or milestones.get('debug_always_make_milestones_snapshot'):
    tct.make_snapshot_of_milestones(params['milestonesfile'], sys.argv[1])


# ==================================================
# Helper functions
# --------------------------------------------------

deepget = tct.deepget

def lookup(D, *keys, **kwdargs):
    result = deepget(D, *keys, **kwdargs)
    loglist.append((keys, result))
    return result


# ==================================================
# define
# --------------------------------------------------

publish_html_htaccess_copied = None
publish_html_remove_latest_file = False
publish_latest_file_target_old = None
publish_stable_file = None
publish_stable_file_created = False
ter_extension = None
xeq_name_cnt = 0


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    configset = lookup(milestones, 'configset')
    publish_dir = lookup(milestones, 'publish_dir')
    publish_html_done = lookup(milestones, 'publish_html_done')
    publish_project_dir = lookup(milestones, 'publish_project_dir')
    if not (configset and publish_dir and publish_html_done and publish_project_dir):
        CONTINUE = -2

if exitcode == CONTINUE:
    htaccess_template_show_latest = lookup(facts, 'tctconfig', configset, 'htaccess_template_show_latest')
    if not htaccess_template_show_latest:
        CONTINUE = -2

if exitcode == CONTINUE:
    if not os.path.exists(htaccess_template_show_latest):
        loglist.append('htaccess_template_show_latest does not exist')
        exitcode = 1

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('Bad PARAMS or nothing to do')

# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    ter_extension = int(tct.deepget(milestones, 'buildsettings', 'ter_extension'))
    loglist.append(('ter_extension', ter_extension))


if exitcode == CONTINUE:
    # provide .htaccess
    htaccess_file = os.path.join(publish_project_dir, '.htaccess')
    if not os.path.exists(htaccess_file):
        shutil.copy(htaccess_template_show_latest, htaccess_file)
        publish_html_htaccess_copied = htaccess_file

if exitcode == CONTINUE:
    # remove 'latest' if not dir
    latest_file = os.path.join(publish_project_dir, 'latest')
    if os.path.islink(latest_file):
        publish_latest_file_target_old = os.readlink(latest_file)
    if os.path.isfile(latest_file):
        os.remove(latest_file)
        publish_html_remove_latest_file = True

if exitcode == CONTINUE:
    # find existing versions
    publish_existing_versions = []
    for top, dirs, files in os.walk(publish_project_dir):
        for dir in dirs:
            if dir[0] in '0123456789':
                publish_existing_versions.append(dir)
        dirs[:] = [] # stop recursion
    publish_existing_versions.sort(key=tct.versiontuple, reverse=True)

if exitcode == CONTINUE:
    publish_stable_file = os.path.join(publish_project_dir, 'stable')
    if ter_extension:
        # for extensions 'stable' should always point to the highest
        # version denoted by numbers
        if os.path.islink(publish_stable_file):
            os.remove(publish_stable_file)
        if publish_existing_versions:
            os.symlink(publish_existing_versions[0], publish_stable_file)
            publish_stable_file_created = publish_stable_file
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

NM = new_milestones = {}

if publish_html_htaccess_copied:
    NM['publish_html_htaccess_copied'] = publish_html_htaccess_copied

if publish_html_remove_latest_file:
    NM['publish_html_remove_latest_file'] = publish_html_remove_latest_file

if publish_latest_file_target_old:
    NM['publish_latest_file_target_old'] = publish_latest_file_target_old

if publish_stable_file_created:
    NM['publish_stable_file_created'] = publish_stable_file_created

result['MILESTONES'].append(NM)


# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)


# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
