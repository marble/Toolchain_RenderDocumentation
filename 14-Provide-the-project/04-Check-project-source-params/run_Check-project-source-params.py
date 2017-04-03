#!/usr/bin/env python

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
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
# Helper functions
# --------------------------------------------------

def lookup(D, *keys, **kwdargs):
    result = tct.deepget(D, *keys, **kwdargs)
    loglist.append((keys, result))
    return result


# ==================================================
# define
# --------------------------------------------------

buildsettings = None
gitbranch = ''
gitdir = ''
giturl = ''
repositories_rootfolder = ''
ter_extkey = ''
ter_extversion = ''
toolchain_name = ''
xeq_name_cnt = 0


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    # required milestones
    requirements = []

    # just test
    for requirement in requirements:
        v = lookup(milestones, requirement)
        if not v:
            loglist.append("'%s' not found" % requirement)
            exitcode = 2

    buildsettings = lookup(milestones, 'buildsettings')
    gitbranch = lookup(milestones, 'buildsettings', 'gitbranch')
    gitdir = lookup(milestones, 'buildsettings', 'gitdir')
    giturl = lookup(milestones, 'buildsettings', 'giturl')
    ter_extkey = lookup(milestones, 'buildsettings', 'ter_extkey')
    ter_extversion = lookup(milestones, 'buildsettings', 'ter_extversion')

    if not ((gitdir or giturl) or (ter_extkey and ter_extversion)):
        loglist.append('no source project specified')
        CONTINUE = -2

if exitcode == CONTINUE:
    if not buildsettings:
        exitcode = 2

if exitcode == CONTINUE:
    if giturl and not gitbranch:
        loglist.append('we need to know the branch of the repository')
        CONTINUE = -2

if exitcode == CONTINUE:
    if (gitdir or giturl) and (ter_extkey or ter_extversion):
        loglist.append('we either expect a manual or a ter extension. ')
        exitcode = 99

if exitcode == CONTINUE:
    if not gitdir:
        toolchain_name = lookup(facts, 'toolchain_name')
        repositories_rootfolder = lookup(facts, 'tctconfig', toolchain_name, 'repositories_rootfolder')
        if not (toolchain_name and repositories_rootfolder):
            CONTINUE = -2

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('PROBLEM with required params')

if CONTINUE != 0:
    loglist.append({'CONTINUE': CONTINUE})
    loglist.append('NOTHING to do')


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
    if not gitdir and giturl:
        gitdir = os.path.join(repositories_rootfolder, slugify_url('-'.join(giturl.split('://'))))
        buildsettings['gitdir'] = gitdir


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if buildsettings:
    result['MILESTONES'].append({'buildsettings': buildsettings})

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
