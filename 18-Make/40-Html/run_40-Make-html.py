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
# Get and check required milestone(s)
# --------------------------------------------------
def milestones_get(name, default=None):
    result = milestones.get(name, default)
    loglist.append((name, result))
    return result

if exitcode == CONTINUE:
    ready_for_build = milestones_get('ready_for_build')
    rebuild_needed = milestones_get('rebuild_needed')
    included_files_check = milestones_get('included_files_check')
    if not (ready_for_build and rebuild_needed and included_files_check):
        exitcode = 2

if exitcode == CONTINUE:
    masterdoc = milestones.get('masterdoc')
    has_settingscfg = milestones.get('has_settingscfg')
    TheProject = milestones.get('TheProject')
    TheProjectLog = milestones.get('TheProjectLog')
    TheProjectBuild = milestones.get('TheProjectBuild')
    TheProjectMakedir = milestones.get('TheProjectMakedir')
    SPHINXBUILD = milestones.get('SPHINXBUILD')

# ==================================================
# work
# --------------------------------------------------

# CONTINUE = -1

if exitcode == CONTINUE:

    import codecs
    import subprocess

    def cmdline(cmd, cwd=None):
        if cwd is None:
            cwd = os.getcwd()
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=cwd)
        out, err = process.communicate()
        exitcode = process.returncode
        return exitcode, cmd, out, err

if exitcode == CONTINUE:
    builder = 'html'
    sourcedir = milestones['documentation_folder']
    outdir = build_builder_folder = os.path.join(TheProjectBuild, builder)
    warnings_file_folder = os.path.join(TheProjectLog, builder)
    warnings_file = os.path.join(warnings_file_folder, 'warnings.txt')
    doctree_folder = os.path.join(TheProjectBuild, 'doctree', builder)
    confpy_folder = TheProjectMakedir
    workdir = params['workdir']
    loglist.append(['workdir', workdir])

    if not os.path.exists(warnings_file_folder):
        os.makedirs(warnings_file_folder)

    cmdlist = [
        'sphinx-build',
        '-a',                  # write all files; default is to only write new and changed files
        '-b ' + builder,       # builder to use; default is html
        '-c ' + confpy_folder, # path where configuration file(conf.py) is located (default: same as sourcedir)
        '-d ' + doctree_folder,# path for the cached environment and doctree files (default: outdir /.doctrees)
        '-E',                  # don't use a saved environment, always read all files
        '-n',                  # nit-picky mode, warn about all missing references
        '-T',                  # show full traceback on exception
        '-w ' + warnings_file, # write warnings (and errors) to given file
        sourcedir,
        outdir
    ]
    cmd = ' '.join(cmdlist)
    cmd_multiline = ' \\\n   '.join(cmdlist) + '\n'

    exitcode, cmd, out, err = cmdline(cmd, cwd=workdir)

    loglist.append([exitcode, cmd, out, err])
    with codecs.open(os.path.join(workdir, 'cmd-01-cmd.txt'), 'w', 'utf-8') as f2:
        f2.write(cmd_multiline)
    with codecs.open(os.path.join(workdir, 'cmd-01-stdout.txt'), 'w', 'utf-8') as f2:
        f2.write(out)
    with codecs.open(os.path.join(workdir, 'cmd-01-stderr.txt'), 'w', 'utf-8') as f2:
        f2.write(err)



# ==================================================
# Set MILESTONE
# --------------------------------------------------

if exitcode == CONTINUE:
    builds_successful = milestones.get('builds_successful', [])
    builds_successful.append('html')
    result['MILESTONES'].append({
        'build_html': 'success',
        'builds_successful': builds_successful,
        'build_' + builder + '_folder': build_builder_folder,
    })

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
