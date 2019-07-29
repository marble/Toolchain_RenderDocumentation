#!/usr/bin/env python
# coding: utf-8

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
from __future__ import absolute_import
import os
import tct
import sys

ospj = os.path.join

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

def lookup(D, *keys, **kwdargs):
    result = tct.deepget(D, *keys, **kwdargs)
    loglist.append((keys, result))
    return result

def firstNotNone(*args):
    for arg in args:
        if arg is not None:
            return arg
    else:
        return None

def findRunParameter(key, default=None, D=None):
    result = firstNotNone(
        tct.deepget(milestones, key, default=None),
        tct.deepget(facts, 'run_command', key, default=None),
        # is 'jobfile_data' available at this point?
        tct.deepget(milestones, 'jobfile_data', 'tctconfig', key, default=None),
        tct.deepget(facts, 'tctconfig', configset, key, default=None),
        default,
        None)
    # deliberate side effect
    if isinstance(D, dict):
        D[key] = result
    return result

ATNM = all_the_new_milestones = {}


# ==================================================
# define
# --------------------------------------------------

#buildsettings_builddir_root = /ALL/dummy_webroot
buildsettings_builddir = ''
checksum_ttl_seconds = 86400 * 7 # render if last checksum calculation is older
gitdir_must_start_with = '/home/mbless/HTDOCS/:/home/marble/Repositories/:/tmp/'
lockfile_ttl_seconds = 1800
relative_part_of_builddir = ''
if os.path.isdir('/RESULT'):
    # in Docker container
    TheProjectCacheDir = '/RESULT/Cache'
else:
    TheProjectCacheDir = ospj(params['workdir_home'], 'Cache')
url_of_webroot = 'https://docs.typo3.org/'
webroot_abspath = '/ALL/dummy_webroot'
xeq_name_cnt = 0


email_user_do_not_send = 0
email_user_receivers_exlude_list = [
    'documentation@typo3.org',
    'info@typo3.org',
    'kasperYYYY@typo3.com',
    'kasperYYYY@typo3.org',
]

general_string_options = (
    ('conf_py_masterfile', ''),
    ('email_admin', 'martin.bless@gmail.com'),
    ('email_user_bcc', ''),
    ('email_user_cc', ''),
    ('email_user_to_instead', ''),
    ('oo_parser', 'dl'),  # dl | flt
)
general_int_options = (
    ('email_admin_send_extra_mail', 0),
    ('email_user_do_not_send', 0),
    ('make_latex', 1),
    ('make_package', 1),
    ('make_pdf', 1),
    ('make_singlehtml', 1),
    ('rebuild_needed', 0),
    ('replace_static_in_html', 0),
)

general_csvlist_options = (
    ('email_user_receivers_exlude_list', ''),
)


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    configset = milestones.get('configset')

    url_of_webroot = lookup(facts, 'tctconfig', configset, 'url_of_webroot', default=url_of_webroot)
    # relative_part_of_builddir = lookup(facts, 'tctconfig', configset, 'relative_part_of_builddir', default=relative_part_of_builddir)
    webroot_abspath = lookup(facts, 'tctconfig', configset, 'webroot_abspath', default=webroot_abspath)
    buildsettings_builddir = lookup(milestones, 'buildsettings', 'builddir', default=buildsettings_builddir)
    makedir_abspath = lookup(milestones, 'makedir_abspath')

if not (1
        and buildsettings_builddir
        and configset
        and url_of_webroot
        and webroot_abspath
        and makedir_abspath
    ):
    exitcode = 22

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('Bad PARAMS or nothing to do')


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    for option, default in general_int_options:
        v = findRunParameter(option, default)
        if v is not None:
            result['MILESTONES'].append({option: int(v)})

    for option, default in general_string_options:
        v = findRunParameter(option, default)
        if v is not None:
            result['MILESTONES'].append({option: v})

    for option, default in general_csvlist_options:
        v = findRunParameter(option, default)
        if v is not None:
            v = v.replace(' ', ',').split(',')
            v = [item for item in v if item]
            result['MILESTONES'].append({option: v})


if exitcode == CONTINUE:
    # calculate relative_part_of_builddir. E.g.: typo3cms/Project/default/0.0.0
    if not relative_part_of_builddir:
        if buildsettings_builddir.startswith(webroot_abspath):
            relative_part_of_builddir = buildsettings_builddir[len(webroot_abspath):]
        else:
            relative_part_of_builddir = buildsettings_builddir

    relative_part_of_builddir = relative_part_of_builddir.strip('/')

    SYMLINK_THE_PROJECT = ospj(makedir_abspath, 'SYMLINK_THE_PROJECT')
    SYMLINK_THE_OUTPUT = ospj(makedir_abspath, 'SYMLINK_THE_OUTPUT')

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if buildsettings_builddir:
    result['MILESTONES'].append({'buildsettings_builddir': buildsettings_builddir})

if checksum_ttl_seconds:
    result['MILESTONES'].append({'checksum_ttl_seconds': checksum_ttl_seconds})

if email_user_do_not_send:
    result['MILESTONES'].append({'email_user_do_not_send': email_user_do_not_send})

if email_user_receivers_exlude_list:
    result['MILESTONES'].append({'email_user_receivers_exlude_list': email_user_receivers_exlude_list})

if lockfile_ttl_seconds:
    result['MILESTONES'].append({'lockfile_ttl_seconds': lockfile_ttl_seconds})

if TheProjectCacheDir:
    result['MILESTONES'].append({'TheProjectCacheDir': TheProjectCacheDir})

if relative_part_of_builddir:
    result['MILESTONES'].append({'relative_part_of_builddir': relative_part_of_builddir})

if url_of_webroot:
    result['MILESTONES'].append({'url_of_webroot': url_of_webroot})

if webroot_abspath:
    result['MILESTONES'].append({'webroot_abspath': webroot_abspath})

if gitdir_must_start_with:
    result['MILESTONES'].append({'gitdir_must_start_with': gitdir_must_start_with})

if SYMLINK_THE_PROJECT:
    result['MILESTONES'].append({'SYMLINK_THE_PROJECT': SYMLINK_THE_PROJECT})

if SYMLINK_THE_OUTPUT:
    result['MILESTONES'].append({'SYMLINK_THE_OUTPUT': SYMLINK_THE_OUTPUT})


# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)

"""
[general]
temp_home = /tmp
toolchains_home = /ALL/Toolchains/

[default]
buildsettings_builddir_root = /ALL/dummy_webroot
webroot_part_of_builddir = /ALL/dummy_webroot
webroot_abspath = /ALL/dummy_webroot
htaccess_template_show_latest = /ALL/Makedir/_htaccess
conf_py_masterfile = /ALL/Makedir/conf.py
repositories_rootfolder = /tmp/T3REPOS
extensions_rootfolder = /tmp/T3EXTENSIONS
extensions_builddir_relpath = typo3cms/extensions
drafts_builddir_relpath = typo3cms/drafts

# override these on the commandline
force_rebuild_needed = 1
make_latex = 0
make_package = 0
make_pdf = 0
make_singlehtml = 0
rebuild_needed = 1
replace_static_in_html = 0
talk = 1


# others
email_admin =
email_user_cc =
email_user_bcc =
lockfile_name = lockfile.json
url_of_webroot = https://docs.typo3.org/
latex_contrib_typo3_folder = /ALL/Downloads/latex.typo3
email_user_send_to_admin_too = 0
email_user_to =
email_user_do_not_send = 0
email_user_receivers_exlude_list = ,
smtp_host=

"""