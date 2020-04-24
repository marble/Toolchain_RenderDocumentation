#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function
from __future__ import absolute_import

import codecs
import os
import subprocess
import sys
import tct

from tct import deepget
from os.path import join as ospj, exists as ospe

params = tct.readjson(sys.argv[1])
facts = tct.readjson(params['factsfile'])
milestones = tct.readjson(params['milestonesfile'])
reason = ''
resultfile = params['resultfile']
result = tct.readjson(resultfile)
toolname = params['toolname']
toolname_pure = params['toolname_pure']
toolchain_name = facts['toolchain_name']
workdir = params['workdir']
loglist = result['loglist'] = result.get('loglist', [])
initial_working_dir = facts['initial_working_dir']
exitcode = CONTINUE = 0


# ==================================================0
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

gitloginfo_json_file = None
xeq_name_cnt = 0


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    gitdir = lookup(milestones, 'buildsettings', 'gitdir')
    TheProjectMakedir = lookup(milestones, 'TheProjectMakedir')

    if not (1
        and gitdir
        and TheProjectMakedir
    ):
        CONTINUE = -2
        reason = 'Bad PARAMS or nothing to do'

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('Bad PARAMS or nothing to do')


# ==================================================
# functions
# --------------------------------------------------

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


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:

    scriptfile = ospj(params['toolfolderabspath'], 'git-restore-mtime/git-restore-mtime-modified.py')
    jsonfile = ospj(TheProjectMakedir, 'gitloginfo.json')
    cmdlist = [
        'python',
        scriptfile,
        '--test', # don't touch files
        '--no-directories', # unnotably faster
        '--destfile-gitloginfo=' + jsonfile,
        '.'
        ]

    exitcode, cmd, out, err = execute_cmdlist(cmdlist, cwd=gitdir)

if exitcode == CONTINUE:
    gitloginfo_jsonfile = jsonfile


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if gitloginfo_json_file:
    result['MILESTONES'].append({'gitloginfo_json_file':
                                 gitloginfo_json_file})


# ==================================================
# save result
# --------------------------------------------------

tct.save_the_result(result, resultfile, params, facts, milestones, exitcode, CONTINUE, reason)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
