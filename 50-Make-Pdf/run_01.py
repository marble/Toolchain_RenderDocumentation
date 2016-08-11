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
errormsg = ''
helpmsg = ''

# ==================================================
# Check required milestone(s)
# --------------------------------------------------
if exitcode == CONTINUE:
    latex_file_folder = milestones.get('latex_file_folder')
    latex_file_tweaked = milestones.get('latex_file_tweaked')
    latex_make_file_tweaked  = milestones.get('latex_make_file_tweaked')

    loglist.append(['latex_file_folder', latex_file_folder])
    loglist.append(['latex_file_tweaked', latex_file_tweaked])
    loglist.append(['latex_make_file_tweaked', latex_make_file_tweaked])

if not (latex_file_folder and latex_file_tweaked and latex_make_file_tweaked):
        CONTINUE = -1

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

    exitcode, cmd, out, err = cmdline(cmd, cwd=workdir)

    loglist.append([exitcode, cmd, out, err])
    with codecs.open(os.path.join(workdir, 'cmd-01-cmd.txt'   ), 'wb', 'utf-8') as f2:
        f2.write(cmd)
    with codecs.open(os.path.join(workdir, 'cmd-01-stdout.txt'), 'wb', 'utf-8') as f2:
        f2.write(out.decode('utf-8', errors='replace'))
    with codecs.open(os.path.join(workdir, 'cmd-01-stderr.txt'), 'wb', 'utf-8') as f2:
        f2.write(err.decode('utf-8', errors='replace'))

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

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
