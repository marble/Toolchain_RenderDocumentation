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
# Get and check required milestone(s)
# --------------------------------------------------

if exitcode == CONTINUE:
    settingsyml_file = milestones.get('settingsyml_file', '')
    settingscfg_file = milestones.get('settingscfg_file', '')
    if settingscfg_file:
        loglist.append('Nothing to do. Settings.cfg is existing.')
        CONTINUE = -1

if exitcode == CONTINUE:
    if not settingsyml_file:
        loglist.append('Settings.yml not found')
        CONTINUE = -1

# ==================================================
# work
# --------------------------------------------------

import codecs
import copy
import yaml
import ConfigParser

config = ConfigParser.RawConfigParser()


if exitcode == CONTINUE:

    settingsyml_file = milestones['settingsyml_file']
    with codecs.open(settingsyml_file, 'r', 'utf-8') as f1:
        settingsyml = yaml.safe_load(f1)
    loglist.append({'settingsyml': copy.deepcopy(settingsyml)})
    confpy = settingsyml['conf.py']

    section = 'general'
    config.add_section(section)
    cnt = 0
    for key,value in sorted(confpy.items()):
        if isinstance(value, (dict, list)):
            pass
        else:
            if key.startswith('latex_'):
                # we saw problems with these
                continue
            cnt += 1
            config.set(section, key, value)
            del confpy[key]

    section = 'html_theme_options'
    config.add_section(section)
    config.set(section, 'github_branch', '')
    config.set(section, 'github_commit_hash', '')
    config.set(section, 'github_repository', '')
    config.set(section, 'github_revision_msg', '')
    config.set(section, 'github_sphinx_locale', '')
    config.set(section, 'project_contact', '')
    config.set(section, 'project_discussions', '')
    config.set(section, 'project_home', '')
    config.set(section, 'project_issues', '')
    config.set(section, 'project_repository', '')
    config.set(section, 'use_opensearch', '')

    section = 'intersphinx_mapping'
    config.add_section(section)
    im = confpy.get('intersphinx_mapping')
    if im:
        for key, value in sorted(im.items()):
            config.set(section, key, value[0])
        del confpy['intersphinx_mapping']

    section = 'extensions'
    extensions = confpy.get('extensions')
    if extensions:
        config.add_section(section)
        for i, extension in enumerate(sorted(extensions)):
            config.set(section, 'ext_%02d' % i, extension)
        del confpy['extensions']

    section = 'extlinks'
    extlinks = confpy.get('extlinks')
    if extlinks:
        config.add_section(section)
        for key, value in sorted(extlinks.items()):
            config.set(section, key, '%s | %s' % (value[0], value[1]))
        del confpy['extlinks']


    # todo: handle 'latex_documents'
    # No, it turns out it's better to leave them out.

    for section in ['latex_elements', 'texinfo_documents', 'man_pages']:
        items = confpy.get(section)
        if items:
            config.add_section(section)
            for key, value in sorted(items.items()):
                config.set(section, key, value)
            del confpy[section]

    loglist.append({'UNCONVERTED_REST': copy.deepcopy(settingsyml)})
    settingscfg_file = settingsyml_file[:-4] + '.cfg'
    with codecs.open(settingscfg_file, 'w') as configfile:
        config.write(configfile)


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if exitcode == CONTINUE:
    result['MILESTONES'].append({
        'settingscfg_file': settingscfg_file,
        'has_settingscfg': True,
        'has_settingscfg_generated': True,
    })

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
