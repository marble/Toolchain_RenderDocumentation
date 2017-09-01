    #!/usr/bin/env python

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
import os
import sys
import tct

params = tct.readjson(sys.argv[1])
binabspath = sys.argv[2]
facts = tct.readjson(params['factsfile'])
milestones = tct.readjson(params['milestonesfile'])
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
    result = tct.deepget(D, *keys, **kwdargs)
    loglist.append((keys, result))
    return result


# ==================================================
# define
# --------------------------------------------------

xeq_name_cnt = 0

# which section of tctconfig does the Toolchain use?
configset = None

buildsettings = {}

if 0:
    # defining this buildsettings here allows PyCharm to
    # autocomplete the names of the keys
    # The Python compiler will generate no code though since the
    # if clause is always False
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


if 0:
    "webroot_abspath, 'typo3cms/drafts', giturlslug"


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    # required milestones
    requirements = ['configset']

    # just test
    for requirement in requirements:
        v = lookup(milestones, requirement)
        if not v:
            loglist.append("'%s' not found" % requirement)
            exitcode = 22

    # step 1
    # Which section of tctconfig.cfg do we use?
    configset = lookup(milestones, 'configset')
    buildsettings = lookup(milestones, 'buildsettings')

    # step 2
    extensions_builddir_relpath = lookup(facts, 'tctconfig', configset, 'extensions_builddir_relpath')
    drafts_builddir_relpath = lookup(facts, 'tctconfig', configset, 'drafts_builddir_relpath')
    webroot_abspath = lookup(facts, 'tctconfig', configset, 'webroot_abspath')

    # test
    if not (buildsettings and extensions_builddir_relpath and
            drafts_builddir_relpath and webroot_abspath):
        exitcode = 99

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


    def by_terextkey(ter_extkey, ter_extversion):
        if ter_extkey and ter_extversion:

            # 01 builddir
            if not buildsettings['builddir']:
                buildsettings['builddir'] = os.path.join(
                    webroot_abspath, extensions_builddir_relpath,
                    buildsettings['ter_extkey'], buildsettings['ter_extversion'])

            # 02 gitbranch
            # 03 gitdir
            # 04 giturl

            # 05 localization
            if not buildsettings['localization']:
                buildsettings['localization'] = 'default'

            # 07 logdir
            # 08 masterdoc

            # 09 package_key
            # 10 package_language
            # 11 package_zip

            if buildsettings_initial.get('package_zip') is None:
                buildsettings['package_zip'] = 1
            if buildsettings['package_zip']:
                if not buildsettings['package_language']:
                    buildsettings['package_language'] = buildsettings['localization']
                if not buildsettings['package_key']:
                    buildsettings['package_key'] = buildsettings['ter_extkey']

            # 12 project
            if not buildsettings['project']:
                buildsettings['project'] = buildsettings['ter_extkey']

            # 13 t3docdir

            # 14 ter_extension
            if buildsettings_initial.get('ter_extension') is None:
                buildsettings['ter_extension'] = 1

            # 15 ter_extkey
            # 16 ter_extversion


            # 17 version
            if not buildsettings['version']:
                buildsettings['version'] = buildsettings['ter_extversion']

            CONTINUE = -2


    def by_giturl(giturl):

        made_a_change = False

        parts = giturl.split('/') # ['https', '', 'github.com', 'user', 'repo']
        if len(parts) < 4 or not (parts[0] in ['https:', 'http:']) or parts[1]:
            # we can't handle this
            return made_a_change

        repo_domain = parts[2]
        repo_domain_slugified = repo_domain.replace('.', '-')
        repo_relpath = '/'.join(parts[3:])
        repo_relpath_without_ext = os.path.splitext(repo_relpath)[0]

        # 01 builddir
        if not buildsettings['builddir']:
            if repo_relpath_without_ext:
                buildsettings['builddir'] = os.path.join(
                    webroot_abspath, drafts_builddir_relpath,
                    repo_domain_slugified, repo_relpath_without_ext, 'latest')
                made_a_change = True

        # 02 gitbranch
        if not buildsettings['gitbranch']:
            buildsettings['gitbranch'] = 'master'
            made_a_change = True

        # 03 gitdir
        # 04 giturl

        # 05 localization
        if not buildsettings['localization']:
            buildsettings['localization'] = 'default'
            made_a_change = True

        # 07 logdir
        # 08 masterdoc

        # 09 package_key
        # 10 package_language
        if not buildsettings['package_language']:
            buildsettings['package_language'] = 'default'
            made_a_change = True

        # 11 package_zip

        # 12 project
        if not buildsettings['project']:
            buildsettings['project'] = repo_relpath_without_ext.replace('/', '-')
            made_a_change = True

        # 13 t3docdir
        # 14 ter_extension
        # 15 ter_extkey
        # 16 ter_extversion

        # 17 version
        if not buildsettings['version']:
            buildsettings['version'] = '0.0.0'
            made_a_change = True

        return made_a_change

    def by_gitdir(gitdir):

        gitdir = gitdir.strip('/')
        gitdir = gitdir.strip('\\')
        made_a_change = False

        if not gitdir:
            return made_a_change

        gitdir_slugified = gitdir
        for old, new in ((':', '-'), ('/', '-'), ('\\', '-'), ('--', '-')):
            while old in gitdir_slugified:
                gitdir_slugified = gitdir_slugified.replace(old, new)

        # 01 builddir
        if not buildsettings['builddir']:
            buildsettings['builddir'] = os.path.join(
                webroot_abspath, drafts_builddir_relpath, gitdir_slugified, 'latest')
            made_a_change = True

        # 02 gitbranch
        # 03 gitdir
        # 04 giturl
        # 05 localization
        if not buildsettings['localization']:
            buildsettings['localization'] = 'default'
            made_a_change = True

        # 07 logdir
        # 08 masterdoc
        # 09 package_key
        # 10 package_language
        if not buildsettings['package_language']:
            buildsettings['package_language'] = 'default'
            made_a_change = True

        # 11 package_zip
        # 12 project
        if not buildsettings['project']:
            buildsettings['project'] = 'Project'
            made_a_change = True
        # 13 t3docdir
        # 14 ter_extension
        # 15 ter_extkey
        # 16 ter_extversion
        # 17 version
        if not buildsettings['version']:
            buildsettings['version'] = '0.0.0'
            made_a_change = True

        return made_a_change


if exitcode == CONTINUE:

    changed = False

    ter_extkey = buildsettings['ter_extkey']
    ter_extversion = buildsettings['ter_extversion']
    giturl = buildsettings.get('giturl', '')
    gitdir = buildsettings.get('gitdir', '')

    if ter_extkey and ter_extversion:
        changed = by_terextkey(ter_extkey, ter_extversion)

    elif giturl and not gitdir:
        changed = by_giturl(giturl)

    elif gitdir and not giturl:
        changed = by_gitdir(gitdir)


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

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------


sys.exit(exitcode)
