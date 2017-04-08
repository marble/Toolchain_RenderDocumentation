#!/usr/bin/env python

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
import os
import tct
import sys

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

    # required milestones
    requirements = []

    # just test
    for requirement in requirements:
        v = milestones_get(requirement)
        if not v:
            loglist.append("'%s' not found" % requirement)
            exitcode = 22

    # fetch
    publish_dir = milestones_get('publish_dir')
    publish_parent_dir = milestones_get('publish_parent_dir')
    publish_html_done = milestones_get('publish_html_done')
    toolchain_name = facts_get('toolchain_name')

    # test
    if not (publish_dir and publish_parent_dir and publish_html_done
            and toolchain_name):
        exitcode = 22

if exitcode == CONTINUE:
    htaccess_template_show_latest = tct.deepget(facts, 'tctconfig', toolchain_name, 'htaccess_template_show_latest')
    loglist.append(('htaccess_template_show_latest', htaccess_template_show_latest))

    # test
    if not htaccess_template_show_latest:
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
    ter_extension = int(tct.deepget(milestones, 'buildsettings', 'ter_extension'))
    loglist.append(('ter_extension', ter_extension))

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
    publish_stable_file = os.path.join(publish_parent_dir, 'stable')
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
