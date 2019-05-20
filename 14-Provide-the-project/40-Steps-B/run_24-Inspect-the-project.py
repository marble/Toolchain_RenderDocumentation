#!/usr/bin/env python

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
from __future__ import absolute_import
import os
import tct
import sys
#
import os

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

# first
checksum_file  = None
checksum_old  = None
checksum_time = None
checksum_time_decoded = None
composerjson = None
documentation_folder_exists = None
email_user_receivers_exlude_list = lookup(milestones, 'email_user_receivers_exlude_list', default=[])
emails_found_in_projects = None
emails_user_from_project = None
has_settingscfg = None
has_settingsyml = None
localization_has_localization = None
NAMING = milestones.get('NAMING', {})
settingscfg_file = None
settingsyml_file = None

# second
NAMING['meta'] = NAMING.get('meta', 'Here we keep names and values that are looking good')


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    TheProject = lookup(milestones, 'TheProject')

    if not (TheProject):
        CONTINUE = -2

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('Bad PARAMS or nothing to do')


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    import datetime
    import glob
    import re

    documentation_folder = os.path.join(TheProject, 'Documentation')
    documentation_folder_exists = os.path.isdir(documentation_folder)

    settingscfg_file = os.path.join(TheProject, 'Documentation/Settings.cfg')
    has_settingscfg = os.path.exists(settingscfg_file)
    settingsyml_file = os.path.join(TheProject, 'Documentation/Settings.yml')
    has_settingsyml = os.path.exists(settingsyml_file)

    pattern = TheProject + '/Documentation/Localization.*'
    loglist.append({'pattern': pattern})
    folders = glob.glob(pattern)
    loglist.append({'folders': folders})
    localization_has_localization = len(folders) > 0


if exitcode == CONTINUE:

    makedir = milestones['makedir']
    checksum_file = os.path.join(makedir, 'build.checksum')
    checksum_old = None
    checksum_time = None
    if os.path.exists(checksum_file):
        with open(checksum_file, 'r') as f1:
            checksum_old = f1.read()
        checksum_old = checksum_old.strip()
        checksum_time = int(os.path.getmtime(checksum_file))

if exitcode == CONTINUE:
    composerjson = None
    composerjson_file = os.path.join(TheProject, 'composer.json')
    if os.path.exists(composerjson_file):
        composerjson = tct.readjson(composerjson_file)


if exitcode == CONTINUE:
    emails_found_in_projects = []
    for fname in sorted(['ext_emconf.php', 'Documentation/Index.rst']):
        fpath = os.path.join(TheProject, fname)
        if os.path.exists(fpath):
            with open(fpath, 'r') as f1:
                data = f1.read()

            # emails
            findings = re.findall(r'[\w\.-]+@[\w\.-]+', data, re.MULTILINE)
            if findings:
                unique = []
                for emadr in sorted(findings):
                    if emadr not in unique:
                        unique.append(emadr)
                emails_found_in_projects.append((fname, unique))

            # project_name
            # project_version

if exitcode == CONTINUE:
    excluded_emails_lowercase = [e.lower() for e in email_user_receivers_exlude_list]
    emails_user_from_project = []
    if emails_found_in_projects:
        for filename, emails in emails_found_in_projects:
            for email in emails:
                email_lower = email.lower()
                if email_lower not in excluded_emails_lowercase:
                    if email_lower not in emails_user_from_project:
                        emails_user_from_project.append(email_lower)


if exitcode == CONTINUE:
    NAMING['project_name'] = milestones.get('buildsettings', {}).get('project', 'PROJECT')
    NAMING['project_version'] = milestones.get('buildsettings', {}).get('version', 'VERSION')
    NAMING['project_language'] = milestones.get('buildsettings', {}).get('package_language', 'default').lower()
    NAMING['pdf_name'] = ('manual.' +
        NAMING['project_name'] + '-' +
        NAMING['project_version'] + '.pdf'
    )
    NAMING['package_name'] = (
        NAMING['project_name'] + '-' +
        NAMING['project_version'] + '-' +
        NAMING['project_language'] + '.zip'
    )


# ==================================================
# Set MILESTONE
# --------------------------------------------------

def decode_timestamp(unixtime):
    return datetime.datetime.fromtimestamp(unixtime).strftime('%Y-%m-%d %H:%M')

D = {}

if documentation_folder_exists:
    D['documentation_folder'] = documentation_folder

if has_settingscfg:
    D['has_settingscfg'] = has_settingscfg
    D['settingscfg_file'] = settingscfg_file

if has_settingsyml:
    D['has_settingsyml'] = has_settingsyml
    D['settingsyml_file'] = settingsyml_file

if localization_has_localization:
    D['localization_has_localization'] = localization_has_localization

if checksum_file:
    D['checksum_file'] = checksum_file

if checksum_old:
    D['checksum_old'] = checksum_old

if checksum_time:
    D['checksum_time'] = checksum_time
    D['checksum_time_decoded'] = decode_timestamp(checksum_time)

if emails_found_in_projects:
    D['emails_found_in_projects'] = emails_found_in_projects

if composerjson:
    D['composerjson'] = composerjson

if 'always':
    D['NAMING'] = NAMING

if emails_user_from_project:
    D['emails_user_from_project'] = emails_user_from_project

result['MILESTONES'].append(D)


# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)


# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
