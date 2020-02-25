#!/usr/bin/env python

from __future__ import print_function
from __future__ import absolute_import

import os
import os.path as osp
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

configset = None

xeq_name_cnt = 0

if 0:
    # defining this buildsettings here allows PyCharm to autocomplete the
    # names of the keys. The Python compiler will generate no code though since
    # the if clause is always False.
    buildsettings['builddir']             # 01 builddir
    buildsettings['gitbranch']            # 02 gitbranch
    buildsettings['gitdir']               # 03 gitdir
    buildsettings['giturl']               # 04 giturl
    buildsettings['localization']         # 05 localization
    buildsettings['logdir']               # 07 logdir
    buildsettings['masterdoc']            # 08 masterdoc
    buildsettings['package_key']          # 09 package_key
    buildsettings['package_language']     # 10 package_language
    buildsettings['package_zip']          # 11 package_zip
    buildsettings['project']              # 12 project
    buildsettings['t3docdir']             # 13 t3docdir
    buildsettings['ter_extension']        # 14 ter_extension
    buildsettings['ter_extkey']           # 15 ter_extkey
    buildsettings['ter_extversion']       # 16 ter_extversion
    buildsettings['version']              # 17 version
    buildsettings['origproject']          # 18 origproject
    buildsettings['origprojectdocroot']   # 19 origprojectdocroot
    buildsettings['origprojectmasterdoc'] # 20 origprojectmasterdoc



# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    xx_XX = re.compile('([a-z]{2}_[A-Z]{2})|default')

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
                       'Not matching "([a-z]{2}_[A-Z]{2})|default"')
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

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('Bad PARAMS or nothing to do')


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    # fetched from $MAKEDIR/buildsettings.sh
    buildsettings_initial = lookup(milestones, 'buildsettings_initial')

    if not buildsettings['localization']:
        buildsettings['localization'] = 'default'

    if not buildsettings['package_language']:
        buildsettings['package_language'] = localization.lower().replace('_', '-')

    # when fetching a ter extension
    if buildsettings['ter_extkey']:
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
            repo_relpath_without_ext = osp.splitext(repo_relpath)[0]

            if buildsettings['builddir'] in ['', 'typo3cms/project/0.0.0']:
                if repo_relpath_without_ext:
                    buildsettings['builddir'] = osp.join(
                        drafts_builddir_relpath, repo_domain_slugified,
                        repo_relpath_without_ext, 'latest')

            if buildsettings['project'].lower() in ['', 'project']:
                buildsettings['project'] = repo_relpath_without_ext.replace('/', '-')

    # when rendering from an existing directory
    elif buildsettings['gitdir']:
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
            buildsettings['builddir'] = osp.join(
                drafts_builddir_relpath, gitdir_slugified, '0.0.0')

# normalize
gitdir = osp.abspath(buildsettings['gitdir'])
t3docdir = buildsettings['t3docdir']
if not osp.isabs(t3docdir):
    t3docdir = osp.abspath(osp.join(gitdir, t3docdir))
t3docdir = t3docdir[len(gitdir)+1:]

origproject = lookup(buildsettings, 'origproject', default='')
if not origproject:
    origproject = gitdir

origprojectdocroot = lookup(buildsettings, 'origprojectdocroot', default='')
if not origprojectdocroot:
    origprojectdocroot = t3docdir

origprojectmasterdoc = lookup(buildsettings, 'origprojectmasterdoc', default='')
if not origprojectmasterdoc:
    origprojectmasterdoc = buildsettings['masterdoc']

buildsettings['gitdir'] = gitdir  # absolute
buildsettings['t3docdir'] =  t3docdir  # relative
buildsettings['origproject'] = origproject  # absolute
buildsettings['origprojectdocroot'] = origprojectdocroot  # relative
buildsettings['origprojectmasterdoc'] = origprojectmasterdoc  # relative


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if buildsettings:
    result['MILESTONES'].append({'buildsettings': buildsettings})

if configset:
    result['MILESTONES'].append({'configset': configset})


# ==================================================
# save result
# --------------------------------------------------

tct.save_the_result(result, resultfile, params, facts, milestones, exitcode, CONTINUE, reason)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------


sys.exit(exitcode)
