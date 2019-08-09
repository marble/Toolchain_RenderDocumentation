#!/usr/bin/env python

# ==================================================
# open
# --------------------------------------------------

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
resultfile = params['resultfile']
result = tct.readjson(resultfile)
loglist = result['loglist'] = result.get('loglist', [])
toolname = params['toolname']
toolname_pure = params['toolname_pure']
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

# we assume:
#     typo3cms/project/0.0.0        publish_dir
#     typo3cms/project              publish_dir_language
#     typo3cms/project              publish_dir_project

#     typo3cms/project/fr-fr/0.0.0  publish_dir
#     typo3cms/project/fr-fr        publish_dir_language
#     typo3cms/project              publish_dir_project


known_target_folders = ['/typo3cms']

localized = None
publish_dir = None
publish_dir_buildinfo_planned = ''
publish_dir_planned = None
publish_language_dir_planned = None
publish_package_dir_planned = ''
publish_parent_dir = None
publish_parent_dir_planned = None
publish_project_dir_planned = None
publish_project_parent_dir = None
publish_project_parent_dir_planned = None
publish_settings_cfg_planned = None
publish_warnings_txt_planned = None
xeq_name_cnt = 0

# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    buildsettings_builddir = lookup(milestones, 'buildsettings_builddir',
                                    default=None)
    create_buildinfo = lookup(milestones, 'create_buildinfo', default=1)
    relative_part_of_builddir = lookup(milestones, 'relative_part_of_builddir',
                                       default=None)
    TheProjectResult = lookup(milestones, 'TheProjectResult', default=None)
    TheProjectResultVersion = lookup(milestones, 'TheProjectResultVersion',
                                     default=None)
    TheProjectWebroot = lookup(milestones, 'TheProjectWebroot', default=None)
    url_of_webroot = lookup(milestones, 'url_of_webroot', default=None)
    # webroot_abspath = lookup(milestones, 'webroot_abspath', default=None)

    if not (1
            and buildsettings_builddir
            and relative_part_of_builddir
            and TheProjectResult
            and TheProjectResultVersion
            and TheProjectWebroot
            and url_of_webroot
            # and webroot_abspath
            ):
        exitcode = 22

    buildsettings_localization = lookup(milestones, 'buildsettings',
                                        'localization', default='')


if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('Bad PARAMS or nothing to do')


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    # 'typo3cms/project/0.0.0'
    relative_part_of_builddir_stripped = relative_part_of_builddir.strip('/')
    # /abspath/to/Documentation-GENERATED-temp
    resultdir = lookup(milestones, 'resultdir', default=None)
    # /tmp/.../TheProjectResultVersion
    TheProjectResultVersionLen = len(TheProjectResultVersion)

    if buildsettings_localization in ['', 'default']:
        localized = 0
        required_parts = 2
    else:
        localized = 1
        required_parts = 3

    # project/[language/]0.0.0
    if len(relative_part_of_builddir_stripped.split('/')) < required_parts:
        loglist.append("'%s' is shorter than the '%s' required parts"
                       % (relative_part_of_builddir_stripped, required_parts))
        exitcode = 22

if exitcode == CONTINUE:

    if localized:
        # a='.../typo3cms', b='project', c='en_us', d='0.0.0'
        a, d = os.path.split(relative_part_of_builddir_stripped)
        a, c = os.path.split(a)
        a, b = os.path.split(a)
    else:
        # a='.../typo3cms', b='project', c='', d='0.0.0'
        a, d = os.path.split(relative_part_of_builddir_stripped)
        a, b = os.path.split(a)
        c = ''

    # TheProjectWebroot/typo3cms
    publish_project_parent_dir_planned = os.path.join(TheProjectWebroot, a)
    # TheProjectWebroot/typo3cms/project
    publish_project_dir_planned = os.path.join(TheProjectWebroot, a, b)
    # TheProjectWebroot/typo3cms/project/
    # TheProjectWebroot/typo3cms/project/en-us
    publish_language_dir_planned = os.path.join(TheProjectWebroot, a, b, c)
    # TheProjectWebroot/typo3cms/project/0.0.0
    # TheProjectWebroot/typo3cms/project/en-us/0.0.0
    publish_dir_planned = os.path.join(TheProjectWebroot, a, b, c, d)

    # eliminate this one!
    # TheProjectWebroot/typo3cms/project/0.0.0
    # TheProjectWebroot/typo3cms/project/en-us/0.0.0
    publish_parent_dir_planned = os.path.split(publish_dir_planned)[0]

    # TheProjectWebroot/typo3cms/project/packages
    publish_package_dir_planned = os.path.join(publish_project_dir_planned,
                                               'packages')

