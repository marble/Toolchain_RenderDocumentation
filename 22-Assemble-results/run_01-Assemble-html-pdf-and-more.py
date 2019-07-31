#!/usr/bin/env python
# coding: utf-8

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
from __future__ import absolute_import
import os
import shutil
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
    result = tct.deepget(D, *keys, **kwdargs)
    loglist.append((keys, result))
    return result

# ==================================================
# define
# --------------------------------------------------

package_file_new_value = None
xeq_name_cnt = 0


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    build_html = lookup(milestones, 'build_html')
    build_html_folder = lookup(milestones, 'build_html_folder')
    TheProject = lookup(milestones, 'TheProject')
    version = lookup(milestones, 'buildsettings', 'version')

    if not (build_html and build_html_folder and TheProject and version):
        exitcode = 22

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('PROBLEM with required params')


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    all_html_files_sanitized = lookup(milestones, 'all_html_files_sanitized')
    all_singlehtml_files_sanitized = lookup(milestones, 'all_singlehtml_files_sanitized')
    build_latex = lookup(milestones, 'build_latex')
    build_pdf = lookup(milestones, 'build_pdf')
    build_singlehtml = lookup(milestones, 'build_singlehtml')
    build_singlehtml_folder = lookup(milestones, 'build_singlehtml_folder')
    package_file = lookup(milestones, 'package_file')
    postprocessing_is_required = lookup(milestones, 'postprocessing_is_required')
    if postprocessing_is_required:
        if not all_html_files_sanitized:
            exitcode = 22
        if not all_singlehtml_files_sanitized and build_singlehtml:
            exitcode = 22

if exitcode == CONTINUE:
    assembled = []
    TheProjectResult = TheProject + 'Result'
    loglist.append(('TheProjectResult', TheProjectResult))
    if os.path.exists(TheProjectResult):
        loglist.append("'TheProjectResult' already exists.")
        exitcode = 22

if exitcode == CONTINUE:
    src = build_html_folder
    TheProjectResultVersion = os.path.join(TheProjectResult, version)
    shutil.move(src, TheProjectResultVersion)
    assembled.append('html')

    if build_singlehtml and build_singlehtml_folder and all_singlehtml_files_sanitized:
        shutil.move(build_singlehtml_folder, os.path.join(TheProjectResultVersion, 'singlehtml'))
        assembled.append('singlehtml')

    pdf_file = milestones.get('pdf_file')
    pdf_dest_file = None
    pdf_dest_folder = None
    if pdf_file:
        srcname = os.path.split(pdf_file)[1]
        destname = srcname
        NAMING = milestones.get('NAMING')
        if NAMING:
            naming_project_name = NAMING.get('project_name')
            naming_project_version = NAMING.get('project_version')
            if naming_project_name and naming_project_version:
                destname = 'manual.' + naming_project_name + '-' + naming_project_version + '.pdf'
    if pdf_file:
        pdf_dest_folder = os.path.join(TheProjectResultVersion, '_pdf')
        pdf_dest_file = os.path.join(pdf_dest_folder, destname)
        if not os.path.exists(pdf_dest_folder):
            os.makedirs(pdf_dest_folder)
        shutil.copy(pdf_file, pdf_dest_file)
        assembled.append('pdf')

    if package_file:
        TheProjectResultPackages = os.path.join(TheProjectResult, 'packages')
        if not os.path.exists(TheProjectResultPackages):
            os.makedirs(TheProjectResultPackages)

        shutil.move(package_file, TheProjectResultPackages)
        package_file_new_value = os.path.join(TheProjectResultPackages, os.path.split(package_file)[1])


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if exitcode == CONTINUE:
    result['MILESTONES'].append({
        'assembled': assembled,
        'TheProjectResult': TheProjectResult,
        'TheProjectResultVersion': TheProjectResultVersion})

    if package_file_new_value:
        result['MILESTONES'].append({'package_file': package_file_new_value})

    if pdf_dest_file:
        result['MILESTONES'].append({'pdf_dest_file': pdf_dest_file})

    if pdf_dest_folder:
        result['MILESTONES'].append({'pdf_dest_folder': pdf_dest_folder})


# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)


# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
