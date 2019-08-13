#!/usr/bin/env python
# coding: utf-8

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
from __future__ import absolute_import

import codecs
import os
import subprocess
import sys
import tct

from os.path import join as ospj, exists as ospe

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

build_latex = None
build_latex_file = None
build_latex_folder = None
builder_latex_folder = None
xeq_name_cnt = 0


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    make_latex = lookup(milestones, 'make_latex')
    if not make_latex:
        CONTINUE = -2

if exitcode == CONTINUE:
    disable_include_files_check = lookup(milestones,
                                         'disable_include_files_check')
    included_files_check_is_ok = lookup(milestones,
                                        'included_files_check_is_ok')
    if not (0
            or disable_include_files_check
            or included_files_check_is_ok
    ):
        CONTINUE = -2

if exitcode == CONTINUE:
    build_html = lookup(milestones, 'build_html')
    ready_for_build = lookup(milestones, 'ready_for_build')
    rebuild_needed = lookup(milestones, 'rebuild_needed')

    if not (1
            and build_html
            and ready_for_build
            and rebuild_needed
    ):
        CONTINUE = -2

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('Bad PARAMS or nothing to do')

# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    #1
    masterdoc = milestones.get('masterdoc')
    rebuild_needed = milestones.get('rebuild_needed')
    SPHINXBUILD = milestones.get('SPHINXBUILD')
    SYMLINK_THE_OUTPUT = lookup(milestones, 'SYMLINK_THE_OUTPUT')
    SYMLINK_THE_PROJECT = lookup(milestones, 'SYMLINK_THE_PROJECT')
    TheProject = milestones.get('TheProject')
    TheProjectBuild = milestones.get('TheProjectBuild')
    TheProjectCacheDir = lookup(milestones, 'TheProjectCacheDir')
    TheProjectLog = milestones.get('TheProjectLog')
    TheProjectMakedir = milestones.get('TheProjectMakedir')
    if not (1
            and masterdoc
            and rebuild_needed
            and SPHINXBUILD
            and SYMLINK_THE_OUTPUT
            and SYMLINK_THE_PROJECT
            and TheProject
            and TheProjectBuild
            and TheProjectCacheDir
            and TheProjectLog
            and TheProjectMakedir
    ):
        exitcode = 22


if exitcode == CONTINUE:

    def cmdline(cmd, cwd=None):
        if cwd is None:
            cwd = os.getcwd()
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, shell=True, cwd=cwd)
        out, err = process.communicate()
        exitcode = process.returncode
        return exitcode, cmd, out, err

    def execute_cmdlist(cmdlist, cwd=None):
        global xeq_name_cnt
        cmd = ' '.join(cmdlist)
        cmd_multiline = ' \\\n   '.join(cmdlist) + '\n'

        xeq_name_cnt += 1
        filename_cmd = 'xeq-%s-%d-%s.txt' % (toolname_pure, xeq_name_cnt, 'cmd')
        filename_err = 'xeq-%s-%d-%s.txt' % (toolname_pure, xeq_name_cnt, 'err')
        filename_out = 'xeq-%s-%d-%s.txt' % (toolname_pure, xeq_name_cnt, 'out')

        with codecs.open(os.path.join(workdir, filename_cmd), 'w', 'utf-8') as f2:
            f2.write(cmd_multiline.decode('utf-8', 'replace'))

        exitcode, cmd, out, err = cmdline(cmd, cwd=cwd)

        loglist.append({'exitcode': exitcode, 'cmd': cmd, 'out': out, 'err': err})

        with codecs.open(os.path.join(workdir, filename_out), 'w', 'utf-8') as f2:
            f2.write(out.decode('utf-8', 'replace'))

        with codecs.open(os.path.join(workdir, filename_err), 'w', 'utf-8') as f2:
            f2.write(err.decode('utf-8', 'replace'))

        return exitcode, cmd, out, err


