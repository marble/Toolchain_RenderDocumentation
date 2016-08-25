#!/usr/bin/env python

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
loglist = result['loglist'] = result.get('loglist', [])
exitcode = CONTINUE = 0
errormsg = ''
helpmsg = ''

# ==================================================
# Check required milestone(s)
# --------------------------------------------------

def milestones_get(name, default=None):
    result = milestones.get(name, default)
    loglist.append((name, result))
    return result

if exitcode == CONTINUE:
    TheProject = milestones_get('TheProject')
    if not TheProject:
        exitcode = 2

# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    NAMING = milestones.get('NAMING', {})
    NAMING['meta'] = NAMING.get('meta', 'Here we keep names and values that are looking good')

if exitcode == CONTINUE:

    import datetime
    import glob
    import re

    locations = [
        'Documentation/Index.rst',
        'Documentation/index.rst',
        'Documentation/Index.md',
        'Documentation/index.md',
        'README.rst',
        'README.md',
    ]
    loglist.append({'locations': locations})
    masterdoc = None
    for location in locations:
        fpath = os.path.join(TheProject, location)
        if os.path.exists(fpath):
            masterdoc = fpath
        if masterdoc:
            break


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
        with file(checksum_file, 'r') as f1:
            checksum_old = f1.read()
        checksum_old = checksum_old.strip()
        checksum_time = int(os.path.getmtime(checksum_file))

if exitcode == CONTINUE:
    composerjson = None
    composerjson_file = os.path.join(TheProject, 'composer.json')
    if os.path.exists(composerjson_file):
        composerjson = tct.readjson(composerjson_file)


if exitcode == CONTINUE:
    emails_found = []
    for fname in sorted(['ext_emconf.php', 'Documentation/Index.rst']):
        fpath = os.path.join(TheProject, fname)
        if os.path.exists(fpath):
            with file(fpath, 'r') as f1:
                data = f1.read()

            # emails
            findings = re.findall(r'[\w\.-]+@[\w\.-]+', data, re.MULTILINE)
            if findings:
                unique = []
                for emadr in sorted(findings):
                    if emadr not in unique:
                        unique.append(emadr)
                emails_found.append((fname, unique))

            # project_name
            # project_version

if exitcode == CONTINUE:
    emails_user = []
    if emails_found:
        for filename, emails in emails_found:
            for email in emails:
                if email not in ['documentation@typo3.org']:
                    if email not in emails_user:
                        emails_user.append(email)


if exitcode == CONTINUE:
    NAMING['project_name'] = milestones.get('buildsettings', {}).get('project', 'PROJECT')
    NAMING['project_version'] = milestones.get('buildsettings', {}).get('version', 'VERSION')

    NAMING['project_language'] = milestones.get('buildsettings', {}).get('package_language', 'default').lower()
    NAMING['pdf_name'] = ('manual.' +
        NAMING['project_name'] + '-' +
        NAMING['project_version'] + '.pdf')
    NAMING['package_name'] = (
        NAMING['project_name'] + '-' +
        NAMING['project_version'] + '-' +
        NAMING['project_language'] + '.zip')


# ==================================================
# Set MILESTONE
# --------------------------------------------------

def decode_timestamp(unixtime):
    return datetime.datetime.fromtimestamp(unixtime).strftime('%Y-%m-%d %H:%M')

if exitcode == CONTINUE:
    if documentation_folder_exists:
        result['MILESTONES'].append({'documentation_folder': documentation_folder})
    if masterdoc:
        result['MILESTONES'].append({'masterdoc': masterdoc})
    if has_settingscfg:
        result['MILESTONES'].append({'settingscfg_file': settingscfg_file})
    if has_settingsyml:
        result['MILESTONES'].append({'settingsyml_file': settingsyml_file})
    if localization_has_localization:
        result['MILESTONES'].append({'localization_has_localization': localization_has_localization})
    if checksum_file:
        result['MILESTONES'].append({'checksum_file': checksum_file})
    if checksum_old:
        result['MILESTONES'].append({'checksum_old': checksum_old})
    if checksum_time:
        result['MILESTONES'].append({'checksum_time': checksum_time,
                                     'checksum_time_decoded': decode_timestamp(checksum_time)})
    if emails_found:
        result['MILESTONES'].append({'emails_found': emails_found})
    if composerjson:
        result['MILESTONES'].append({'composerjson': composerjson})
    if composerjson:
        result['MILESTONES'].append({'NAMING': NAMING})
    if emails_user:
        result['MILESTONES'].append({'emails_user': emails_user})


# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------
# exitcode = 99
sys.exit(exitcode)