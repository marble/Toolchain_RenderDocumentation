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

from tct import deepget

params = tct.readjson(sys.argv[1])
facts = tct.readjson(params['factsfile'])
milestones = tct.readjson(params['milestonesfile'])
resultfile = params['resultfile']
result = tct.readjson(resultfile)
toolname = params['toolname']
toolname_pure = params['toolname_pure']
toolchain_name = facts['toolchain_name']
workdir = params['workdir']
loglist = result['loglist'] = result.get('loglist', [])
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

included_files_check_is_ok = 0
included_files_check_logfile = None
included_files_check_logfile_dumped_to_stdout = None
xeq_name_cnt = 0


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    disable_include_files_check = lookup(milestones,
                                         'disable_include_files_check',
                                         default=0)

    if disable_include_files_check:
        CONTINUE = -2

if exitcode == CONTINUE:
    documentation_folder = lookup(milestones, 'documentation_folder')
    masterdoc = lookup(milestones, 'masterdoc')
    TheProjectLog = lookup(milestones, 'TheProjectLog')
    toolfolderabspath = lookup(params, 'toolfolderabspath')
    workdir = lookup(params, 'workdir')

    if not (documentation_folder and masterdoc and TheProjectLog and
            toolfolderabspath and workdir):
        CONTINUE = -2

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('Bad PARAMS or nothing to do')


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
        out, err = process.communicate()
        exitcode = process.returncode
        return exitcode, cmd, out, err

if exitcode == CONTINUE:
    cmdlist = [
        facts['python_exe_abspath'],
        os.path.join(toolfolderabspath, 'check_include_files.py'),
        '--verbose',
        documentation_folder,
    ]
    cmd = ' '.join(cmdlist)
    cmd_multiline = ' \\\n   '.join(cmdlist) + '\n'

    exitcode, cmd, out, err = cmdline(cmd, cwd=workdir)
    if exitcode == 0:
        included_files_check_is_ok = 1

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

    included_files_check_logfile = os.path.join(TheProjectLog, ('%s.txt' %
                                                                toolname_pure))
    with codecs.open(included_files_check_logfile, 'w', 'utf-8') as f2:
        f2.write(out.decode('utf-8', 'replace'))


if (exitcode != 0) and included_files_check_logfile:
    with codecs.open(included_files_check_logfile, 'r', 'utf-8') as f1:
        for line in f1:
            print(line, end='')
    included_files_check_logfile_dumped_to_stdout = 1


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if included_files_check_is_ok:
    result['MILESTONES'].append({'included_files_check_is_ok':
                                 included_files_check_is_ok})
if included_files_check_logfile:
    result['MILESTONES'].append({'included_files_check_logfile':
                                 included_files_check_logfile})
if included_files_check_logfile_dumped_to_stdout:
    result['MILESTONES'].append({
        'included_files_check_logfile_dumped_to_stdout':
        included_files_check_logfile_dumped_to_stdout})

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)


# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