if exitcode == CONTINUE:
    builder = 'latex'

    warnings_file_folder = os.path.join(TheProjectLog, builder)
    warnings_file = os.path.join(warnings_file_folder, 'warnings.txt')

    html_doctrees_folder = lookup(milestones, 'html_doctrees_folder')
    confpy_folder = TheProjectMakedir
    if not ospe(warnings_file_folder):
        os.makedirs(warnings_file_folder)

    # Here we decide where the inital build goes
    usingTheProjectCacheDir = None
    if 0:
        # can be external
        builder_latex_folder = os.path.join(TheProjectCacheDir, builder)
        usingTheProjectCacheDir = True
    if 1:
        # always within the /tmp area
        builder_latex_folder = os.path.join(TheProjectBuild, builder)
        usingTheProjectCacheDir = False

    if builder_latex_folder and not ospe(builder_latex_folder):
        os.makedirs(builder_latex_folder)

    cmdlist = [
        'sphinx-build',
      # '-a',                # always write all files
        '-b', builder,
        '-c', confpy_folder,
        ]

    if html_doctrees_folder:
        cmdlist.extend([
            '-d', html_doctrees_folder])

    cmdlist.extend([
      # '-E',
        '-n',
        '-T',
        '-w', warnings_file,
        SYMLINK_THE_PROJECT,
        SYMLINK_THE_OUTPUT
        ])

    if ospe(SYMLINK_THE_OUTPUT):
        os.unlink(SYMLINK_THE_OUTPUT)
    if ospe(SYMLINK_THE_PROJECT):
        os.unlink(SYMLINK_THE_PROJECT)

    sourcedir = os.path.split(masterdoc)[0]
    os.symlink(sourcedir, SYMLINK_THE_PROJECT)
    loglist.append(('os.symlink(sourcedir, SYMLINK_THE_PROJECT)',
                    sourcedir, SYMLINK_THE_PROJECT))

    os.symlink(builder_latex_folder, SYMLINK_THE_OUTPUT)
    loglist.append(('os.symlink(builder_latex_folder, SYMLINK_THE_OUTPUT)',
                    builder_latex_folder, SYMLINK_THE_OUTPUT))

    exitcode, cmd, out, err = execute_cmdlist(cmdlist, cwd=workdir)

    if ospe(SYMLINK_THE_OUTPUT):
        os.unlink(SYMLINK_THE_OUTPUT)
    if ospe(SYMLINK_THE_PROJECT):
        os.unlink(SYMLINK_THE_PROJECT)
    if not ospe(builder_latex_folder):
        builder_latex_folder = None

if exitcode == CONTINUE:
    build_latex = 'success'
    if usingTheProjectCacheDir:
        cmdlist = ['rsync', '-a', '--delete',
                   '"%s"' % builder_latex_folder,
                   '"%s/"' % TheProjectBuild ]
        exitcode, cmd, out, err = execute_cmdlist(cmdlist, cwd=workdir)

if exitcode == CONTINUE:
    build_latex_folder = ospj(TheProjectBuild, builder)
    if not ospe(build_latex_folder):
        build_latex_folder = None
    if build_latex_folder:
        build_latex_file = ospj(build_latex_folder, 'PROJECT.tex')
        if not ospe(build_latex_file):
            build_latex_file = None


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if build_latex:
    result['MILESTONES'].append({'build_latex': 'success'})

# within TheProjectBuild
if build_latex_folder:
    result['MILESTONES'].append({'build_latex_folder': build_latex_folder})

# where the Sphinx builder initially builds
if builder_latex_folder:
    result['MILESTONES'].append({'builder_latex_folder': builder_latex_folder})

if build_latex_file:
    result['MILESTONES'].append({'build_latex_file': build_latex_file})


# ==================================================
# save result
# --------------------------------------------------

tct.save_the_result(result, resultfile, params, facts, milestones, exitcode, CONTINUE)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
