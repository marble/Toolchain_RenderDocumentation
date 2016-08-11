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
# work
# --------------------------------------------------

usage = """\
Usage: tct run [OPTIONS] Process_makedir

  Run a toolchain 'Process_makedir'.

Options:
  -c, --config KEY VALUE  Define or override config key-value pair
                          (repeatable)

  -c, --config makedir PATH/TO/MAKEDIR
                           Required! The path to the 'make' folder.

  -c, --config rebuild_needed 1
                           Force rebuild.

  -n, --dry-run            Perform a trial run with no changes made.
  --help                   Show this message and exit.
"""

if exitcode == CONTINUE:
    for line in usage.split('\n'):
        loglist.append(line)


if exitcode == CONTINUE:
    makedir = params.get('makedir', '')
    if not makedir:
        errormsg = "Error: Parameter 'makedir' is missing. \nAdd: --config makedir PATH/TO/MAKEDIR\nFor help run: tct run TOOLCHAIN -c usage 1"
        exitcode = 99


if exitcode == CONTINUE:
    if not os.path.isabs(makedir):
        makedir = os.path.join(facts['cwd'], makedir)
    makedir = os.path.abspath(os.path.normpath(makedir))
    if not os.path.exists(makedir):
        errormsg = "Error: Cannot find makedir '%s'. \nAdd: --config makedir PATH/TO/MAKEDIR\nFor help run: tct run TOOLCHAIN -c usage 1" % makedir
        exitcode = 99

if exitcode == CONTINUE:
    if not os.path.isdir(makedir):
        errormsg = "Error: makedir is not a directory ('%s'). \nAdd: --config makedir PATH/TO/MAKEDIR\nFor help run: tct run TOOLCHAIN -c usage 1" % makedir
        exitcode = 99

if errormsg:
    loglist.append('errormsg: ' + errormsg)
    print(errormsg)

if helpmsg:
    loglist.append('helpmsg: ' + helpmsg)
    print(helpmsg)


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
