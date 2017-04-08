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
toolname_pure = params['toolname_pure']
workdir = params['workdir']
loglist = result['loglist'] = result.get('loglist', [])
exitcode = CONTINUE = 0


# ==================================================
# Make a copy of milestones for later inspection?
# --------------------------------------------------

if 0 or milestones.get('debug_always_make_milestones_snapshot'):
    tct.make_snapshot_of_milestones(params['milestonesfile'], sys.argv[1])


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


# ==================================================
# define
# --------------------------------------------------

TheProjectTodos = None
TheProjectTodosMakefolders = []


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')
    TheProject = milestones_get('TheProject')
    localization_locales = milestones_get('localization_locales')
    buildsettings = milestones.get('buildsettings', {}).copy()
    project = buildsettings.get('project')
    version = buildsettings.get('version')
    localization = buildsettings.get('localization')
    if not (localization_locales):
        loglist.append('Nothing to do - no localizations found')
        CONTINUE = -1
    if localization:
        loglist.append("Nothing to do - we are building '%s' already" % localization)
        CONTINUE = -1


if exitcode == CONTINUE:
    if not (TheProject and buildsettings and project and version):
        exitcode = 22

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('PROBLEM with params')

if CONTINUE != 0:
    loglist.append({'CONTINUE': CONTINUE})
    loglist.append('NOTHING to do')


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    TheProjectTodos = milestones.get('TheProjectTodos', TheProject + 'Todos')

if exitcode == CONTINUE:
    TheProjectLocalization = TheProject + 'Localization'

if exitcode == CONTINUE:
    if not os.path.exists(TheProjectTodos):
        os.makedirs(TheProjectTodos)

if exitcode == CONTINUE:

    a, c = os.path.split(buildsettings['builddir'])
    for locale in localization_locales:

        # builddir
        b = locale.lower().replace('_', '-')
        buildsettings['builddir'] = os.path.join(a, b, c)

        # localization
        buildsettings['localization'] = locale

        # masterdoc
        masterdoc_selected = tct.deepget(milestones, 'masterdoc_selected', locale, default='MASTERDOC')
        masterdoc_selected_file = os.path.join(buildsettings['gitdir'], masterdoc_selected)
        buildsettings['masterdoc'] = masterdoc_selected_file

        folder_name = 'make_%s_%s_%s' % (project, version, locale)
        TheProjectTodosMakefolder = os.path.join(TheProjectTodos, folder_name)
        TheProjectTodosMakefolders.append(TheProjectTodosMakefolder)
        os.makedirs(TheProjectTodosMakefolder)
        f2path = TheProjectTodosMakefolderBuildsettingsSh = os.path.join(TheProjectTodosMakefolder, 'buildsettings.sh')
        with file(f2path, 'w') as f2:
            for k in sorted(buildsettings):
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
