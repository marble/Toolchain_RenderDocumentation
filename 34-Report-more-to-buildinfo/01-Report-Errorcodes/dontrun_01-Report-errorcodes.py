#!/usr/bin/env python
# coding: utf-8

"""
To be written ...

...
"""

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
from __future__ import absolute_import
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
toolname = params['toolname']
toolname_pure = params['toolname_pure']
workdir = params['workdir']
toolchain_name = facts['toolchain_name']
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


# ==================================================
# define
# --------------------------------------------------

final_exitcode = 0
talk = lookup(milestones, default=0)
xeq_name_cnt = 0

publish_dir_buildinfo = None
publish_dir_buildinfo_exitcodes = None

TheProjectResultBuildinfo = None
TheProjectResultBuildinfoExitcodes = None


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    tools_exitcodes = lookup(milestones, 'tools_exitcodes', default={})
    # publish_dir_buildinfo = lookup(milestones, 'publish_dir_buildinfo')
    TheProjectResultBuildinfo = lookup(milestones, 'TheProjectResultBuildinfo')

    if not (tools_exitcodes and TheProjectResultBuildinfo):
        CONTINUE = -2

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
    D = {}
    cnt = 0
    for k in sorted(tools_exitcodes):
        cnt += 1
        v = tools_exitcodes[k]
        k2 = '%3d | %3s | %s' % (cnt, v, k)
        D[k2] = v

    if publish_dir_buildinfo:
        publish_dir_buildinfo_exitcodes = os.path.join(publish_dir_buildinfo, 'exitcodes.json')
        tct.writejson(D, publish_dir_buildinfo_exitcodes)

    if TheProjectResultBuildinfo:
        TheProjectResultBuildinfoExitcodes = os.path.join(TheProjectResultBuildinfo, 'exitcodes.json')
        tct.writejson(D, TheProjectResultBuildinfoExitcodes)


if exitcode == CONTINUE:
    for k, v in tools_exitcodes.items():
        if v != 0 and v != 22:
            final_exitcode = 1
            break

if exitcode == CONTINUE:
    if talk >= 2 and not (final_exitcode == 0):
        print(tct.data2json(D))


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if publish_dir_buildinfo_exitcodes:
    result['MILESTONES'].append({'publish_dir_buildinfo_exitcodes': publish_dir_buildinfo_exitcodes})

if TheProjectResultBuildinfoExitcodes:
    result['MILESTONES'].append({'TheProjectResultBuildinfoExitcodes': TheProjectResultBuildinfoExitcodes})

if final_exitcode is not None:
    result['MILESTONES'].append({'FINAL_EXITCODE': final_exitcode})


# ==================================================
# save result
# --------------------------------------------------

tct.save_the_result(result, resultfile, params, facts, milestones, exitcode, CONTINUE, reason)


# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
