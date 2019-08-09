#!/usr/bin/env python
# coding: utf-8

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
from __future__ import absolute_import

import os
import shutil
import subprocess
import sys
import tct

ospj = os.path.join
ospe = os.path.exists

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

build_package = None
package_file = None
package_name = 'manual.zip'
pdf_name = 'manual.pdf'
xeq_name_cnt = 0


# ==================================================
# Disable for now
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('Disabled in tool (run_53-Create-package.py '
                   'because its functionality may not be complete.')
    CONTINUE = -2

# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    build_html_folder = lookup(milestones, 'build_html_folder')
    make_package = lookup(milestones, 'make_package')
    package_key = lookup(milestones, 'buildsettings', 'package_key',
                         default=None)
    package_language = lookup(milestones, 'buildsettings', 'package_language',
                              default=None)
    TheProjectBuild = lookup(milestones, 'TheProjectBuild')
    if not (1
            and build_html_folder
            and make_package
            and package_key
            and package_language
            and TheProjectBuild):
        CONTINUE = -2

if exitcode == CONTINUE:
    buildsettings = lookup(milestones, 'buildsettings')
    package_name = lookup(milestones, 'NAMING', 'package_name',
                          default=package_name)
    pdf_file = lookup(milestones, 'pdf_file')
    pdf_name = lookup(milestones, 'NAMING', 'pdf_name', default=pdf_name)

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('Bad PARAMS or nothing to do')


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:

    def cmdline(cmd, cwd=None):
        if cwd is None:
            cwd = os.getcwd()
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,
            cwd=cwd)
        out, err = process.communicate()
        exitcode = process.returncode
        return exitcode, cmd, out, err

    language_segment = package_language.lower()

    # we first assemble everything for the package in the workdir temp folder
    # of this step. Afterwards we run 'zip' to pack everything.

    dest_folder = os.path.join(workdir, 'packages', package_key,
                               package_language)
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    shutil.copytree(build_html_folder, os.path.join(dest_folder, 'html'))

    # Add PDF file if existing
    if pdf_file:
        dest_folder_pdf = os.path.join(dest_folder, 'pdf')
        if not os.path.exists(dest_folder_pdf):
            os.makedirs(dest_folder_pdf)
        shutil.copy(pdf_file, os.path.join(dest_folder_pdf, pdf_name))
    else:
        pdf_name = None

    if 0 and "remove all font files":
        shutil.rmtree(ospj(dest_folder, 'html', '_static', 'fonts'),
                      ignore_errors=True)

    if 1 and "remove some font files":
        fonts_folder = os.path.join(dest_folder, 'html', '_static', 'fonts')
        for f2name in os.listdir(fonts_folder):
            if not ('fontawesome' in f2name):
                f2path = ospj(fonts_folder, f2name)
                if os.path.isfile(f2path):
                    os.remove(f2path)
                elif os.path.isdir(f2path):
                    shutil.rmtree(f2path, ignore_errors=True)

    # use theme without fonts
    theme_css = ospj(dest_folder, 'html', '_static', 'css', 'theme.css')
    theme_no_fonts_css = ospj(dest_folder, 'html', '_static', 'css',
                              'theme-no-fonts.css')
    if ospe(theme_css) and ospe(theme_no_fonts_css):
        os.remove(theme_css)
        os.rename(theme_no_fonts_css, theme_css)

    # ToDo: Improve!
    # remove piwik call
    # find:  <script type = "text/javascript" id="idPiwikScript" src="/js/piwik.js">
    # write: <script type = "text/javascript" id="idPiwikScript">
    needle = 'id="idPiwikScript" src="'
    for dirpath, dirnames, filenames in os.walk(dest_folder):
        for filename in filenames:
            if filename.endswith('.html'):
                with open(ospj(dirpath, filename), 'rb') as f1:
                    data = f1.read()
                p1 = data.find(needle)
                if p1 >= 0:
                    p2 = data.find('"', p1 + len(needle))
                    if p2 > p1:
                        with open(ospj(dirpath, filename), 'w') as f2:
                            f2.write(data[0: p1 + len(needle) - 6])
                            f2.write(data[p2 + 1:])

    # packing
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
    build_package = 'success'


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if pdf_name:
    result['MILESTONES'].append({'pdf_name': pdf_name})

if package_name:
    result['MILESTONES'].append({'package_name': package_name})

if package_file:
    result['MILESTONES'].append({'package_file': package_file})

if build_package:
    result['MILESTONES'].append({'build_package': build_package})


# ==================================================
# save result
# --------------------------------------------------

tct.save_the_result(result, resultfile, params, facts, exitcode, CONTINUE)


# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
