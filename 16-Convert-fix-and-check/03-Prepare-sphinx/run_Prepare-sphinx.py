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
toolname_pure = params['toolname_pure']
workdir = params['workdir']
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

ready_for_build = False
ready_for_build_vars = None
SPHINXBUILD = None


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')
    buildsettings_file_fixed = milestones_get('buildsettings_file_fixed')
    makedir = milestones_get('makedir')
    masterdoc = milestones_get('masterdoc')
    TheProject = milestones_get('TheProject')
    TheProjectBuild = milestones_get('TheProjectBuild')
    TheProjectLog = milestones_get('TheProjectLog')

    if not (buildsettings_file_fixed and makedir and masterdoc and TheProject
            and TheProjectBuild and TheProjectLog):
        exitcode = 22

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('PROBLEM with params')

# ==================================================
# work
# --------------------------------------------------

import subprocess

if exitcode == CONTINUE:
    has_settingscfg = milestones_get('has_settingscfg')
    rebuild_needed = milestones_get('rebuild_needed')

def cmdline(cmd, cwd=None):
    if cwd is None:
        cwd = os.getcwd()
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=cwd)
    out, err = process.communicate()
    exitcode = process.returncode
    return exitcode, cmd, out, err

if exitcode == CONTINUE:

    if not SPHINXBUILD:
        this_exitcode, cmd, out, err = cmdline('which sphinx-build')
        SPHINXBUILD = out.strip()
        loglist.append([this_exitcode, cmd, out, err])

    if 'just a test':
        this_exitcode, cmd, out, err = cmdline('sphinx-build --help')
        loglist.append([this_exitcode, cmd, out, err])

    ready_for_build_vars = [TheProject, TheProjectBuild, TheProjectLog, SPHINXBUILD, makedir, masterdoc, buildsettings_file_fixed]
    ready_for_build_vars_str = '[TheProject, TheProjectBuild, TheProjectLog, SPHINXBUILD, makedir, masterdoc, buildsettings_file_fixed]'

    loglist.append({'ready_for_build_vars_str': ready_for_build_vars_str,
                    'ready_for_build_vars': ready_for_build_vars})

    # All variables set (!= False)?
    ready_for_build = not any([not v for v in ready_for_build_vars])


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if SPHINXBUILD:
    result['MILESTONES'].append({'SPHINXBUILD': SPHINXBUILD})

if ready_for_build:
    result['MILESTONES'].append({'ready_for_build': ready_for_build})

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
