#!/usr/bin/env python
# coding: utf-8

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
from __future__ import absolute_import

import os
import shutil
import sys
import tct

VERSION = '2.7.0'

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

lockfiles_removed = []
removed_dirs = []
toolchain_actions = lookup(params, 'toolchain_actions', default=[])
xeq_name_cnt = 0


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    lockfile_name = lookup(milestones, 'lockfile_name')
    run_id = lookup(facts, 'run_id')
    toolchain_temp_home = lookup(params, 'toolchain_temp_home')
    if not (lockfile_name and run_id and toolchain_temp_home):
        exitcode = 22

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('PROBLEM with required params')


# =========================================================
# Prepare for a subprocess with perfect logging
# ---------------------------------------------------------

if exitcode == CONTINUE:

    import codecs
    import os
    import subprocess

    def cmdline(cmd, cwd=None):
        if cwd is None:
            cwd = os.getcwd()
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=cwd)
        out, err = process.communicate()
        exitcode = process.returncode
        return exitcode, cmd, out, err


    def execute_cmdlist(cmdlist):
        global xeq_name_cnt
        cmd = ' '.join(cmdlist)
        cmd_multiline = ' \\\n   '.join(cmdlist) + '\n'
        exitcode, cmd, out, err = cmdline(cmd, cwd=workdir)
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

    # exitcode, cmd, out, err = execute_cmdlist(cmdlist)

# ==================================================
# work
# --------------------------------------------------


if exitcode == CONTINUE:
    if 'version' in toolchain_actions:
        print(VERSION)
        exitcode = 90

if exitcode == CONTINUE:
    if 'unlock' in toolchain_actions:
        for top, dirs, files in os.walk(toolchain_temp_home):
            dirs[:] = [] # stop recursion
            for fname in files:
                if fname == lockfile_name:
                    lockfile = os.path.join(top, fname)
                    os.remove(lockfile)
                    lockfiles_removed.append(lockfile)
        exitcode = 90

if exitcode == CONTINUE:
    if 'clean' in toolchain_actions:
        for top, dirs, files in os.walk(toolchain_temp_home):
            dirs.sort()
            for adir in dirs:
                fpath = os.path.join(top, adir)
                if not run_id in adir:
                    if os.path.isdir(fpath):
                        shutil.rmtree(fpath)
            dirs[:] = [] # stop recursion
        exitcode = 90


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if exitcode == 90:
    result['MILESTONES'].append({'FINAL_EXITCODE': 0})

if lockfiles_removed:
    result['MILESTONES'].append({'lockfiles_removed': lockfiles_removed})



# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
