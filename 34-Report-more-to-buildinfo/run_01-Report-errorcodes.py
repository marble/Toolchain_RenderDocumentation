#!/usr/bin/env python
# coding: utf-8

"""
Report errorcodes

This tool writes a human readable json file :file:`exitcodes.json`
to the buildinfo folder if that folder exists. The file lists the
tools in the order that they were run together with their exitcodes.

If there are no exitcodes then the `final_exitcode` is `None`.
Otherwise the `final_exitcode` is `0`, if all exitcodes are zero.
If non-zero exitcodes exist the `final_exitcode` is set to `1`.

For `RenderDocumentation -c talk 2` the contents of :file:`exitcodes.json`
is echoed to the console.

"""

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

final_exitcode = 0
talk_builtin = 1
talk_run_command = tct.deepget(facts, 'run_command', 'talk')
talk_tctconfig = tct.deepget(facts, 'tctconfig', facts['toolchain_name'], 'talk')
talk = int(talk_run_command or talk_tctconfig or talk_builtin)
publish_dir_buildinfo_exitcodes = None
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

    # fetch

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
    tools_exitcodes = milestones.get('tools_exitcodes', {})
    publish_dir_buildinfo = milestones_get('publish_dir_buildinfo')
    if 0:
        if not (publish_dir_buildinfo and tools_exitcodes):
            loglist.append('no buildinfo, nothing to do')
            CONTINUE = -1

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
        loglist.append(('publish_dir_buildinfo_exitcodes', publish_dir_buildinfo_exitcodes))

if exitcode == CONTINUE:
    for k, v in tools_exitcodes.items():
        if v != 0 and v != 2:
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

if final_exitcode is not None:
    result['MILESTONES'].append({'FINAL_EXITCODE': final_exitcode})


# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)


# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
