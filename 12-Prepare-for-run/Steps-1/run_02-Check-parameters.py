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
loglist = result['loglist'] = result.get('loglist', [])
exitcode = CONTINUE = 0
errormsg = ''
helpmsg = ''

# ==================================================
# Get and check required milestone(s)
# --------------------------------------------------
def milestones_get(name, default=None):
    result = milestones.get(name, default)
    loglist.append((name, result))
    return result

if exitcode == CONTINUE:
    toolchain_name = facts.get('toolchain_name')
    toolchain_usage = milestones_get('toolchain_usage')

if not toolchain_name:
    exitcode = 99

# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    for line in toolchain_usage.split('\n'):
        loglist.append(line)

if exitcode == CONTINUE:
    makedir = params.get('makedir', '')
    if not makedir:
        errormsg = 'Usage: tct run %s --config makedir MAKEDIR [--toolchain-help]\nmakedir is not specified' % toolchain_name
        exitcode = 2

if exitcode == CONTINUE:
    if not os.path.isabs(makedir):
        makedir = os.path.join(facts['cwd'], makedir)
    makedir = os.path.abspath(os.path.normpath(makedir))
    if not os.path.isdir(makedir):
        errormsg = "makedir not found: '%s'" % makedir
        exitcode = 2

if errormsg:
    loglist.append(errormsg)
    print(errormsg)


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if exitcode == CONTINUE:
    result['MILESTONES'].append({'makedir': makedir})

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
