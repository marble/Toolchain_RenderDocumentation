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

toolchain_usage = False


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')
    toolchain_name = params_get('toolchain_name')
    if not toolchain_name:
        exitcode = 99

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('PROBLEMS with params')


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
  -T clean                       Let the toolchain delete prior builds, then exit.
  -T help                        Let the toolchain show this help, then exit.
  -T unlock                      Let the toolchain remove existing locks, then exit

  -c makedir PATH/TO/MAKEDIR     Required! The path to the 'make' folder.
  -c rebuild_needed 1            Force rebuild regardless of checksum

  -c make_singlehtml 1           yes (default)
  -c make_singlehtml 0           no

  -c make_latex 1                yes! Make LaTeX and PDF(default)
  -c make_latex 0                no

  -c make_package 1              yes (default)
  -c make_package 0              no

  -c talk 0                      run quietly
  -c talk 1                      talk just the minimum (default)
  -c talk 2                      talk more

  -c email_user_to  "email1,email2,..."  instead of real user
  -c email_user_cc  "email1,email2,..."  additionally, publicly
  -c email_user_bcc "email1,email2,..."  additionally, secretly
  -c email_user_send_to_admin_too  1     like it says

""" % {'toolchain_name': toolchain_name}

if exitcode == CONTINUE:
    if params.get('toolchain_help') or ('help' in params.get('toolchain_actions', [])):
        print(toolchain_usage)
        exitcode = 90


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if toolchain_usage:
    result['MILESTONES'].append({'toolchain_usage': toolchain_usage})

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
