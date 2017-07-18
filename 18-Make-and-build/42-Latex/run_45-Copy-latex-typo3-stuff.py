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

xeq_name_cnt = 0
copied_latex_resources = []


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    configset = milestones_get('configset')

    if not configset:
        exitcode = 22

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('PROBLEMS with params')

if CONTINUE != 0:
    loglist.append({'CONTINUE': CONTINUE})
    loglist.append('NOTHING to do')


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    make_latex = params_get('make_latex')
    if not make_latex:
        CONTINUE == -2

if exitcode == CONTINUE:
    build_latex = milestones_get('build_latex')
    build_latex_folder = milestones_get('build_latex_folder')
    latex_contrib_typo3_folder = tct.deepget(facts, 'tctconfig', configset, 'latex_contrib_typo3_folder')
    loglist.append(('latex_contrib_typo3_folder', latex_contrib_typo3_folder))
    if not (build_latex and build_latex_folder and latex_contrib_typo3_folder):
        CONTINUE = -1

    if CONTINUE != 0:
        loglist.append('not enough info to start')

if exitcode == CONTINUE:
    if not os.path.isdir(latex_contrib_typo3_folder):
        loglist.append(('is not a directory', latex_contrib_typo3_folder))
        exitcode = 22

if exitcode == CONTINUE:

    import shutil

    for thing in os.listdir(latex_contrib_typo3_folder):
        if thing in ['.', '..', 'Makefile']:
            continue
        srcpath = os.path.join(latex_contrib_typo3_folder, thing)
        destpath = os.path.join(build_latex_folder, thing)
        if os.path.isdir(srcpath):
            shutil.copytree(srcpath, destpath)
        else:
            shutil.copy(srcpath, destpath)
        copied_latex_resources.append(thing)


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if copied_latex_resources:
    result['MILESTONES'].append({
        'copied_latex_resources': copied_latex_resources,
    })


# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)


# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
