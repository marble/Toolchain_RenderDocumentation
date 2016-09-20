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




# masterdoc
# t3docdir









# ==================================================
# define
# --------------------------------------------------

MASTERDOC_line = None
LOGDIR_line = None
buildsettings_file_fixed = None

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
    TheProjectLog = milestones_get('TheProjectLog')
    if not (TheProjectLog):
        exitcode = 2

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('PROBLEMS with params')

if exitcode == CONTINUE:
    masterdoc = milestones_get('masterdoc')
    TheProjectMakedir = milestones_get('TheProjectMakedir')
    if not (masterdoc and TheProjectMakedir):
        loglist.append('SKIPPING')
        CONTINUE = -1

# ==================================================
# work
# --------------------------------------------------

import shutil
import codecs

if exitcode == CONTINUE:
    buildsettingssh_file = os.path.join(TheProjectMakedir, 'buildsettings.sh')
    original = buildsettingssh_file + '.original'
    shutil.move(buildsettingssh_file, original)

if exitcode == CONTINUE:

    masterdoc_without_fileext = os.path.splitext(masterdoc)[0]
    with codecs.open(original, 'r', 'utf-8') as f1:
        with codecs.open(buildsettingssh_file, 'w', 'utf-8') as f2:
            for line in f1:
                if line.startswith('MASTERDOC='):
                    MASTERDOC_line = 'MASTERDOC=' + masterdoc_without_fileext + '\n'
                    loglist.append(('MASTERDOC_line', MASTERDOC_line))
                    line = MASTERDOC_line
                elif line.startswith('LOGDIR='):
                    LOGDIR_line = 'LOGDIR=' + TheProjectLog + '\n'
                    loglist.append(('LOGDIR_line', LOGDIR_line))
                    line = LOGDIR_line
                f2.write(line)
    buildsettings_file_fixed = True

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if buildsettings_file_fixed:
    result['MILESTONES'].append('buildsettings_file_fixed')\


# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
