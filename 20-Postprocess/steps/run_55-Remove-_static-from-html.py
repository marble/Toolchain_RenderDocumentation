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

# ==================================================
# Get and check required milestone(s)
# --------------------------------------------------

def milestones_get(name, default=None):
    result = milestones.get(name, default)
    loglist.append((name, result))
    return result

if exitcode == CONTINUE:
    replace_static_in_html = milestones_get('replace_static_in_html')
    build_html_folder = milestones_get('build_html_folder')
    build_singlehtml_folder = milestones_get('build_singlehtml_folder')

if not (replace_static_in_html and (build_html_folder or build_singlehtml_folder)):
    CONTINUE = -1

# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:

    import shutil

    todolist = [item for item in [build_html_folder, build_singlehtml_folder] if item]
    for build_folder in todolist:
        fpath = os.path.join(build_folder, '_static')
        if os.path.exists(fpath):
            shutil.rmtree(fpath)
            loglist.append('%s, %s' % ('remove', fpath))


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if exitcode == CONTINUE:
    result['MILESTONES'].append({'remove_static_folder_from_html': True})

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
