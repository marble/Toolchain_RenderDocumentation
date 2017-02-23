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

locale_folders = []
locale_locales = []
locale_masterdocs = []

masterdoc_candidates = [
    'Documentation/Index.rst',
    'Documentation/index.rst',
    'Documentation/Index.md',
    'Documentation/index.md',
    'README.rst',
    'README.md',
    'doc/manual.pdf',
    'doc/manual.sxw',
]
masterdoc_selected = {}
masterdocs_initial = {}
xeq_name_cnt = 0


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')
    gitdir = tct.deepget(milestones, 'buildsettings', 'gitdir')
    if not gitdir:
        exitcode = 2

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('PROBLEM with params')

if CONTINUE != 0:
    loglist.append({'CONTINUE': CONTINUE})
    loglist.append('NOTHING to do')


# ==================================================
# work
# --------------------------------------------------

import glob
import re

if exitcode == CONTINUE:
    loglist.append({'masterdoc_candidates': masterdoc_candidates})
    locale = 'default'
    for candidate in masterdoc_candidates:
        fpath = os.path.join(gitdir, candidate)
        if os.path.exists(fpath):
            masterdocs_initial[candidate] = True
            if not masterdoc_selected.get(locale):
                masterdoc_selected[locale] = candidate
        else:
            masterdocs_initial[candidate] = False

if exitcode == CONTINUE:
    top = os.path.join(gitdir, 'Documentation', 'Localization.??_??')

    candidates = glob.glob(top)
    # [u'/home/marble/Repositories/git.typo3.org/TYPO3CMS/Extensions/sphinx/Documentation/Localization.fr_FR']

    for candidate in candidates:
        m = re.search('(?P<folder>Localization\.(?P<locale>[a-z][a-z]_[A-Z][A-Z]))$', candidate, re.UNICODE)
        if m:
            folder = m.groupdict()['folder']
            locale = m.groupdict()['locale']
            locale_for_file = locale.lower().replace('_', '-')

            locale_folders.append(folder)
            locale_locales.append(locale)

            for candi in masterdoc_candidates:
                if not masterdoc_selected.get(locale):
                    a = candi.split('/')
                    if len(a) > 1 and a[0] == 'Documentation':
                        fpath = os.path.join(gitdir, a[0], folder, a[1])
                        if os.path.exists(fpath):
                            masterdoc_selected[locale] = os.path.join(a[0], folder, a[1])
                            locale_masterdocs.append(masterdoc_selected[locale])


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if 1:
    result['MILESTONES'].append({
        'locale_folders': locale_folders,
        'locale_locales': locale_locales,
        'locale_masterdocs': locale_masterdocs,
    })

if masterdoc_candidates:
    result['MILESTONES'].append({
        'masterdoc_candidates': masterdoc_candidates,
    })

if masterdocs_initial:
    result['MILESTONES'].append({
        'masterdocs_initial': masterdocs_initial,
    })

if masterdoc_selected:
    result['MILESTONES'].append({
        'masterdoc_selected': masterdoc_selected,
    })


# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
