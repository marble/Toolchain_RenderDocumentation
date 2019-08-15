#!/usr/bin/env python
# coding: utf-8

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
from __future__ import absolute_import

import os
import shutil
import stat
import sys
import tct

from os.path import exists as ospe, join as ospj
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

copied_latex_resources = []
run_latex_make_sh_file = None
xeq_name_cnt = 0


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    make_latex = lookup(milestones, 'make_latex', default=None)
    if not make_latex:
        CONTINUE == -2

if exitcode == CONTINUE:
    build_latex = lookup(milestones, 'build_latex', default=None)
    build_latex_folder = lookup(milestones, 'build_latex_folder', default=None)
    latex_contrib_typo3_folder = lookup(milestones,
                                        'latex_contrib_typo3_folder',
                                        default=None)
    if not (1
            and build_latex
            and build_latex_folder
            and latex_contrib_typo3_folder):
        CONTINUE = -2

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('Bad PARAMS or nothing to do')


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    if not os.path.isdir(latex_contrib_typo3_folder):
        CONTINUE = -2

if exitcode == CONTINUE:
    foldername = os.path.split(latex_contrib_typo3_folder)[1]
    destpath = ospj(build_latex_folder, foldername)
    shutil.copytree(latex_contrib_typo3_folder, destpath)

if exitcode == CONTINUE:
    run_latex_make_sh_file = ospj(build_latex_folder, 'run-make.sh')
    f2text = (
        "#!/bin/bash\n"
        "\n"
        "# This is run-make.sh\n"
        "\n"
        'scriptdir=$( cd $(dirname "$0") ; pwd -P )'
        "\n"
        "# cd to this dir\n"
        "pushd \"$scriptdir\" >/dev/null\n"
        "\n"
        "# set environment var pointing to the folder and run make\n"
        "TEXINPUTS=::texmf_typo3   make\n"
        "\n"
        "popd >/dev/null\n"
        "\n"
    )
    with open(run_latex_make_sh_file, 'w') as f2:
        f2.write(f2text)

    file_permissions = (os.stat(run_latex_make_sh_file).st_mode | stat.S_IXUSR
                                                          | stat.S_IXGRP
                                                          | stat.S_IXOTH)
    os.chmod(run_latex_make_sh_file, file_permissions)


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if copied_latex_resources:
    result['MILESTONES'].append({'copied_latex_resources':
                                 copied_latex_resources})

if run_latex_make_sh_file:
    result['MILESTONES'].append({'run_latex_make_sh_file':
                                 run_latex_make_sh_file})


# ==================================================
# save result
# --------------------------------------------------

tct.save_the_result(result, resultfile, params, facts, milestones, exitcode, CONTINUE)


# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
