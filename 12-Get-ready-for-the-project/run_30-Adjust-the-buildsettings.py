#!/usr/bin/env python

from __future__ import print_function
from __future__ import absolute_import

import os
import re
import sys
import tct

from tct import deepget

params = tct.readjson(sys.argv[1])
binabspath = sys.argv[2]
facts = tct.readjson(params['factsfile'])
milestones = tct.readjson(params['milestonesfile'])
reason = ''
resultfile = params['resultfile']
result = tct.readjson(resultfile)
loglist = result['loglist'] = result.get('loglist', [])
toolname = params['toolname']
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
    result = deepget(D, *keys, **kwdargs)
    loglist.append((keys, result))
    return result


# ==================================================
# define
# --------------------------------------------------

buildsettings_changed = None
configset = None

OrigProject = None
OrigProjectDocroot = None
OrigProjectMasterdoc = None

xeq_name_cnt = 0

if 0:
    # defining this buildsettings here allows PyCharm to autocomplete the
    # names of the keys. The Python compiler will generate no code though since
    # the if clause is always False.
    buildsettings = {}
    buildsettings['builddir'] = ""
    buildsettings['gitbranch'] = ""
    buildsettings['gitdir'] = ""
    buildsettings['giturl'] = ""
    buildsettings['localization'] = ""
    buildsettings['logdir'] = ""
    buildsettings['masterdoc'] = ""
    buildsettings['package_key'] = ""
    buildsettings['package_language'] = ""
    buildsettings['package_zip'] = 0
    buildsettings['project'] = ""
    buildsettings['t3docdir'] = ""
    buildsettings['ter_extension'] = 0
    buildsettings['ter_extkey'] = ""
    buildsettings['ter_extversion'] = ""
    buildsettings['version'] = ""


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    xx_XX = re.compile('([a-z]{2}_[a-z]{2})|default')

    buildsettings = lookup(milestones, 'buildsettings')
    configset = lookup(milestones, 'configset')
    if not (1
            and buildsettings
            and configset):
        exitcode = 22
        reason = 'Bad PARAMS or nothing to do'

if exitcode == CONTINUE:
    localization = buildsettings.get('localization', '')
    if localization and not xx_XX.match(localization):
        loglist.append('Bad buildsettings.localization. '
                       'Not matching "([a-z]{2}_[a-z]{2})|default"')
        exitcode = 22
        reason = 'Bad PARAMS or nothing to do'

if exitcode == CONTINUE:
    extensions_builddir_relpath = lookup(facts, 'tctconfig', configset, 'extensions_builddir_relpath', default=None)
    drafts_builddir_relpath = lookup(facts, 'tctconfig', configset, 'drafts_builddir_relpath', default=None)
    webroot_abspath = lookup(facts, 'tctconfig', configset, 'webroot_abspath', default=None)

    if not (1
            and buildsettings
            and drafts_builddir_relpath
            and extensions_builddir_relpath
            and webroot_abspath
            and 1):
        exitcode = 22
        reason = 'Bad PARAMS or nothing to do'

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('Bad PARAMS or nothing to do')


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:

    # we have to care about these:

    # 01 builddir
    # 02 gitbranch
    # 03 gitdir
    # 04 giturl
    # 05 localization
    # 07 logdir
    # 08 masterdoc
    # 09 package_key
    # 10 package_language
    # 11 package_zip
    # 12 project
    # 13 t3docdir
    # 14 ter_extension
    # 15 ter_extkey
    # 16 ter_extversion
    # 17 version

    buildsettings_initial = lookup(milestones, 'buildsettings_initial')


if exitcode == CONTINUE:
    if 0 and 'all':
        buildsettings['builddir']          # 01 builddir
        buildsettings['gitbranch']         # 02 gitbranch
        buildsettings['gitdir']            # 03 gitdir
        buildsettings['giturl']            # 04 giturl
        buildsettings['localization']      # 05 localization
        buildsettings['logdir']            # 07 logdir
        buildsettings['masterdoc']         # 08 masterdoc
        buildsettings['package_key']       # 09 package_key
        buildsettings['package_language']  # 10 package_language
        buildsettings['package_zip']       # 11 package_zip
        buildsettings['project']           # 12 project
        buildsettings['t3docdir']          # 13 t3docdir
        buildsettings['ter_extension']     # 14 ter_extension
        buildsettings['ter_extkey']        # 15 ter_extkey
        buildsettings['ter_extversion']    # 16 ter_extversion
        buildsettings['version']           # 17 version


