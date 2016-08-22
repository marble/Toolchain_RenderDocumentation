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
    build_html = milestones_get('build_html')
    TheProjectLog = milestones_get('TheProjectLog')
    TheProjectResultBuildinfo = milestones_get('TheProjectResultBuildinfo')

if not (build_html and TheProjectLog and TheProjectResultBuildinfo):
    exitcode = 2

if exitcode == CONTINUE:
    warnings_file = None
    warnings_file_size = None

# ==================================================
# work
# --------------------------------------------------

import codecs

if exitcode == CONTINUE:
    src_warnings_file = os.path.join(TheProjectLog, 'html/warnings.txt')
    if not os.path.exists(src_warnings_file):
        exitcode = -2

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

if exitcode == CONTINUE:
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
