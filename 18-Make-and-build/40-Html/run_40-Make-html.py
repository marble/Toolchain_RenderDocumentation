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

def lookup(D, *keys, **kwdargs):
    result = tct.deepget(D, *keys, **kwdargs)
    loglist.append((keys, result))
    return result


# ==================================================
# define
# --------------------------------------------------

xeq_name_cnt = 0
documentation_folder_for_sphinx = ''


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    # required milestones
    requirements = []

    # just test
    for requirement in requirements:
        v = lookup(milestones, requirement)
        if not v:
            loglist.append("'%s' not found" % requirement)
            exitcode = 2

    # fetch
    included_files_check_is_ok = lookup(milestones, 'included_files_check_is_ok')
    ready_for_build = lookup(milestones, 'ready_for_build')
    rebuild_needed = lookup(milestones, 'rebuild_needed')
    toolname = lookup(params, 'toolname')
    toolname_pure = lookup(params, 'toolname_pure')

    # test
    if not (included_files_check_is_ok and ready_for_build and
            rebuild_needed and toolname and toolname_pure):
        exitcode = 2
    else:
        loglist.append('ok, check more params')

if exitcode == CONTINUE:

    masterdoc = lookup(milestones, 'masterdoc')
    SPHINXBUILD = lookup(milestones, 'SPHINXBUILD')
    TheProject = lookup(milestones, 'TheProject')
    TheProjectBuild = lookup(milestones, 'TheProjectBuild')
    TheProjectLog = lookup(milestones, 'TheProjectLog')
    TheProjectMakedir = lookup(milestones, 'TheProjectMakedir')

    if not (masterdoc and SPHINXBUILD and
            TheProject and TheProjectBuild and TheProjectLog and TheProjectMakedir):
        exitcode = 2

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

    import codecs
    import subprocess

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
        exitcode, cmd, out, err = cmdline(cmd, cwd=cwd)
        loglist.append({'exitcode': exitcode, 'cmd': cmd, 'out': out, 'err': err})
        xeq_name_cnt += 1
        filename_cmd = 'xeq-%s-%d-%s.txt' % (toolname_pure, xeq_name_cnt, 'cmd')
        filename_err = 'xeq-%s-%d-%s.txt' % (toolname_pure, xeq_name_cnt, 'err')
        filename_out = 'xeq-%s-%d-%s.txt' % (toolname_pure, xeq_name_cnt, 'out')

        with codecs.open(os.path.join(workdir, filename_cmd), 'w', 'utf-8') as f2:
            f2.write(cmd_multiline.decode('utf-8', 'replace'))

        with codecs.open(os.path.join(workdir, filename_out), 'w', 'utf-8') as f2:
            f2.write(out.decode('utf-8', 'replace'))

        with codecs.open(os.path.join(workdir, filename_err), 'w', 'utf-8') as f2:
            f2.write(err.decode('utf-8', 'replace'))

        return exitcode, cmd, out, err


if exitcode == CONTINUE:
    builder = 'html'
    sourcedir = documentation_folder_for_sphinx
    outdir = build_builder_folder = os.path.join(TheProjectBuild, builder)
    warnings_file_folder = os.path.join(TheProjectLog, builder)
    warnings_file = os.path.join(warnings_file_folder, 'warnings.txt')
    doctree_folder = os.path.join(TheProjectBuild, 'doctree', builder)
    confpy_folder = TheProjectMakedir

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

    exitcode, cmd, out, err = execute_cmdlist(cmdlist, cwd=workdir)

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
