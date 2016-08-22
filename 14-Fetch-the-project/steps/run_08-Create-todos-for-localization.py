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
# Check required milestone(s)
# --------------------------------------------------
def milestones_get(name, default=None):
    result = milestones.get(name, default)
    loglist.append((name, result))
    return result

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')
    TheProject = milestones_get('TheProject')
    localization_locales = milestones_get('localization_locales')
    buildsettings = milestones.get('buildsettings')
    if not (TheProject and localization_locales and buildsettings):
        CONTINUE = -1
        loglist.append('DON\'T DO ANYTHING: not all params given')
    else:
        loglist.append('PARAMS ARE OK')

if exitcode == CONTINUE:
    TheProjectTodos = milestones.get('TheProjectTodos', TheProject + 'Todos')
    TheProjectTodosMakefolders = []

# ==================================================
# work
# --------------------------------------------------

import glob
import shutil

if exitcode == CONTINUE:
    TheProject = milestones['TheProject']
    TheProjectLocalization = TheProject + 'Localization'

if exitcode == CONTINUE:
    if not os.path.exists(TheProjectTodos):
        os.makedirs(TheProjectTodos)

    project = buildsettings.get('project')
    version = buildsettings.get('version')
    if not (project and version and buildsettings):
        exitcode = 2

if exitcode == CONTINUE:
    for locale in localization_locales:
        folder_name = 'make_%s_%s_%s' % (project, version, locale)
        TheProjectTodosMakefolder = os.path.join(TheProjectTodos, folder_name)
        TheProjectTodosMakefolders.append(TheProjectTodosMakefolder)
        os.makedirs(TheProjectTodosMakefolder)
        f2path = TheProjectTodosMakefolderBuildsettingsSh = os.path.join(TheProjectTodosMakefolder, 'buildsettings.sh')
        with file(f2path, 'w') as f2:
            for k in sorted(buildsettings):
                if k == 'localization':
                    v = locale
                else:
                    v = buildsettings[k]
                f2.write('%s=%s\n' % (k.upper(), v))

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if exitcode == CONTINUE:
    result['MILESTONES'].append({'TheProjectTodos': TheProjectTodos})

    if TheProjectTodosMakefolders:
        result['MILESTONES'].append({'TheProjectTodosMakefolders': TheProjectTodosMakefolders})

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
