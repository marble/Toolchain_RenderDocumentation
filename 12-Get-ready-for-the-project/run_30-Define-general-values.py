#!/usr/bin/env python
# coding: utf-8

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

buildsettings_builddir = ''
checksum_ttl_seconds = 86400 * 7 # render if last checksum calculation is older
gitdir_must_start_with = '/home/mbless/HTDOCS/:/home/marble/Repositories/:/tmp/'
lockfile_ttl_seconds = 1800
relative_part_of_builddir = ''
url_of_webroot = ''
webroot_abspath = ''
webroot_part_of_builddir = '/ALL/dummy_webroot'
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
)
general_int_options = (
    ('email_admin_send_extra_mail', 0),
    ('email_user_do_not_send', 0),
    ('make_latex', 1),
    ('make_package', 1),
    ('make_pdf', 1),
    ('make_singlehtml', 1),
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

    # is always on srv123 (?)
    webroot_part_of_builddir = lookup(facts, 'tctconfig', configset, 'webroot_part_of_builddir', default=webroot_part_of_builddir)
    url_of_webroot = lookup(facts, 'tctconfig', configset, 'url_of_webroot', default=url_of_webroot)
    # relative_part_of_builddir = lookup(facts, 'tctconfig', configset, 'relative_part_of_builddir', default=relative_part_of_builddir)
    webroot_abspath = lookup(facts, 'tctconfig', configset, 'webroot_abspath', default=webroot_abspath)
    buildsettings_builddir = lookup(milestones, 'buildsettings', 'builddir', default=buildsettings_builddir)

if not (configset and webroot_part_of_builddir and url_of_webroot
        and webroot_abspath and buildsettings_builddir):
    exitcode = 22

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('Cannot work with these PARAMS')


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    for option, default in general_int_options:
        v = deepget(facts, 'run_command', option, default=None)
        if v is None:
            v = deepget(facts, 'tctconfig', configset, option, default=default)
        result['MILESTONES'].append({option: int(v)})

    for option, default in general_string_options:
        v = deepget(facts, 'run_command', option, default=None)
        if v is None:
            v = deepget(facts, 'tctconfig', configset, option, default=default)
        result['MILESTONES'].append({option: v})

    for option, default in general_csvlist_options:
        v = deepget(facts, 'run_command', option, default=None)
        if v is None:
            v= deepget(facts, 'tctconfig', configset, option, default=default)
        v = v.replace(' ', ',').split(',')
        v = [item for item in v if item]
        result['MILESTONES'].append({option: v})


if exitcode == CONTINUE:
    # calculate relative_par_of_builddir. E.g.: typo3cms/Project/default/0.0.0
    if not relative_part_of_builddir:
        if buildsettings_builddir.startswith(webroot_part_of_builddir):
            relative_part_of_builddir = buildsettings_builddir[len(webroot_part_of_builddir):]
        elif buildsettings_builddir.startswith(webroot_abspath):
            relative_part_of_builddir = buildsettings_builddir[len(webroot_abspath):]
        else:
            relative_part_of_builddir = buildsettings_builddir

    relative_part_of_builddir = relative_part_of_builddir.strip('/')


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

if relative_part_of_builddir:
    result['MILESTONES'].append({'relative_part_of_builddir': relative_part_of_builddir})

if url_of_webroot:
    result['MILESTONES'].append({'url_of_webroot': url_of_webroot})

if webroot_abspath:
    result['MILESTONES'].append({'webroot_abspath': webroot_abspath})

if webroot_part_of_builddir:
    result['MILESTONES'].append({'webroot_part_of_builddir': webroot_part_of_builddir})

if gitdir_must_start_with:
    result['MILESTONES'].append({'gitdir_must_start_with': gitdir_must_start_with})


# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)

