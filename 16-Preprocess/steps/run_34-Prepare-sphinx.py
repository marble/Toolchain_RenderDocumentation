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
    buildsettings_file_fixed = milestones_get('buildsettings_file_fixed')
    makedir = milestones_get('makedir')
    masterdoc = milestones_get('masterdoc')
    TheProject = milestones.get('TheProject')

    if not (buildsettings_file_fixed and makedir and masterdoc and TheProject):
        exitcode = 2

if exitcode == CONTINUE:
    has_settingscfg = milestones.get('has_settingscfg')
    ready_for_build = False
    ready_for_build_vars = None
    rebuild_needed = milestones.get('rebuild_needed')
    SPHINXBUILD = None
    TheProjectBuild = None
    TheProjectLog = None

# ==================================================
# work
# --------------------------------------------------

import subprocess

def cmdline(cmd, cwd=None):
    if cwd is None:
        cwd = os.getcwd()
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=cwd)
    out, err = process.communicate()
    exitcode = process.returncode
    return exitcode, cmd, out, err


if exitcode == CONTINUE:

    if not TheProjectLog:
        TheProjectLog = TheProject + 'Log'
        if not os.path.exists(TheProjectLog):
            os.makedirs(TheProjectLog)

    if not TheProjectBuild:
        TheProjectBuild = TheProject + 'Build'
        if not os.path.exists(TheProjectBuild):
            os.makedirs(TheProjectBuild)

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

if exitcode == CONTINUE:
    if TheProjectBuild:
        result['MILESTONES'].append({'TheProjectBuild': TheProjectBuild })
    if TheProjectLog:
        result['MILESTONES'].append({'TheProjectLog': TheProjectLog})
    if TheProjectLog:
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
