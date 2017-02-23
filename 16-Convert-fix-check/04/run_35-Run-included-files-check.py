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
# Make a copy of milestones for later inspection?
# --------------------------------------------------

if 0 or milestones.get('debug_always_make_milestones_snapshot'):
    tct.make_snapshot_of_milestones(params['milestonesfile'], sys.argv[1])


# ==================================================
# Get and check required milestone(s)
# --------------------------------------------------

def milestones_get(name, default=None):
    result = milestones.get(name, default)
    loglist.append((name, result))
    return result

def facts_get(name, default=None):
    result = facts.get(name, default)
    loglist.append((name, result))
    return result

def params_get(name, default=None):
    result = params.get(name, default)
    loglist.append((name, result))
    return result


# ==================================================
# define
# --------------------------------------------------

pass


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    documentation_folder = milestones_get('documentation_folder')
    masterdoc = milestones_get('masterdoc')
    TheProjectLog = milestones_get('TheProjectLog')
    workdir = params.get('workdir')
    loglist.append(('workdir', workdir))

    if not (documentation_folder and masterdoc and TheProjectLog and workdir):
        CONTINUE = -1

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('PROBLEM with required params')


# ==================================================
# work
# --------------------------------------------------

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
    cmd = 'check_include_files.py --verbose ' + documentation_folder
    this_exitcode, cmd, out, err = cmdline(cmd)
    loglist.append('exitcode of check_include_files: %s' % this_exitcode)

    with codecs.open(os.path.join(workdir, 'cmd-01-stdout.txt'), 'w', 'utf-8') as f2:
        f2.write(out)

    with codecs.open(os.path.join(workdir, 'cmd-01-stderr.txt'), 'w', 'utf-8') as f2:
        f2.write(err)


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if exitcode == CONTINUE:
    if this_exitcode == 0:
        result['MILESTONES'].append('included_files_check')


# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)


# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
