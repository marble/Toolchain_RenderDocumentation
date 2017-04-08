#!/usr/bin/env python

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
import os
import sys
import tct

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


known_target_folders = ['/typo3cms']

publish_dir = None
publish_dir_buildinfo_planned = ''
publish_dir_planned = ''
publish_package_dir_planned = ''
publish_parent_dir = None
publish_parent_dir_planned = ''
publish_parent_parent_dir = None
publish_parent_parent_dir_planned = ''
publish_settings_cfg_planned = ''
publish_warnings_txt_planned = ''
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
    url_of_webroot = milestones_get('url_of_webroot')
    TheProjectResult = milestones_get('TheProjectResult')
    TheProjectResultVersion = milestones_get('TheProjectResultVersion')
    buildsettings_builddir = milestones_get('buildsettings_builddir')
    webroot_part_of_builddir = milestones_get('webroot_part_of_builddir')
    webroot_abspath = milestones_get('webroot_abspath')
    relative_part_of_builddir = milestones_get('relative_part_of_builddir')


    # test
    if not (url_of_webroot and TheProjectResult and TheProjectResultVersion and
            buildsettings_builddir and
            webroot_part_of_builddir and webroot_abspath and
            relative_part_of_builddir):
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
    TheProjectResultVersionLen = len(TheProjectResultVersion)

    publish_dir_planned = webroot_abspath + relative_part_of_builddir
    loglist.append(('publish_dir_planned', publish_dir_planned))

if exitcode == CONTINUE:
    publish_parent_dir_planned = os.path.split(publish_dir_planned)[0]
    loglist.append(('publish_parent_dir_planned', publish_parent_dir_planned))
    publish_package_dir_planned = os.path.join(publish_parent_dir_planned, 'packages')
    loglist.append(('publish_package_dir_planned', publish_package_dir_planned))

if exitcode == CONTINUE:
    publish_parent_parent_dir_planned = os.path.split(publish_parent_dir_planned)[0]
    if os.path.exists(publish_parent_parent_dir_planned):
        publish_parent_parent_dir = publish_parent_parent_dir_planned

    if 0:
        if not os.path.exists(publish_parent_parent_dir):
            loglist.append(('publish_parent_parent_dir does not exist', publish_parent_parent_dir))
            exitcode = 22


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if exitcode == CONTINUE:
    publish_dir_buildinfo_planned = publish_dir_planned + '/_buildinfo'
    publish_dir_pdf_planned = publish_dir_planned + '/_pdf'
    publish_warnings_txt_planned = publish_dir_buildinfo_planned + '/warnings.txt'
    publish_settings_cfg_planned = publish_dir_buildinfo_planned + '/Settings.cfg'

    publish_dir_singlehtml_planned = ''
    build_singlehtml_folder = milestones_get('build_singlehtml_folder')
    if build_singlehtml_folder:
        publish_dir_singlehtml_planned = publish_dir_planned + '/' + os.path.split(build_singlehtml_folder)[1]

    publish_file_pdf_planned = ''
    pdf_dest_file = milestones_get('pdf_dest_file')
    if pdf_dest_file:
        publish_file_pdf_planned = publish_dir_pdf_planned + '/' + os.path.split(pdf_dest_file)[1]

    publish_package_file_planned = ''
    package_file = milestones_get('package_file')
    if publish_package_dir_planned and package_file:
        publish_package_file_planned = os.path.join(publish_package_dir_planned, os.path.split(package_file)[1])


    result['MILESTONES'].append({
        'publish_dir_buildinfo_planned':        publish_dir_buildinfo_planned,
        'publish_dir_pdf_planned':              publish_dir_pdf_planned,
        'publish_dir_planned':                  publish_dir_planned,
        'publish_file_pdf_planned':             publish_file_pdf_planned,
        'publish_package_dir_planned':          publish_package_dir_planned,
        'publish_package_file_planned':         publish_package_file_planned,
        'publish_parent_dir_planned':           publish_parent_dir_planned,
        'publish_parent_parent_dir':            publish_parent_parent_dir,
        'publish_parent_parent_dir_planned':    publish_parent_parent_dir_planned,
        'publish_settings_cfg_planned':         publish_settings_cfg_planned,
        'publish_warnings_txt_planned':         publish_warnings_txt_planned,
    })

    tuples = [
        ('absurl_buildinfo_dir',                publish_dir_buildinfo_planned,      '/'),
        ('absurl_html_dir',                     publish_dir_planned,                '/'),
        ('absurl_package_dir',                  publish_package_dir_planned,        '/'),
        ('absurl_package_file',                 publish_package_file_planned,       '' ),
        ('absurl_parent_dir',                   publish_parent_dir_planned,         '/'),
        ('absurl_parent_parent_dir',            publish_parent_parent_dir,          '/'),
        ('absurl_parent_parent_dir_planned',    publish_parent_parent_dir_planned,  '/'),
        ('absurl_pdf_dir',                      publish_dir_pdf_planned,            '/'),
        ('absurl_pdf_file',                     publish_file_pdf_planned,           '' ),
        ('absurl_settings_cfg_file',            publish_settings_cfg_planned,       '' ),
        ('absurl_singlehtml_dir',               publish_dir_singlehtml_planned,     '/'),
        ('absurl_warnings_txt_file',            publish_warnings_txt_planned,       '' ),
    ]

    some_milestones = {}
    for a, b, c in tuples:
        if b:
            some_milestones[a] = url_of_webroot + b[len(webroot_abspath):] + c
    result['MILESTONES'].append(some_milestones)


# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)


# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