if 0 and "Eliminate this!" and exitcode == CONTINUE:
    publish_project_parent_dir_planned = os.path.split(
        publish_parent_dir_planned)[0]
    if os.path.exists(publish_project_parent_dir_planned):
        publish_project_parent_dir = publish_project_parent_dir_planned

if exitcode == CONTINUE:
    if os.path.exists(publish_project_parent_dir_planned):
        publish_project_dir = publish_project_dir_planned

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if exitcode == CONTINUE:
    publish_dir_buildinfo_planned = publish_dir_planned + '/_buildinfo'
    publish_dir_pdf_planned = publish_dir_planned + '/_pdf'
    publish_warnings_txt_planned = (publish_dir_buildinfo_planned
                                    + '/warnings.txt')
    publish_settings_cfg_planned = (publish_dir_buildinfo_planned
                                    + '/Settings.cfg')

    publish_dir_singlehtml_planned = ''
    build_singlehtml_folder = lookup(milestones, 'build_singlehtml_folder',
                                     default=None)
    if build_singlehtml_folder:
        publish_dir_singlehtml_planned = (
                publish_dir_planned + '/'
                + os.path.split(build_singlehtml_folder)[1])

    publish_file_pdf_planned = ''
    pdf_dest_file = lookup(milestones, 'pdf_dest_file', default=None)
    if pdf_dest_file:
        publish_file_pdf_planned = (publish_dir_pdf_planned + '/'
                                    + os.path.split(pdf_dest_file)[1])

    publish_package_file_planned = ''
    package_file = lookup(milestones, 'package_file', default=None)
    if publish_package_dir_planned and package_file:
        publish_package_file_planned = os.path.join(
            publish_package_dir_planned, os.path.split(package_file)[1])


    result['MILESTONES'].append({
        'publish_dir_buildinfo_planned':      publish_dir_buildinfo_planned,
        'publish_dir_pdf_planned':            publish_dir_pdf_planned,
        'publish_dir_planned':                publish_dir_planned,
        'publish_file_pdf_planned':           publish_file_pdf_planned,
        'publish_language_dir_planned':       publish_language_dir_planned,
        'publish_package_dir_planned':        publish_package_dir_planned,
        'publish_package_file_planned':       publish_package_file_planned,
        'publish_parent_dir_planned':         publish_parent_dir_planned,
        'publish_project_dir_planned':        publish_project_dir_planned,
        'publish_project_parent_dir':         publish_project_parent_dir,
        'publish_project_parent_dir_planned': publish_project_parent_dir_planned,
        'publish_settings_cfg_planned':       publish_settings_cfg_planned,
        'publish_warnings_txt_planned':       publish_warnings_txt_planned,
    })

    tuples = [
        ('absurl_buildinfo_dir',              publish_dir_buildinfo_planned,      '/'),
        ('absurl_html_dir',                   publish_dir_planned,                '/'),
        ('absurl_package_dir',                publish_package_dir_planned,        '/'),
        ('absurl_package_file',               publish_package_file_planned,       ''),
        ('absurl_parent_dir',                 publish_parent_dir_planned,         '/'),
        ('absurl_project_parent_dir',         publish_project_parent_dir,         '/'),
        ('absurl_project_parent_dir_planned', publish_project_parent_dir_planned, '/'),
        ('absurl_pdf_dir',                    publish_dir_pdf_planned,            '/'),
        ('absurl_pdf_file',                   publish_file_pdf_planned,           ''),
        ('absurl_settings_cfg_file',          publish_settings_cfg_planned,       ''),
        ('absurl_singlehtml_dir',             publish_dir_singlehtml_planned,     '/'),
        ('absurl_warnings_txt_file',          publish_warnings_txt_planned,       ''),
    ]

    some_milestones = {}
    for a, b, c in tuples:
        if b:
            some_milestones[a] = (url_of_webroot + b[len(TheProjectWebroot):]
                                  + c)
    result['MILESTONES'].append(some_milestones)

    if create_buildinfo:
        result['MILESTONES'].append({'create_buildinfo':create_buildinfo})

# ==================================================
# save result
# --------------------------------------------------

tct.save_the_result(result, resultfile, params, facts, exitcode=exitcode, CONTINUE=CONTINUE)


# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
