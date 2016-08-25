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

# ==================================================
# define
# --------------------------------------------------

xeq_name_cnt = 0
settings_cfg_data = {}

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
    settingscfg_file = milestones.get('settingscfg_file', '')
    if not (settingscfg_file):
        CONTINUE = -1

# ==================================================
# work
# --------------------------------------------------

import codecs
import copy
import ConfigParser

if exitcode == CONTINUE:
    config = ConfigParser.RawConfigParser()
    config.readfp(codecs.open(settingscfg_file, 'r', 'utf-8'))
    for s in config.sections():
        settings_cfg_data[s] = settings_cfg_data.get(s, {})
        for o in config.options(s):
            settings_cfg_data[s][o] = config.get(s,o)

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if settings_cfg_data:
    result['MILESTONES'].append({
        'settings_cfg':settings_cfg_data,
    })

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
