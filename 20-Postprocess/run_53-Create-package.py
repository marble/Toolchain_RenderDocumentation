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

package_file = None
package_name = 'manual.zip'
pdf_name = 'manual.pdf'
xeq_name_cnt = 0


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    buildsettings = lookup(milestones, 'buildsettings')
    make_package = lookup(milestones, 'make_package')
    package_language = lookup(milestones, 'buildsettings', 'package_language', default=None)
    package_key = lookup(milestones, 'buildsettings', 'package_key', default=None)

    # build_html = milestones_get('build_html')
    build_html_folder = lookup(milestones, 'build_html_folder')
    # build_singlehtml = milestones_get('build_singlehtml')
    # build_singlehtml_folder = milestones_get('build_singlehtml_folder')
    # build_latex = milestones_get('build_latex')
    # build_pdf = milestones_get('build_pdf')
    pdf_file = lookup(milestones, 'pdf_file')
    # TheProject = milestones_get('TheProject')
    pdf_name = lookup(milestones, 'NAMING', 'pdf_name', default=pdf_name)
    package_name = lookup(milestones, 'NAMING', 'package_name', default=package_name)
    TheProjectBuild = lookup(milestones, 'TheProjectBuild')

    if not (make_package and package_key and package_language
            and build_html_folder and TheProjectBuild):
        CONTINUE = -2

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

if pdf_name:
    result['MILESTONES'].append({'pdf_name': pdf_name})

if package_name:
    result['MILESTONES'].append({'package_name': package_name})

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
