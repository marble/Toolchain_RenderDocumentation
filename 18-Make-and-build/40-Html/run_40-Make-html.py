#!/usr/bin/env python
# coding: utf-8

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
from __future__ import absolute_import
import codecs
import json
import os
import subprocess
import shutil
import sys
import tct
from  os.path import join as ospj, exists as ospe

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

conf_py_settings = None
documentation_folder_for_sphinx = ''
settings_dump_json_file = None
xeq_name_cnt = 0


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')
    included_files_check_is_ok = lookup(milestones, 'included_files_check_is_ok')
    ready_for_build = lookup(milestones, 'ready_for_build')
    rebuild_needed = lookup(milestones, 'rebuild_needed')
    toolname = lookup(params, 'toolname')
    toolname_pure = lookup(params, 'toolname_pure')
    if not (included_files_check_is_ok and ready_for_build and
            rebuild_needed and toolname and toolname_pure):
        exitcode = 22
    else:
        loglist.append('ok, check more params')

if exitcode == CONTINUE:
    masterdoc = lookup(milestones, 'masterdoc')
    SPHINXBUILD = lookup(milestones, 'SPHINXBUILD')
    SYMLINK_THE_OUTPUT = lookup(milestones, 'SYMLINK_THE_OUTPUT')
    SYMLINK_THE_PROJECT = lookup(milestones, 'SYMLINK_THE_PROJECT')
    TheProject = lookup(milestones, 'TheProject')
    TheProjectBuild = lookup(milestones, 'TheProjectBuild')
    TheProjectCacheDir = lookup(milestones, 'TheProjectCacheDir')
    TheProjectLog = lookup(milestones, 'TheProjectLog')
    TheProjectMakedir = lookup(milestones, 'TheProjectMakedir')
    if not (masterdoc and SPHINXBUILD and SYMLINK_THE_OUTPUT
            and SYMLINK_THE_PROJECT and TheProject and TheProjectBuild
            and TheProjectCacheDir and TheProjectLog and TheProjectMakedir):
        exitcode = 22

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('PROBLEM with required params')

if CONTINUE != 0:
    loglist.append({'CONTINUE': CONTINUE})
    loglist.append('NOTHING to do')

# ==================================================
# work
# --------------------------------------------------

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

        with codecs.open(ospj(workdir, filename_cmd), 'w', 'utf-8') as f2:
            f2.write(cmd_multiline.decode('utf-8', 'replace'))

        exitcode, cmd, out, err = cmdline(cmd, cwd=cwd)

        loglist.append({'exitcode': exitcode, 'cmd': cmd, 'out': out, 'err': err})

        with codecs.open(ospj(workdir, filename_out), 'w', 'utf-8') as f2:
            f2.write(out.decode('utf-8', 'replace'))

        with codecs.open(ospj(workdir, filename_err), 'w', 'utf-8') as f2:
            f2.write(err.decode('utf-8', 'replace'))

        return exitcode, cmd, out, err


if exitcode == CONTINUE:
    builder = 'html'
    sourcedir = documentation_folder_for_sphinx
    outdir = ospj(TheProjectBuild, builder)
    outdir_in_cache = ospj(TheProjectCacheDir, builder)
    warnings_file_folder = ospj(TheProjectLog, builder)
    warnings_file = ospj(warnings_file_folder, 'warnings.txt')
    doctree_folder = ospj(TheProjectBuild, 'doctree', builder)
    confpy_folder = TheProjectMakedir
    if not ospe(warnings_file_folder):
        os.makedirs(warnings_file_folder)
    if not ospe(outdir_in_cache):
        os.makedirs(outdir_in_cache)


if exitcode == CONTINUE:
    if 1:
        cmdlist = [
            'sphinx-build',
            ]
    if 0 and '--no-cache or something like that name':
        cmdlist.extend([
            '-a',                  # write all files; default is to only write new and changed files
            ])
    if 0 and '--no-cache or something like that name':
        cmdlist.extend([
            '-E',                  # don't use a saved environment, always read all files
            ])
    if 1:
        cmdlist.extend([
            '-b ' + builder,       # builder to use; default is html
            '-c ' + confpy_folder, # path where configuration file(conf.py) is located (default: same as sourcedir)
            #'-d ' + doctree_folder,# path for the cached environment and doctree files (default: outdir /.doctrees)
            '-n',                  # nit-picky mode, warn about all missing references
            '-N',                  # do not emit colored output
            '-T',                  # show full traceback on exception
            '-w ' + warnings_file, # write warnings (and errors) to given file
            SYMLINK_THE_PROJECT,   # need a stable name for Sphinx caching
            SYMLINK_THE_OUTPUT     # # need a stable name for Sphinx caching
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


if exitcode == CONTINUE:
    # Now, since Sphinx has written directly to the Cachedir, we fetch that
    # result since the Toolchain is expecting that
    # copy folder 'outdir_in_cache' as 'outdir'
    cmdlist = [
        'rsync', '-a', '--delete',
        '--exclude=".doctrees"',
        '"%s"' % outdir_in_cache,
        '"%s/"' % TheProjectBuild ]
    exitcode, cmd, out, err = execute_cmdlist(cmdlist, cwd=workdir)

if exitcode == CONTINUE:
    fname = 'Settings.dump.json'
    src = ospj(TheProjectMakedir, fname)
    if ospe(src):
        settings_dump_json_file = ospj(workdir, fname)
        shutil.copy(src, settings_dump_json_file)

if exitcode == CONTINUE:
    if settings_dump_json_file:
        with codecs.open(settings_dump_json_file, 'r', 'utf-8') as f1:
            conf_py_settings = json.load(f1)

# ==================================================
# Set MILESTONE
# --------------------------------------------------

# only if successfull
if exitcode == CONTINUE:
    builds_successful = milestones.get('builds_successful', [])
    builds_successful.append('html')
    result['MILESTONES'].append({
        'build_html': 'success',
        'builds_successful': builds_successful,
        'build_' + builder + '_folder': outdir,
    })

if documentation_folder_for_sphinx:
    result['MILESTONES'].append({'documentation_folder_for_sphinx':
                                 documentation_folder_for_sphinx})

if settings_dump_json_file:
    result['MILESTONES'].append({'settings_dump_json_file':
                                 settings_dump_json_file})

if conf_py_settings:
    result['MILESTONES'].append({'conf_py_settings':
                                 conf_py_settings})


# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)


# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
