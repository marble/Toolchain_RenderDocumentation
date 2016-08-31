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
workdir = params['workdir']
loglist = result['loglist'] = result.get('loglist', [])
exitcode = CONTINUE = 0

# ==================================================
# define
# --------------------------------------------------

xeq_name_cnt = 0
relative_part_of_builddir = ''
webroot_part_of_builddir = ''
url_of_webroot = ''
webroot_abspath = ''
buildsettings_builddir = ''
lockfile_ttl_seconds = 1800
checksum_ttl_seconds = 86400

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

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')
    toolchain_name = facts.get('toolchain_name')

    # is always on srv123
    webroot_part_of_builddir = tct.deepget(facts, 'tctconfig', toolchain_name, 'webroot_part_of_builddir')
    loglist.append(('webroot_part_of_builddir', webroot_part_of_builddir))

    url_of_webroot = tct.deepget(facts, 'tctconfig', toolchain_name, 'url_of_webroot')
    loglist.append(('url_of_webroot', url_of_webroot))

    webroot_abspath = tct.deepget(facts, 'tctconfig', toolchain_name, 'webroot_abspath')
    loglist.append(('webroot_abspath', webroot_abspath))

    buildsettings_builddir = tct.deepget(milestones, 'buildsettings', 'builddir')
    loglist.append(('buildsettings_builddir', buildsettings_builddir))

if not (toolchain_name and webroot_part_of_builddir and url_of_webroot
        and webroot_abspath and buildsettings_builddir):
    exitcode = -2

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('PROBLEMS with params')


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    if not relative_part_of_builddir:
        if buildsettings_builddir.startswith(webroot_part_of_builddir):
            relative_part_of_builddir = buildsettings_builddir[len(webroot_part_of_builddir):]
        elif buildsettings_builddir.startswith(webroot_abspath):
            relative_part_of_builddir = buildsettings_builddir[len(webroot_abspath):]

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if relative_part_of_builddir:
    result['MILESTONES'].append({'relative_part_of_builddir': relative_part_of_builddir})

if webroot_part_of_builddir:
    result['MILESTONES'].append({'webroot_part_of_builddir': webroot_part_of_builddir})

if url_of_webroot:
    result['MILESTONES'].append({'url_of_webroot': url_of_webroot})

if webroot_abspath:
    result['MILESTONES'].append({'webroot_abspath': webroot_abspath})

if buildsettings_builddir:
    result['MILESTONES'].append({'buildsettings_builddir': buildsettings_builddir})

if lockfile_ttl_seconds:
    result['MILESTONES'].append({'lockfile_ttl_seconds': lockfile_ttl_seconds})

if checksum_ttl_seconds:
    result['MILESTONES'].append({'checksum_ttl_seconds': checksum_ttl_seconds})


# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
