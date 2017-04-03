#!/usr/bin/env python

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
import tct
import os
import sys

params = tct.readjson(sys.argv[1])
facts = tct.readjson(params['factsfile'])
milestones = tct.readjson(params['milestonesfile'])
resultfile = params['resultfile']
result = tct.readjson(resultfile)
toolname = params["toolname"]
toolname_pure = params['toolname_pure']
workdir = params['workdir']
loglist = result['loglist'] = result.get('loglist', [])
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

# Should we verify these do exist?

list_for_which = [
    'bzip2',
    'check_include_files.py',
    'dvips',
    'git',
    'gzip',
    'html2text',
    'latex',
    'makeindex',
    'pandoc',
    'pdflatex',
    'python',
    'python2',
    'python3',
    'sphinx-build',
    't3xutils.phar',
    'tidy',
    ]

known_systemtools = {}

# ==================================================
# Check params
# --------------------------------------------------

pass


# ==================================================
# work
# --------------------------------------------------

import subprocess

for k in list_for_which:
    try:
        v = subprocess.check_output('which ' + k, shell=True)
    except subprocess.CalledProcessError, e:
        v = ''
    known_systemtools[k] = v.strip()

# ==================================================
# Set MILESTONE
# --------------------------------------------------

result['MILESTONES'].append({'known_systemtools': known_systemtools})

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
