#!/usr/bin/env python

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
import os
import tct
import sys
#
import re
import shutil
import stat

params = tct.readjson(sys.argv[1])
facts = tct.readjson(params['factsfile'])
milestones = tct.readjson(params['milestonesfile'])
resultfile = params['resultfile']
result = tct.readjson(resultfile)
toolname = params['toolname']
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
# Helper functions
# --------------------------------------------------

deepget = tct.deepget

def lookup(D, *keys, **kwdargs):
    result = deepget(D, *keys, **kwdargs)
    loglist.append((keys, result))
    return result

def firstNotNone(*args):
    for arg in args:
        if arg is not None:
            return arg
    else:
        return None


# ==================================================
# define
# --------------------------------------------------

TheProjectTodos = None
TheProjectTodosMakefolders = []
toolchain_temp_home_todo_folder = None
toolchain_temp_home_todo_file = None
toolchain_temp_home_todo_file_all = None


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')
    TheProject = lookup(milestones, 'TheProject')
    localization_locales = lookup(milestones, 'localization_locales')
    buildsettings = milestones.get('buildsettings', {}).copy()
    project = buildsettings.get('project')
    version = buildsettings.get('version')
    localization = buildsettings.get('localization')
    if not (localization_locales):
        loglist.append('Nothing to do - no localizations found')
        CONTINUE = -1
    if localization and localization != 'default':
        loglist.append("Nothing to do - we are building '%s' already" % localization)
        CONTINUE = -1

if exitcode == CONTINUE:
    if not (TheProject and localization_locales and buildsettings and project and version):
        CONTINUE = -2

if exitcode == CONTINUE:
    cmdline = lookup(facts, 'cmdline')
    toolchain_temp_home = lookup(facts, 'toolchain_temp_home')
    if not (cmdline and toolchain_temp_home):
        CONTINUE = -2

if exitcode == CONTINUE:
    TheProjectMakedir = lookup(milestones, 'TheProjectMakedir')
    webroot_abspath = lookup(milestones, 'webroot_abspath')

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('Bad PARAMS or nothing to do')


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    TheProjectTodos = milestones.get('TheProjectTodos', TheProject + 'Todos')
    TheProjectLocalization = TheProject + 'Localization'
    if not os.path.exists(TheProjectTodos):
        os.makedirs(TheProjectTodos)

    toolchain_temp_home_todo_folder = os.path.join(toolchain_temp_home, 'Todo')
    if os.path.isdir(toolchain_temp_home_todo_folder):
        shutil.rmtree(toolchain_temp_home_todo_folder)
    if not os.path.exists(toolchain_temp_home_todo_folder):
        os.makedirs(toolchain_temp_home_todo_folder)

    # create the original commandline again but
    # but use 'makedir' as value here: '-c makedir makedir'
    words = []
    state = 0
    for word in cmdline.split():
        if state == 0:
            if word == '-c':
                state = 1
            else:
                words.append(word)
        elif state == 1:
            k = word
            state = 2
        elif state == 2:
            v = word
            state = 3

        if state == 3:
            if k == 'makedir':
                # write '-c makedir ~~~makedir~~~'
                words.append('-c')
                words.append('makedir')
                words.append('~~~makedir~~~')
                state = 0
            elif k == 'jobfile':
                # leave out jobfile
                state = 0
            else:
                words.append('-c')
                words.append(k)
                words.append(v)
                state = 0

    new_cmdline = ' '.join(words)

if exitcode == CONTINUE:

    # /ALL/dummy_webroot/typo3cms/project/default/0.0.0
    path_to_builddir = buildsettings['builddir'].strip('/')
    a, d = os.path.split(path_to_builddir)
    a, c = os.path.split(a)
    a, b = os.path.split(a)
    # a = path_to_builddir
    # b = builddir_project
    # c = builddir_localization
    # d = builddir_version
    xx_xx = re.compile('([a-z]{2}-[a-z]{2})|default')

    if not xx_xx.match(c):
        a, b, c, d = os.path.join(a, b), c, '' ,d

    for locale in localization_locales:
        # builddir
        c = locale.lower().replace('_', '-')
        abcd = os.path.join(a, b, c, d)
        # "webroot_abspath": "/ALL/dummy_webroot",
        if abcd.startswith(webroot_abspath):
            abcd = abcd[len(webroot_abspath):]
        buildsettings['builddir'] = abcd

        # package_language
        buildsettings['package_language'] = c

        # localization
        buildsettings['localization'] = locale

        # masterdoc
        masterdoc_selected = tct.deepget(milestones, 'masterdoc_selected', locale, default='MASTERDOC')
        masterdoc_selected_file = os.path.join(buildsettings['gitdir'], masterdoc_selected)
        buildsettings['masterdoc'] = masterdoc_selected_file

        folder_name = 'make_%s_%s_%s' % (b, c, d)
        TheProjectTodosMakefolder = os.path.join(TheProjectTodos, folder_name)
        TheProjectTodosMakefolders.append(TheProjectTodosMakefolder)
        os.makedirs(TheProjectTodosMakefolder)
        f2path = TheProjectTodosMakefolderBuildsettingsSh = os.path.join(TheProjectTodosMakefolder, 'buildsettings.sh')
        with file(f2path, 'w') as f2:
            for k in sorted(buildsettings):
                v = buildsettings[k]
                f2.write('%s=%s\n' % (k.upper(), v))
            f2.write('GITDIR_IS_READY_FOR_USE=1\n')

        if TheProjectMakedir:
            makedirfiles = ['.gitignore', '_htaccess', '_info.txt', 'conf.py', 'Overrides.cfg']
            for makedirfile in makedirfiles:
                srcfile = os.path.join(TheProjectMakedir, makedirfile)
                destfile = os.path.join(TheProjectTodosMakefolder, makedirfile)
                if os.path.exists(srcfile):
                    shutil.copy(srcfile, destfile)

        if toolchain_temp_home_todo_folder:
            toolchain_temp_home_todo_file = os.path.join(toolchain_temp_home_todo_folder, locale)
            toolchain_temp_home_todo_file_all = os.path.join(toolchain_temp_home_todo_folder, 'ALL.source-me.sh')
            line = new_cmdline.replace('-c makedir ~~~makedir~~~', '-c makedir ' + TheProjectTodosMakefolder)
            with file(toolchain_temp_home_todo_file, 'a') as f2:
                f2.write('#!/bin/sh\n\n')
                f2.write(line + '\n')
            # make executable
            st = os.stat(toolchain_temp_home_todo_file)
            os.chmod(toolchain_temp_home_todo_file, st.st_mode | stat.S_IEXEC)
            with file(toolchain_temp_home_todo_file_all, 'a') as f2:
                f2.write(toolchain_temp_home_todo_file + '\n')

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if TheProjectTodos:
    result['MILESTONES'].append({'TheProjectTodos': TheProjectTodos})

if TheProjectTodosMakefolders:
    result['MILESTONES'].append({'TheProjectTodosMakefolders': TheProjectTodosMakefolders})

if toolchain_temp_home_todo_folder:
    result['MILESTONES'].append({'toolchain_temp_home_todo_folder': toolchain_temp_home_todo_folder})

if toolchain_temp_home_todo_file:
    result['MILESTONES'].append({'toolchain_temp_home_todo_file': toolchain_temp_home_todo_file})

if toolchain_temp_home_todo_file_all:
    result['MILESTONES'].append({'toolchain_temp_home_todo_file_all': toolchain_temp_home_todo_file_all})

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
