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

# ==================================================
# Check required milestone(s)
# --------------------------------------------------
def milestones_get(name, default=None):
    result = milestones.get(name, default)
    loglist.append((name, result))
    return result

if exitcode == CONTINUE:
    toolchain_name = params.get('toolchain_name')
    if not toolchain_name:
        exitcode = 99

# ==================================================
# work
# --------------------------------------------------

toolchain_usage = """\
Usage: tct run [OPTIONS] %(toolchain_name)s

  Run the toolchain '%(toolchain_name)s'.

Options:
  -c, --config KEY VALUE         Define or override config key-value pair
                                 (repeatable)
  -n, --dry-run                  Perform a trial run with no changes made.
  --toolchain-help               Tell the toolchain to display its help text.
                                 The toolchain should do that and then exit.
  -T, --toolchain-action ACTION  Tell the toolchain to execute the action.
                                 (repeatable)
  --help                         Show this message and exit.

Toolchain options:
  -c makedir PATH/TO/MAKEDIR     Required! The path to the 'make' folder.
  -c rebuild_needed 1            Force rebuild regardless of checksum
  -T help                        Tell the toolchain to show this help, then exit.
  -T unlock                      Tell the toolchain to remove existing locks, then exit
""" % {'toolchain_name': toolchain_name}

if exitcode == CONTINUE:
    if params.get('toolchain_help') or ('help' in params.get('toolchain_actions', [])):
        exitcode = 99

if exitcode == 99:
    print(toolchain_usage)
    loglist.append('Done: Show usage')

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if 1:
    result['MILESTONES'].append({'toolchain_usage': toolchain_usage})

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
