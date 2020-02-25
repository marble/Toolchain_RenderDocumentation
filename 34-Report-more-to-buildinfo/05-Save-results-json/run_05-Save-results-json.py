#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function
from __future__ import absolute_import

import os
import sys
import tct

from tct import deepget

params = tct.readjson(sys.argv[1])
binabspath = sys.argv[2]
facts = tct.readjson(params['factsfile'])
milestones = tct.readjson(params['milestonesfile'])
reason = ''
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
        exitcode = 22
        reason = 'Bad PARAMS or nothing to do'

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('Nothing to do for these params')


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    TheProjectResultBuildinfoResultJsonfile = os.path.join(
        TheProjectResultBuildinfo, 'results.json')

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

    settings_cfg_general = lookup(milestones, 'settings_cfg', 'general',
                                  default={})
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

    sitemap_files_html_count = milestones.get('sitemap_files_html_count')
    if sitemap_files_html_count is not None:
        R['sitemap_files_html_count'] = sitemap_files_html_count

    sitemap_files_singlehtml_count = milestones.get('sitemap_files_singlehtml_'
                                                    'count')
    if sitemap_files_singlehtml_count is not None:
        R['sitemap_files_singlehtml_count'] = sitemap_files_singlehtml_count

    R['postprocessed_html_files'] = milestones.get(
        'all_html_files_sanitized_count', 0)

    theme_info = milestones.get('theme_info')
    if theme_info:
        R['theme_info'] = theme_info

if exitcode == CONTINUE:
    # Defined in Dockerfile:
    interesting = [
        'OUR_IMAGE',
        'OUR_IMAGE_SHORT',
        'OUR_IMAGE_VERSION',
        'THEME_MTIME',
        'THEME_NAME',
        'THEME_VERSION',
        'TOOLCHAIN_VERSION',
        'TYPOSCRIPT_PY_VERSION',
    ]
    R['environ'] = {k: os.environ[k] for k in interesting if k in os.environ}


if exitcode == CONTINUE:
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

tct.save_the_result(result, resultfile, params, facts, milestones, exitcode, CONTINUE, reason)


# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
