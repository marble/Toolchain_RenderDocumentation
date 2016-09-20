#!/usr/bin/env python

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
# define
# --------------------------------------------------

localization_folders = []
localization_locales = []       # ['de_DE', 'en_US']
localization_folder_names = []  # ['Localization.de_DE']

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

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')
    toolchain_name = params_get('toolchain_name')
    if not toolchain_name:
        exitcode = 99

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('PROBLEM with params')

# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    localization_has_localization = milestones_get('localization_has_localization')
    if not localization_has_localization:
        loglist.append('nothing to do - no localization found')
        CONTINUE = -1

if exitcode == CONTINUE:
    localization = tct.deepget(milestones, 'buildsettings', 'localization', default=None)
    if localization:
        loglist.append("nothing to do - we do want to render localization '%s'" % localization)
        CONTINUE = -1

# ==================================================
# work
# --------------------------------------------------

import glob
import shutil

if exitcode == CONTINUE:
    TheProject = milestones['TheProject']
    TheProjectLocalization = TheProject + 'Localization'

if exitcode == CONTINUE:
    if not os.path.exists(TheProjectLocalization):
        os.makedirs(TheProjectLocalization)

    localization_pattern = TheProject + '/Documentation/Localization.*'
    localization_folders = glob.glob(localization_pattern)
    for folder in localization_folders:
        shutil.move(folder, TheProjectLocalization)
        localization_folder_name = os.path.split(folder)[1]
        localization_folder_names.append(localization_folder_name)
        localization_locales.append(localization_folder_name[len('Localization.'):])

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if exitcode == CONTINUE:
    result['MILESTONES'].append({'TheProjectLocalization': TheProjectLocalization})

    if localization_folders:
        result['MILESTONES'].append({'localization_folders': localization_folders})

    if localization_pattern:
        result['MILESTONES'].append({'localization_pattern': localization_pattern})

    if localization_folder_names:
        result['MILESTONES'].append({'localization_folder_names': localization_folder_names})

    if localization_locales:
        result['MILESTONES'].append({'localization_locales': localization_locales})

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
