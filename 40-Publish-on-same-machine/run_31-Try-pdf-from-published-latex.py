#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function
from __future__ import absolute_import

import codecs
import os
import subprocess
import shutil
import sys
import tct

from os.path import join as ospj, exists as ospe

params = tct.readjson(sys.argv[1])
binabspath = sys.argv[2]
facts = tct.readjson(params['factsfile'])
milestones = tct.readjson(params['milestonesfile'])
resultfile = params['resultfile']
reason = ''
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

pdf_files_from_published_latex = []
publish_dir_pdf = None
make_pdf_script_to_execute = None
xeq_name_cnt = 0


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    make_pdf = lookup(milestones, 'make_pdf')
    publish_dir_latex = lookup(milestones, 'publish_dir_latex')
    run_latex_make_sh_file = lookup(milestones, 'run_latex_make_sh_file')
    try_pdf_build_from_published_latex = lookup(milestones,
                                                'try_pdf_build_from_published_'
                                                'latex')

    if not (1
            and make_pdf
            and publish_dir_latex
            and try_pdf_build_from_published_latex
            and run_latex_make_sh_file
    ):
        CONTINUE = -2

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('PROBLEM with required params')


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
        bstdout, bstderr = process.communicate()
        exitcode2 = process.returncode
        return exitcode2, cmd, bstdout, bstderr

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

        if 0 and 'activateLocalSphinxDebugging':
            if cmdlist[0] == 'sphinx-build':
                from sphinx.cmd.build import main as sphinx_cmd_build_main
                sphinx_cmd_build_main(cmdlist[1:])
                exitcode, cmd, out, err = 99, cmd, b'', b''
        else:
            exitcode, cmd, out, err = cmdline(cmd, cwd=cwd)

        loglist.append({'exitcode': exitcode, 'cmd': cmd, 'out': out, 'err': err})

        with codecs.open(ospj(workdir, filename_out), 'w', 'utf-8') as f2:
            f2.write(out.decode('utf-8', 'replace'))

        with codecs.open(ospj(workdir, filename_err), 'w', 'utf-8') as f2:
            f2.write(err.decode('utf-8', 'replace'))

        return exitcode, cmd, out, err


if exitcode == CONTINUE:

    make_pdf_script_to_execute = os.path.join(publish_dir_latex,
                                              os.path.basename(run_latex_make_sh_file))
    workdir = publish_dir_latex

    exitcode, cmd, out, err = execute_cmdlist([make_pdf_script_to_execute],
                                              cwd=workdir)

if exitcode == CONTINUE:
   publish_dir_pdf = os.path.normpath(os.path.join(publish_dir_latex, '..', 'pdf'))
   if not ospe(publish_dir_pdf):
       os.makedirs(publish_dir_pdf)
   for fname in os.listdir(publish_dir_latex):
       if fname.endswith('.pdf'):
           destfile = os.path.join(publish_dir_pdf, fname)
           shutil.copy2(os.path.join(publish_dir_latex, fname),
                        destfile)
           pdf_files_from_published_latex.append(destfile)

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if make_pdf_script_to_execute:
    result['MILESTONES'].append({'make_pdf_script_to_execute':
                                 make_pdf_script_to_execute})
if pdf_files_from_published_latex:
    result['MILESTONES'].append({'pdf_files_from_published_latex':
                                 pdf_files_from_published_latex})

if publish_dir_pdf:
    result['MILESTONES'].append({'publish_dir_pdf':
                                 publish_dir_pdf})

# ==================================================
# save result
# --------------------------------------------------

tct.save_the_result(result, resultfile, params, facts, milestones, exitcode, CONTINUE, reason)


# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
