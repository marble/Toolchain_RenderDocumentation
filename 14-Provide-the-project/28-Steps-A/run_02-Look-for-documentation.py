#!/usr/bin/env python

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
from __future__ import absolute_import
import glob
import os
import re
import sys
import tct

params = tct.readjson(sys.argv[1])
facts = tct.readjson(params['factsfile'])
milestones = tct.readjson(params['milestonesfile'])
resultfile = params['resultfile']
result = tct.readjson(resultfile)
toolname = params['toolname']
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

def lookup(D, *keys, **kwdargs):
    result = tct.deepget(D, *keys, **kwdargs)
    loglist.append((keys, result))
    return result


# ==================================================
# define
# --------------------------------------------------

buildsettings = {}
locale_folders = {'': '', 'default': ''} # 'fr_FR':'Localization.fr_FR'
locale_locales = []
locale_masterdocs = []
localization = 'default'
masterdoc_candidates = [
    'Documentation/Index.rst',
    'Documentation/index.rst',
    'Documentation/Index.md',
    'Documentation/index.md',
    'README.rst',
    'README.md',
    # 'doc/manual.sxw',
    # 'doc/manual.pdf',
]
masterdoc_selected = {}
masterdocs_initial = {}
xeq_name_cnt = 0


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    buildsettings = lookup(milestones, 'buildsettings')
    localization = lookup(milestones, 'buildsettings', 'localization', default='default')
    gitdir = lookup(milestones, 'buildsettings', 'gitdir')
    if not gitdir:
        exitcode = 22

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('Bad PARAMS or nothing to do')


# ==================================================
# work
# --------------------------------------------------

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

            locale_folders[locale] = folder
            locale_locales.append(locale)

            for candi in masterdoc_candidates:
                if not masterdoc_selected.get(locale):
                    a = candi.split('/')
                    if len(a) > 1 and a[0] == 'Documentation':
                        fpath = os.path.join(gitdir, a[0], folder, a[1])
                        if os.path.exists(fpath):
                            masterdoc_selected[locale] = os.path.join(a[0], folder, a[1])
                            locale_masterdocs.append(masterdoc_selected[locale])

if 0:
    {
        "buildsettings": {
            "builddir": "/home/marble/htdocs/docs-typo3-org/typo3cms/extensions/sphinx/2.5",
            "gitbranch": "",
            "gitdir": "",
            "giturl": "",
            "localization": "fr_FR",
            "logdir": ".",
            "masterdoc": "",
            "package_key": "typo3cms.extensions.sphinx",
            "package_language": "fr-fr",
            "package_zip": "1",
            "project": "sphinx",
            "t3docdir": "",
            "ter_extension": "1",
            "ter_extkey": "sphinx",
            "ter_extversion": "2.5.0",
            "version": "2.5"
        }}



# ==================================================
# Set MILESTONE #1
# --------------------------------------------------

if 'always':
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
    masterdoc = masterdoc_selected.get(localization)
    if masterdoc:
        masterdoc_no_ext = os.path.splitext(masterdoc)[0]
        buildsettings['masterdoc'] = os.path.join(gitdir, masterdoc_no_ext)
        hit = None
        left, right = os.path.split(masterdoc_no_ext)
        while left:
            hit = left
            left = os.path.split(left)[0]
        if hit:
            buildsettings['t3docdir'] = os.path.join(gitdir, hit)


# ==================================================
# Set MILESTONE #2
# --------------------------------------------------

if buildsettings:
    result['MILESTONES'].append({'buildsettings': buildsettings})


# ==================================================
# save result
# --------------------------------------------------

tct.save_the_result(result, resultfile, params, facts, milestones, exitcode, CONTINUE)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