if exitcode == CONTINUE:

    if not buildsettings['localization']:
        buildsettings['localization'] = 'default'
        buildsettings_changed = True

    if not buildsettings['package_language']:
        buildsettings['package_language'] = localization.lower().replace('_', '-')
        buildsettings_changed = True

    # when fetching a ter extension
    if buildsettings['ter_extkey']:
        buildsettings_changed = True
        buildsettings['gitbranch'] = ''     # 02 gitbranch
        buildsettings['gitdir'] = ''        # 03 gitdir
        buildsettings['giturl'] = ''        # 04 giturl
        buildsettings['package_key'] = 'typo3cms.extensions.' + buildsettings['ter_extkey']  # 09 package_key

        if buildsettings['project'].lower() in ['', 'project']:
            buildsettings['project'] = buildsettings['ter_extkey']

        if buildsettings['version'].lower() in ['', '0.0.0']:
            if buildsettings['ter_extversion']:
                buildsettings['version'] = buildsettings['ter_extversion']

        if buildsettings['builddir'].lower() in ['', 'typo3cms/project/0.0.0']:
            parts = [extensions_builddir_relpath, buildsettings['ter_extkey']]
            if buildsettings['localization'] and buildsettings['localization'] != 'default':
                parts.append(buildsettings['localization'].lower().replace('_', '-'))
            parts.append(buildsettings['ter_extversion'])
            buildsettings['builddir'] = '/'.join(parts)


    # when cloning a repository
    elif buildsettings['giturl']:
        buildsettings_changed = True
        buildsettings['gitdir'] = ''          # 03 gitdir
        buildsettings['ter_extkey'] = ''      # 15 ter_extkey
        buildsettings['ter_extversion'] = ''  # 16 ter_extversion

        parts = buildsettings['giturl'].split('/') # ['https:', '', 'github.com', 'user', 'repo']
        if len(parts) < 4 or not (parts[0] in ['https:', 'http:']) or parts[1]:
            exitcode = 22
            loglist.append('giturl is to short')

        if exitcode == CONTINUE:
            repo_domain = parts[2]
            repo_domain_slugified = repo_domain.replace('.', '-')
            repo_relpath = '/'.join(parts[3:])
            repo_relpath_without_ext = os.path.splitext(repo_relpath)[0]

            if buildsettings['builddir'] in ['', 'typo3cms/project/0.0.0']:
                if repo_relpath_without_ext:
                    buildsettings['builddir'] = os.path.join(
                        drafts_builddir_relpath, repo_domain_slugified,
                        repo_relpath_without_ext, 'latest')

            if buildsettings['project'].lower() in ['', 'project']:
                buildsettings['project'] = repo_relpath_without_ext.replace('/', '-')

    # when rendering from an existing directory
    elif buildsettings['gitdir']:
        buildsettings_changed = True
        buildsettings['gitbranch'] = ''                   # 02 gitbranch
        buildsettings['giturl'] = ''                      # 04 giturl
        buildsettings['ter_extkey'] = ''                  # 15 ter_extkey
        buildsettings['ter_extversion'] = ''              # 16 ter_extversion

        gitdir_slugified = buildsettings['gitdir'].lower()
        for old, new in ((':', '-'), ('/', '-'), ('\\', '-'), ('--', '-')):
            while old in gitdir_slugified:
                gitdir_slugified = gitdir_slugified.replace(old, new)
        gitdir_slugified = gitdir_slugified.strip('-')
        if not gitdir_slugified:
            gitdir_slugified = 'project'

        # ['', 'typo3cms/project/0.0.0']
        if not buildsettings['builddir']:
            buildsettings['builddir'] = os.path.join(
                drafts_builddir_relpath, gitdir_slugified, '0.0.0')


if exitcode == CONTINUE:

    # readonly, what the container copies initially
    OrigProject = buildsettings['gitdir'].rstrip('/')

    OrigProjectDocroot = buildsettings['t3docdir'].rstrip('/')
    if not os.path.isabs(OrigProjectDocroot):
        OrigProjectDocroot = os.path.join(OrigProject, OrigProjectDocroot)
    OrigProjectDocroot = os.path.abspath(OrigProjectDocroot)

    OrigProjectMasterdoc = buildsettings['masterdoc'].rstrip('/')
    if not os.path.isabs(OrigProjectMasterdoc):
        OrigProjectMasterdoc = os.path.join(OrigProject, OrigProjectMasterdoc)
    OrigProjectMasterdoc = os.path.abspath(OrigProjectMasterdoc)

    valid = len(OrigProject) > 0
    valid = valid and OrigProjectDocroot.startswith(OrigProject)
    valid = valid and OrigProjectMasterdoc.startswith(OrigProjectDocroot)

    if not valid:
        loglist.append(('Invalid', {
            'OrigProject': OrigProject,
            'OrigProjectDocroot': OrigProjectDocroot,
            'OrigProjectMasterdoc': OrigProjectMasterdoc}))
        OrigProject = None
        OrigProjectDocroot = None
        OrigProjectMasterdoc = None


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if buildsettings_changed is not None:
    result['MILESTONES'].append({'buildsettings': buildsettings})

if configset:
    result['MILESTONES'].append({'configset': configset})

if OrigProject:
    result['MILESTONES'].append({'OrigProject': OrigProject})

if OrigProjectDocroot:
    result['MILESTONES'].append({'OrigProjectDocroot': OrigProjectDocroot})

if OrigProjectMasterdoc:
    result['MILESTONES'].append({'OrigProjectMasterdoc': OrigProjectMasterdoc})


# ==================================================
# save result
# --------------------------------------------------

tct.save_the_result(result, resultfile, params, facts, milestones, exitcode, CONTINUE, reason)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------


sys.exit(exitcode)
