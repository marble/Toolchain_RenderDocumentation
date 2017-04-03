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
binabspath = sys.argv[2]
facts = tct.readjson(params['factsfile'])
milestones = tct.readjson(params['milestonesfile'])
resultfile = params['resultfile']
result = tct.readjson(resultfile)
loglist = result['loglist'] = result.get('loglist', [])
toolname = params["toolname"]
toolname_pure = params['toolname_pure']
workdir = params['workdir']
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

xeq_name_cnt = 0


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    # required milestones
    requirements = []

    # just test
    for requirement in requirements:
        v = milestones_get(requirement)
        if not v:
            loglist.append("'%s' not found" % requirement)
            exitcode = 2

    build_html = milestones_get('build_html')
    build_singlehtml = milestones_get('build_singlehtml')
    TheProject = milestones_get('TheProject')

    if not (TheProject and (build_html or build_singlehtml)):
        exitcode = 2

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('PROBLEMS with params')

if CONTINUE != 0:
    loglist.append({'CONTINUE': CONTINUE})
    loglist.append('NOTHING to do')


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    build_html_folder = milestones_get('build_html_folder')
    build_singlehtml_folder = milestones_get('build_singlehtml_folder')

if exitcode == CONTINUE:
    loglist.append('Here we remove files that are - unfortunately - still in the theme but are not needed.')


if exitcode == CONTINUE:

    import glob

    file_patterns = [
        '.buildinfo',
        '_static/*.map',
        '_static/css/*.map',
        '_static/jquery-*.js',
        '_static/js/t3autocomplete2.js',
        '_static/js/zumklaun.js',
        '_static/searchtools-ORIGINAL.js',
        '_static/underscore-*.js',
    ]

if exitcode == CONTINUE:
    todolist = [item for item in [build_html_folder, build_singlehtml_folder] if item]

    for folder in todolist:
        for pattern in file_patterns:
            files = glob.glob(folder + '/' + pattern)
            if files:
                loglist.append(files)
                for file in files:
                    os.remove(file)
    if build_singlehtml_folder:
        fpath = os.path.join(build_singlehtml_folder, 'objects.inv')
        if os.path.exists(fpath):
            os.remove(fpath)


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if exitcode == CONTINUE:
    result['MILESTONES'].append({
        'cleanup_files': 'done',
    })


# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)


# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
