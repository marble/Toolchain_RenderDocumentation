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
toolchain_name = facts['toolchain_name']
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

deepget = tct.deepget

def lookup(D, *keys, **kwdargs):
    result = deepget(D, *keys, **kwdargs)
    loglist.append((keys, result))
    return result


# ==================================================
# define
# --------------------------------------------------

TheProjectResultBuildinfoResultJsonfile = None
xeq_name_cnt = 0


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    TheProjectResultBuildinfo = lookup(milestones, 'TheProjectResultBuildinfo')

    if not (TheProjectResultBuildinfo):
        CONTINUE = -2

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('Nothing to do for these params')


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    TheProjectResultBuildinfoResultJsonfile = os.path.join(TheProjectResultBuildinfo, 'results.json')

    mapping = {'checksum_new': 'checksum'}
    keys = [
        "checksum_new",
        "checksum_old",
        "checksum_time",
        "checksum_time_decoded",
        "checksum_ttl_seconds",
    ]
    R = {}
    for k in keys:
        v = milestones.get(k)
        if v is not None:
            k2 = mapping.get(k, k)
            R[k2] = v
    tct.writejson(R, TheProjectResultBuildinfoResultJsonfile)

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if TheProjectResultBuildinfoResultJsonfile:
    result['MILESTONES'].append({
        'TheProjectResultBuildinfoResultJsonfile':
        TheProjectResultBuildinfoResultJsonfile})


# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)


# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
