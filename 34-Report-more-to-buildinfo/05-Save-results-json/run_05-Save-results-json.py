#!/usr/bin/env python
# coding: utf-8

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
from __future__ import absolute_import
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
toolname = params['toolname']
toolname_pure = params['toolname_pure']
toolchain_name = facts['toolchain_name']
workdir = params['workdir']
exitcode = CONTINUE = 0


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

created = {}
TheProjectResultBuildinfoResultJsonfile = None
xeq_name_cnt = 0


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    TheProjectResultBuildinfo = lookup(milestones, 'TheProjectResultBuildinfo')

    if not (TheProjectResultBuildinfo):
        CONTINUE = -2

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('Nothing to do for these params')


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    TheProjectResultBuildinfoResultJsonfile = os.path.join(TheProjectResultBuildinfo, 'results.json')

    mapping = {
        'checksum_new': 'checksum',
        'builddir': 'publish_dir',
    }
    keys = [
        "checksum_new",
        "checksum_old",
        "checksum_time",
        "checksum_time_decoded",
        "checksum_ttl_seconds",
        "email_notify_about_new_build",
        "emails_user_from_project",
        "known_versions",
    ]
    R = {}
    for k in keys:
        v = milestones.get(k)
        if v:
            k2 = mapping.get(k, k)
            R[k2] = v

    # save, even if empty
    for k, default in (('email_notify_about_new_build', []),
                       ('emails_user_from_project', [])):
        R[k] = milestones.get(k, default)

    buildsettings = milestones.get('buildsettings', {})
    for k in [
        'builddir',
        'gitbranch',
        'gitdir',
        'giturl',
        'localization',
        'ter_extension',
        'ter_extkey',
        'ter_extversion',
        'ter_version',
        ]:
        v = buildsettings.get(k)
        if v:
            k2 = mapping.get(k, k)
            R[k2] = v

    html_key_values = milestones.get('html_key_values', {})
    for k in ['build_time']:
        v = html_key_values.get(k)
        if v:
            R[k] = v

    settings_cfg_general = milestones.get('settings_cfg', {}).get('general', {})
    for k in [
        'copyright',
        'description',
        'project',
        'release',
        't3author',
        'version']:
        v = settings_cfg_general.get(k)
        if v:
            R[k] = v

    if milestones.get('build_html'):
        created['html'] = 1
    if milestones.get('build_latex'):
        created['latex'] = 1
    if milestones.get('build_package'):
        created['package'] = 1
    if milestones.get('build_pdf'):
        created['pdf'] = 1
    if milestones.get('build_singlehtml'):
        created['singlehtml'] = 1

    if created:
        R['created'] = created

    if milestones.get('neutralized_links_jsonfile'):
        R['has_neutralized_links'] = 1
    else:
        R['has_neutralized_links'] = 0

    if milestones.get('neutralized_images_jsonfile'):
        R['has_neutralized_images'] = 1
    else:
        R['has_neutralized_images'] = 0

    tct.writejson(R, TheProjectResultBuildinfoResultJsonfile)

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if TheProjectResultBuildinfoResultJsonfile:
    result['MILESTONES'].append({
        'TheProjectResultBuildinfoResultJsonfile':
        TheProjectResultBuildinfoResultJsonfile})


# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)


# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
