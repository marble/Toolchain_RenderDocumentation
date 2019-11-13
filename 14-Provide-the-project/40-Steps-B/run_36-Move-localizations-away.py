#!/usr/bin/env python

from __future__ import print_function
from __future__ import absolute_import
import os
import tct
import sys

# special
import glob
import shutil

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

localization_folder_names = []  # ['Localization.de_DE']
localization_folders = []
localization_locales = []       # ['de_DE', 'en_US']
localization_pattern = None
TheProjectLocalization = None


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    TheProject = lookup(milestones, 'TheProject')
    localization_has_localization = lookup(milestones, 'localization_has_localization')
    if not (TheProject and localization_has_localization):
        CONTINUE = -2
        reason = 'Bad PARAMS or nothing to do'

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('Bad PARAMS or nothing to do')


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    localization = tct.deepget(milestones, 'buildsettings', 'localization', default='')
    if localization not in ['', 'default']:
        reason = 'Nothing to move away, because we want to render the localized version.'
        loglist.append((reason, localization))
        CONTINUE = -2

if exitcode == CONTINUE:
    TheProjectLocalization = TheProject + 'Localization'

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

if localization_folder_names:    result['MILESTONES'].append(
    {'localization_folder_names': localization_folder_names})

if localization_folders:    result['MILESTONES'].append(
    {'localization_folders': localization_folders})

if localization_locales:    result['MILESTONES'].append(
    {'localization_locales': localization_locales})

if localization_pattern:    result['MILESTONES'].append(
    {'localization_pattern': localization_pattern})

if TheProjectLocalization:    result['MILESTONES'].append(
    {'TheProjectLocalization': TheProjectLocalization})


# ==================================================
# save result
# --------------------------------------------------

tct.save_the_result(result, resultfile, params, facts, milestones, exitcode, CONTINUE, reason)


# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
