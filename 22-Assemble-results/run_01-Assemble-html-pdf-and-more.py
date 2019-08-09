#!/usr/bin/env python
# coding: utf-8

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
from __future__ import absolute_import

import os
import shutil
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

package_file_new_value = None
TheProjectResult = None
xeq_name_cnt = 0


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    build_html = lookup(milestones, 'build_html', default=None)
    build_html_folder = lookup(milestones, 'build_html_folder', default=None)
    TheProject = lookup(milestones, 'TheProject', default=None)
    version = lookup(milestones, 'buildsettings', 'version', default=None)

    if not (1
            and build_html
            and build_html_folder
            and TheProject
            and version):
        CONTINUE = -2

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('PROBLEM with required params')


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    all_html_files_sanitized = lookup(milestones, 'all_html_files_sanitized',
                                      default=None)
    all_singlehtml_files_sanitized = lookup(milestones,
                                            'all_singlehtml_files_sanitized',
                                            default=None)
    build_latex = lookup(milestones, 'build_latex', default=None)
    build_pdf = lookup(milestones, 'build_pdf', default=None)
    build_singlehtml = lookup(milestones, 'build_singlehtml', default=None)
    build_singlehtml_folder = lookup(milestones, 'build_singlehtml_folder',
                                     default=None)
    package_file = lookup(milestones, 'package_file', default=None)
    postprocessing_is_required = lookup(milestones,
                                        'postprocessing_is_required',
                                        default=None)
    if postprocessing_is_required:
        if not all_html_files_sanitized:
            exitcode = 22
        if not all_singlehtml_files_sanitized and build_singlehtml:
            exitcode = 22

if exitcode == CONTINUE:

    # 1
    assembled = []
    TheProjectResult = TheProject + 'Result'

    #2
    TheProjectResultVersion = os.path.join(TheProjectResult, version)

    # move the html result
    shutil.move(build_html_folder, TheProjectResultVersion)
    assembled.append('html')

    if build_singlehtml and build_singlehtml_folder:
        shutil.move(build_singlehtml_folder,
                    os.path.join(TheProjectResultVersion, 'singlehtml'))
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
                destname = ('manual.' + naming_project_name + '-'
                            + naming_project_version + '.pdf')
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
        package_file_new_value = os.path.join(TheProjectResultPackages,
                                              os.path.split(package_file)[1])


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

tct.save_the_result(result, resultfile, params, facts, exitcode=exitcode, CONTINUE=CONTINUE)


# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
