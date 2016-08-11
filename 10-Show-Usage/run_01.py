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

usage = """
Usage: tct run [OPTIONS] Process_makedir

  Run a toolchain 'Process_makedir'.

Options:
  -c, --config KEY VALUE  Define or override config key-value pair
                          (repeatable)

  -c, --config makedir PATH/TO/MAKEDIR
                           Required! The path to the 'make' folder.

  -c, --config rebuild_needed 1
                           Force rebuild.

  -c, --config usage 1
                           Show usage and exit.

  -n, --dry-run            Perform a trial run with no changes made.
  --help                   Show this message and exit.
"""

if exitcode == CONTINUE:
    if params.get('usage'):
        print(usage)
        exitcode = 99

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if exitcode == 99:
    result['MILESTONES'].append({'show_usage': True})

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
