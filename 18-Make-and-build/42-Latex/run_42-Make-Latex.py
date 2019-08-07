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

documentation_folder_for_sphinx = ''
xeq_name_cnt = 0


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')
    make_latex = lookup(milestones, 'make_latex')
    if not make_latex:
        loglist.append('Nothing to do - make_latex is not requested.')
        CONTINUE = -2

if exitcode == CONTINUE:
    ready_for_build = lookup(milestones, 'ready_for_build')
    rebuild_needed = lookup(milestones, 'rebuild_needed')
    included_files_check_is_ok = lookup(milestones, 'included_files_check_is_ok')
    toolname = lookup(params, 'toolname')
    build_html = lookup(milestones, 'build_html')
    loglist.append('End of PARAMS')

if exitcode == CONTINUE:
    if not (ready_for_build and rebuild_needed and toolname
            and included_files_check_is_ok and build_html):
        loglist.append('parameters are not sufficient')
        CONTINUE = -2

# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    #1
    build_latex_folder = ''
    has_settingscfg = milestones.get('has_settingscfg')
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
    if not (masterdoc and rebuild_needed and SPHINXBUILD and SYMLINK_THE_OUTPUT
            and SYMLINK_THE_PROJECT and TheProject and TheProjectBuild
            and TheProjectCacheDir and TheProjectLog and TheProjectMakedir):
        exitcode = 22


if exitcode == CONTINUE:
    documentation_folder_for_sphinx = os.path.split(masterdoc)[0]

    def cmdline(cmd, cwd=None):
        if cwd is None:
            cwd = os.getcwd()
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=cwd)
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
    sourcedir = documentation_folder_for_sphinx
    outdir = os.path.join(TheProjectBuild, builder)
    build_latex_folder = outdir
    outdir_in_cache = os.path.join(TheProjectCacheDir, builder)
    warnings_file_folder = os.path.join(TheProjectLog, builder)
    warnings_file = os.path.join(warnings_file_folder, 'warnings.txt')
    # different builder may share the same .doctree
    doctree_folder = os.path.join(TheProjectCacheDir, 'html', '.doctrees')
    loglist.append(('doctree_folder', doctree_folder))
    confpy_folder = TheProjectMakedir
    if not ospe(warnings_file_folder):
        os.makedirs(warnings_file_folder)
    if not ospe(outdir_in_cache):
        os.makedirs(outdir_in_cache)

    cmdlist = [
        'sphinx-build',
      # '-a',                  # write all files; default is to only write new and changed files
        '-b ' + builder,       # builder to use; default is html
        '-c ' + confpy_folder, # path where configuration file(conf.py) is located (default: same as sourcedir)
        ]
    if doctree_folder and ospe(doctree_folder):
        cmdlist.extend(['-d ' + doctree_folder]) # path for the cached environment and doctree files (default: outdir /.doctrees)
    cmdlist.extend([
      # '-E',                  # don't use a saved environment, always read all files
        '-n',                  # nit-picky mode, warn about all missing references
        '-T',                  # show full traceback on exception
        '-w ' + warnings_file, # write warnings (and errors) to given file
        SYMLINK_THE_PROJECT,
        SYMLINK_THE_OUTPUT
        ])
    if ospe(SYMLINK_THE_OUTPUT):
        os.unlink(SYMLINK_THE_OUTPUT)
    if ospe(SYMLINK_THE_PROJECT):
        os.unlink(SYMLINK_THE_PROJECT)
    # let sphinx build directly to the cache
    os.symlink(outdir_in_cache, SYMLINK_THE_OUTPUT)
    loglist.append(('os.symlink(outdir_in_cache, SYMLINK_THE_OUTPUT)', outdir_in_cache, SYMLINK_THE_OUTPUT))
    os.symlink(sourcedir, SYMLINK_THE_PROJECT)
    loglist.append(('os.symlink(sourcedir, SYMLINK_THE_PROJECT)', sourcedir, SYMLINK_THE_PROJECT))

    exitcode, cmd, out, err = execute_cmdlist(cmdlist, cwd=workdir)

    if ospe(SYMLINK_THE_OUTPUT):
        os.unlink(SYMLINK_THE_OUTPUT)
    if ospe(SYMLINK_THE_PROJECT):
        os.unlink(SYMLINK_THE_PROJECT)

    # by definition:
    latex_file = os.path.join(build_latex_folder, 'PROJECT.tex')

if exitcode == CONTINUE:
    # Now, since Sphinx has written directly to the Cachedir, we fetch that
    # result since the Toolchain is expecting that and
    # copy folder 'outdir_in_cache' as 'outdir'
    cmdlist = ['rsync', '-a', '--delete', '"%s"' % outdir_in_cache, '"%s/"' % TheProjectBuild ]
    exitcode, cmd, out, err = execute_cmdlist(cmdlist, cwd=workdir)



# ==================================================
# Set MILESTONE
# --------------------------------------------------

if exitcode == CONTINUE:
    result['MILESTONES'].append({
        'build_latex': 'success',
        'build_latex_folder': build_latex_folder,
        'latex_file': latex_file,
    })

if documentation_folder_for_sphinx:
    result['MILESTONES'].append({'documentation_folder_for_sphinx': documentation_folder_for_sphinx})

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
