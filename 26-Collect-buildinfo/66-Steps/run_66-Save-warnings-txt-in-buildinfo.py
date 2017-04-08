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
warnings_file = None
warnings_file_size = None


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
            exitcode = 22

    build_html = milestones_get('build_html')
    TheProjectLog = milestones_get('TheProjectLog')
    TheProjectResultBuildinfo = milestones_get('TheProjectResultBuildinfo')

    if not (build_html and TheProjectLog and TheProjectResultBuildinfo):
        exitcode = 22

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

import codecs

if exitcode == CONTINUE:
    src_warnings_file = os.path.join(TheProjectLog, 'html/warnings.txt')
    if not os.path.exists(src_warnings_file):
        loglist.append(('warnings.txt file not found', src_warnings_file))
        CONTINUE = -2

if exitcode == CONTINUE:
    warnings_file = os.path.join(TheProjectResultBuildinfo, 'warnings.txt')
    with codecs.open(src_warnings_file, 'r', 'utf-8', 'replace') as f1:
        with codecs.open(warnings_file, 'w', 'utf-8') as f2:
            for line1 in f1:
                line2 = line1
                if line1.startswith('/home/'):
                    p = line1.find('/TheProject/')
                    if p > -1:
                        line2 = line1[p+1:]
                f2.write(line2)
        statinfo = os.stat(warnings_file)
        warnings_file_size = statinfo.st_size


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if warnings_file:
    result['MILESTONES'].append({'warnings_file': warnings_file,
                                 'warnings_file_size': warnings_file_size,
                                 })


# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)


# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
