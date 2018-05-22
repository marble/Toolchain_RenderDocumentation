#!/usr/bin/env python
# coding: utf-8

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
import os
import sys
import tct

params = tct.readjson(sys.argv[1])
facts = tct.readjson(params['factsfile'])
milestones = tct.readjson(params['milestonesfile'])
resultfile = params['resultfile']
result = tct.readjson(resultfile)
toolname = params['toolname']
toolname_pure = params['toolname_pure']
toolchain_name = facts['toolchain_name']
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

    build_html = lookup(milestones, 'build_html')
    TheProject = lookup(milestones, 'TheProject')
    TheProjectLog = lookup(milestones, 'TheProjectLog')
    TheProjectResultBuildinfo = lookup(milestones, 'TheProjectResultBuildinfo')

    if not (build_html and TheProject and TheProjectLog
            and TheProjectResultBuildinfo):
        CONTINUE = -1

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('Bad params or nothing to do')


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
    TheProjectLen = len(TheProject)
    warnings_file = os.path.join(TheProjectResultBuildinfo, 'warnings.txt')
    with codecs.open(src_warnings_file, 'r', 'utf-8', 'replace') as f1:
        with codecs.open(warnings_file, 'w', 'utf-8') as f2:
            for line1 in f1:
                if line1.startswith(TheProject):
                    f2.write('.')
                    f2.write(line1[TheProjectLen:])
                elif line1.startswith('/ALL/Makedir/SYMLINK_THE_PROJECT/'):
                    f2.write('.')
                    f2.write(line1[32:])
                else:
                    f2.write(line1)
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
