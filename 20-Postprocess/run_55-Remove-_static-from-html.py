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
# Helper functions
# --------------------------------------------------

def lookup(D, *keys, **kwdargs):
    result = tct.deepget(D, *keys, **kwdargs)
    loglist.append((keys, result))
    return result


# ==================================================
# define
# --------------------------------------------------

done_remove_static_folder_from_html = 0
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
        v = lookup(milestones, requirement)
        if not v:
            loglist.append("'%s' not found" % requirement)
            exitcode = 22

    done_replace_static_in_html = lookup(milestones, 'done_replace_static_in_html')
    build_html_folder = lookup(milestones, 'build_html_folder')
    build_singlehtml_folder = lookup(milestones, 'build_singlehtml_folder')

    if not (done_replace_static_in_html and (build_html_folder or build_singlehtml_folder)):
        CONTINUE = -1

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

    import shutil

    todolist = [item for item in [build_html_folder, build_singlehtml_folder] if item]
    for build_folder in todolist:
        if not build_folder:
            continue
        fpath = os.path.join(build_folder, '_static')
        if os.path.exists(fpath):
            shutil.rmtree(fpath)
            loglist.append('%s, %s' % ('remove', fpath))

    done_remove_static_folder_from_html = 1


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if done_remove_static_folder_from_html:
    result['MILESTONES'].append({'done_remove_static_folder_from_html': done_remove_static_folder_from_html})


# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)


# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
