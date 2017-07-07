#!/usr/bin/env python
# coding: utf-8

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
# Define variables
# --------------------------------------------------

package_file_new_value = None
pdf_dest_file = None
pdf_dest_folder = None

# ==================================================
# Check required milestone(s)
# --------------------------------------------------
def milestones_get(name, default=None):
    result = milestones.get(name, default)
    loglist.append((name, result))
    return result

if exitcode == CONTINUE:
    buildsettings = milestones_get('buildsettings', {})
    if not buildsettings:
        exitcode = 2

if exitcode == CONTINUE:
    build_html = milestones_get('build_html')
    build_html_folder = milestones_get('build_html_folder')
    TheProject = milestones_get('TheProject')
    version = buildsettings.get('version')

if exitcode == CONTINUE:
    if not (build_html and build_html_folder and TheProject and version):
        exitcode = 2

if exitcode == CONTINUE:
    build_singlehtml = milestones_get('build_singlehtml')
    build_singlehtml_folder = milestones_get('build_singlehtml_folder')
    build_latex = milestones_get('build_latex')
    build_pdf = milestones_get('build_pdf')
    package_file = milestones_get('package_file')

# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:

    import shutil

    assembled = []
    TheProjectResult = TheProject + 'Result'
    loglist.append(TheProjectResult)
    if os.path.exists(TheProjectResult):
        loglist.append("'TheProjectResult' already exists.")
        exitcode = 2

if exitcode == CONTINUE:
    src = build_html_folder
    TheProjectResultVersion = os.path.join(TheProjectResult, version)
    shutil.move(src, TheProjectResultVersion)
    assembled.append('html')

    if build_singlehtml and build_singlehtml_folder:
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
        shutil.move(pdf_file, pdf_dest_file)
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
