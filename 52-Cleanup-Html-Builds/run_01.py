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
loglist = result['loglist'] = result.get('loglist', [])
exitcode = CONTINUE = 0
errormsg = ''
helpmsg = ''

# ==================================================
# Check required milestone(s)
# --------------------------------------------------
def milestones_get(name):
    result = milestones.get(name)
    loglist.append((name, result))
    return result

if exitcode == CONTINUE:
    build_html = milestones_get('build_html')
    build_html_folder = milestones_get('build_html_folder')
    build_singlehtml = milestones_get('build_singlehtml')
    build_singlehtml_folder = milestones_get('build_singlehtml_folder')
    TheProject = milestones_get('TheProject')

if not ((build_html or build_singlehtml) and TheProject):
    CONTINUE = -1

# ==================================================
# work
# --------------------------------------------------

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
