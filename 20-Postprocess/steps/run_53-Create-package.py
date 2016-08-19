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
workdir = params['workdir']
loglist = result['loglist'] = result.get('loglist', [])
exitcode = CONTINUE = 0

# ==================================================
# Get and check required milestone(s)
# --------------------------------------------------

def milestones_get(name, default=None):
    result = milestones.get(name, default)
    loglist.append((name, result))
    return result

if exitcode == CONTINUE:
    package_file = None
    buildsettings = milestones_get('buildsettings', {})
    package_language = buildsettings.get('package_language')
    loglist.append(('package_language', package_language))
    package_key = buildsettings.get('package_key')
    loglist.append(('package_key', package_key))

    # build_html = milestones_get('build_html')
    build_html_folder = milestones_get('build_html_folder')
    # build_singlehtml = milestones_get('build_singlehtml')
    # build_singlehtml_folder = milestones_get('build_singlehtml_folder')
    # build_latex = milestones_get('build_latex')
    # build_pdf = milestones_get('build_pdf')
    pdf_file = milestones_get('pdf_file')
    # TheProject = milestones_get('TheProject')
    pdf_name = milestones_get('NAMING', {}).get('pdf_name', 'manual.pdf')
    package_name = milestones.get('NAMING', {}).get('package_name', 'manual.zip')
    TheProjectBuild = milestones_get('TheProjectBuild')

if not (package_key and package_language and build_html_folder and TheProjectBuild):
    CONTINUE = -1

# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:

    import shutil
    import subprocess

    def cmdline(cmd, cwd=None):
        if cwd is None:
            cwd = os.getcwd()
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=cwd)
        out, err = process.communicate()
        exitcode = process.returncode
        return exitcode, cmd, out, err

    language_segment = package_language.lower()

    dest_folder = os.path.join(workdir, 'packages', package_key, package_language)
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    shutil.copytree(build_html_folder, os.path.join(dest_folder, 'html'))

    if pdf_file:
        dest_folder_pdf = os.path.join(dest_folder, 'pdf')
        if not os.path.exists(dest_folder_pdf):
            os.makedirs(dest_folder_pdf)
        shutil.copy(pdf_file, os.path.join(dest_folder_pdf, pdf_name))

    build_packages_folder = os.path.join(TheProjectBuild, 'packages')
    if not os.path.exists(build_packages_folder):
        os.makedirs(build_packages_folder)

    cwd = os.path.join(workdir, 'packages')
    cmd = 'zip -r -9 -q %s %s' % (package_name, package_key)
    exitcode, cmd, out, err = cmdline(cmd, cwd=cwd)
    loglist.append([exitcode, cmd, out, err])

    src = os.path.join(workdir, 'packages', package_name)
    dest = build_packages_folder
    shutil.move(src, dest)

    package_file = os.path.join(dest, package_name)

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if exitcode == CONTINUE:
    if package_file:
        result['MILESTONES'].append({'package_file': package_file})

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
