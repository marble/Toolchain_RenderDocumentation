#!/usr/bin/env python

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
from __future__ import absolute_import
import tct
import sys

params = tct.readjson(sys.argv[1])
facts = tct.readjson(params['factsfile'])
milestones = tct.readjson(params['milestonesfile'])
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

buildsettings_changed = None
gitbranch = ''
gitdir = ''
giturl = ''
repositories_rootfolder = ''
ter_extkey = ''
ter_extversion = ''
xeq_name_cnt = 0


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    buildsettings = lookup(milestones, 'buildsettings')
    gitbranch = lookup(milestones, 'buildsettings', 'gitbranch')
    gitdir = lookup(milestones, 'buildsettings', 'gitdir')
    gitdir_is_ready_for_use = lookup(milestones, 'buildsettings', 'gitdir_is_ready_for_use')
    giturl = lookup(milestones, 'buildsettings', 'giturl')
    ter_extkey = lookup(milestones, 'buildsettings', 'ter_extkey')
    ter_extversion = lookup(milestones, 'buildsettings', 'ter_extversion')

    if not ((gitdir or giturl) or (ter_extkey and ter_extversion)):
        loglist.append('no source project specified')
        CONTINUE = -2

if exitcode == CONTINUE:
    if not buildsettings:
        exitcode = 22

if exitcode == CONTINUE:
    if not gitdir_is_ready_for_use and giturl and not gitbranch:
            loglist.append('we need to know the branch of the repository')
            CONTINUE = -2

if exitcode == CONTINUE:
    if not gitdir_is_ready_for_use and (gitdir or giturl) and (ter_extkey):
        loglist.append('we either expect a manual or a ter extension. ')
        exitcode = 99

if exitcode == CONTINUE:
    if not gitdir:
        configset = lookup(milestones, 'configset')
        repositories_rootfolder = lookup(facts, 'tctconfig', configset, 'repositories_rootfolder')
        if not (configset and repositories_rootfolder):
            CONTINUE = -2

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('Bad PARAMS or nothing to do')


# ==================================================
# work
# --------------------------------------------------

import os

legalchars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-01234567890'

def slugify_url(url):
    result = []
    for c in url:
        if c in legalchars:
            result.append(c)
        else:
            result.append('-')
    return ''.join(result)

if exitcode == CONTINUE:
    if not gitdir_is_ready_for_use and not gitdir and giturl:
        gitdir = os.path.join(repositories_rootfolder, slugify_url('-'.join(giturl.split('://'))))
        buildsettings['gitdir'] = gitdir
        buildsettings_changed = True

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if buildsettings_changed:
    result['MILESTONES'].append({'buildsettings': buildsettings})

# ==================================================
# save result
# --------------------------------------------------

tct.save_the_result(result, resultfile, params, facts, exitcode=exitcode, CONTINUE=CONTINUE)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
