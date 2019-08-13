#!/usr/bin/env python
# coding: utf-8

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
from __future__ import absolute_import
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

deepget = tct.deepget

def lookup(D, *keys, **kwdargs):
    result = deepget(D, *keys, **kwdargs)
    loglist.append((keys, result))
    return result


# ==================================================
# define
# --------------------------------------------------

makepdf_exitcode = None
xeq_name_cnt = 0


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    make_pdf = lookup(milestones, 'make_pdf')

    if not make_pdf:
        loglist.append('Nothing to do: make_pdf is not requested.')
        CONTINUE = -2

if exitcode == CONTINUE:
    latex_file_folder = lookup(milestones, 'latex_file_folder')
    latex_file_tweaked = lookup(milestones, 'latex_file_tweaked')
    latex_make_file_tweaked  = lookup(milestones, 'latex_make_file_tweaked')

    if not (latex_file_folder and latex_file_tweaked and
            latex_make_file_tweaked and toolname):
        loglist.append('parameters not sufficient')
        CONTINUE = -2

if exitcode == CONTINUE:
    latex = lookup(milestones, 'known_systemtools', 'latex')
    pdflatex = lookup(milestones, 'known_systemtools', 'pdflatex')
    latexmk = lookup(milestones, 'known_systemtools', 'latexmk')
    if not (latex or pdflatex or latexmk):
        loglist.append('It seems the LaTeX PDF builder is not available.')
        CONTINUE = -2

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('PROBLEMS with params')

# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:

    import codecs
    import subprocess

    workdir = params['workdir']

    def cmdline(cmd, cwd=None):
        if cwd is None:
            cwd = os.getcwd()
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=cwd)
        out, err = process.communicate()
        exitcode = process.returncode
        return exitcode, cmd, out, err

    cmd = 'make -C "' + latex_file_folder + '" all-pdf'


    xeq_name_cnt += 1
    filename_cmd = 'xeq-%s-%d-%s.txt' % (toolname_pure, xeq_name_cnt, 'cmd')
    filename_err = 'xeq-%s-%d-%s.txt' % (toolname_pure, xeq_name_cnt, 'err')
    filename_out = 'xeq-%s-%d-%s.txt' % (toolname_pure, xeq_name_cnt, 'out')

    with codecs.open(os.path.join(workdir, filename_cmd), 'w', 'utf-8') as f2:
        f2.write(cmd.decode('utf-8', 'replace'))


    exitcode, cmd, out, err = cmdline(cmd, cwd=latex_file_folder)

    if exitcode:
        # a makepdf failure should not affect the final_exitcode
        makepdf_exitcode = exitcode
        exitcode = 0
        CONTINUE = -2


    loglist.append([exitcode, cmd.decode('utf-8', 'replace'), out.decode('utf-8', 'replace'), err.decode('utf-8', 'replace')])

    with codecs.open(os.path.join(workdir, filename_out), 'w', 'utf-8') as f2:
        f2.write(out.decode('utf-8', 'replace'))

    with codecs.open(os.path.join(workdir, filename_err), 'w', 'utf-8') as f2:
        f2.write(err.decode('utf-8', 'replace'))

if exitcode == CONTINUE:

    PROJECT_pdf_file = os.path.join(latex_file_folder, 'PROJECT.pdf')
    if os.path.exists(PROJECT_pdf_file):
        pdf_file = PROJECT_pdf_file

    PROJECT_log_file = os.path.join(latex_file_folder, 'PROJECT.log')
    if os.path.exists(PROJECT_log_file):
        pdf_log_file = PROJECT_log_file


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if exitcode == CONTINUE:
    builds_successful = milestones.get('builds_successful', [])
    builds_successful.append('pdf')
    result['MILESTONES'].append({
        'pdf_file': pdf_file,
        'pdf_log_file': pdf_log_file,
        'build_pdf': 'success',
        'builds_successful': builds_successful,
    })

if makepdf_exitcode is not None:
    result['MILESTONES'].append({'makepdf_exitcode': makepdf_exitcode})

# ==================================================
# save result
# --------------------------------------------------

if exitcode == CONTINUE:

    import pprint

    with codecs.open(resultfile + '.pprinted.txt', 'w', 'utf-8', 'replace') as f2:
        pprint.pprint(result, f2)

    tct.save_the_result(result, resultfile, params, facts, milestones, exitcode, CONTINUE)


# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
