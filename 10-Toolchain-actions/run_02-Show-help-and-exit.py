#!/usr/bin/env python

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
from __future__ import absolute_import
import tct
import os
import sys

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

def lookup(D, *keys, **kwdargs):
    result = tct.deepget(D, *keys, **kwdargs)
    loglist.append((keys, result))
    return result


# ==================================================
# define
# --------------------------------------------------

show_toolchain_usage_and_exit = None


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

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
  -c, --config KEY VALUE          Define or override config key-value pair
                                  (repeatable)
  -n, --dry-run                   Perform a trial run with no changes made.
  --toolchain-help                Tell the toolchain to display its help text.
                                  The toolchain should do that and then exit.
  -T, --toolchain-action ACTION   Tell the toolchain to execute the action.
                                  (repeatable)
  --help                          Show this message and exit.

Toolchain options:
  -T clean                        Let the toolchain delete prior builds, then exit.
  -T help                         Show toolchain help and e exit.
  -T unlock                       Remove possible lock and exit.
  -T version                      Show toolchain version and exit.

  -c makedir PATH/TO/MAKEDIR      Required! The path to the 'make' folder.
  -c resultdir PATH/TO/MAKEDIR    Optional. The path to the 
                                  'Documentation-GENERATED-temp' folder. Must
                                  exist if specified.

  -c buildsettings PATH/TO/FILE   If specified, this file overrides the normal
                                  makedir/buildsettings.sh

  -c overrides PATH/TO/FILE       If specified, this file is used instead of the
                                  normal makedir/Overrides.cfg

  -c rebuild_needed 1             Force rebuild regardless of checksum

  -c make_singlehtml 1            yes (default)
  -c make_singlehtml 0            no

  -c make_latex 1                 yes! Make LaTeX and PDF(default)
  -c make_latex 0                 no

  -c make_package 1               yes (default)
  -c make_package 0               no

  -c talk 0                       run quietly
  -c talk 1                       talk just the minimum (default)
  -c talk 2                       talk more

  -c jobfile PATH/TO/JOBFILE.JSON  pass in all kind of settings

  -c email_user_to_instead  "email1,email2,..."  instead of real user
  -c email_user_cc  "email1,email2,..."  additionally, publicly
  -c email_user_bcc "email1,email2,..."  additionally, secretly
  -c email_user_send_to_admin_too  1     like it says

""" % {'toolchain_name': toolchain_name}

if exitcode == CONTINUE:
    if params.get('toolchain_help') or ('help' in params.get('toolchain_actions', [])):
        show_toolchain_usage_and_exit = 1
        if show_toolchain_usage_and_exit:
            print(toolchain_usage)
            exitcode = 90


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if show_toolchain_usage_and_exit:
    result['MILESTONES'].append({'show_toolchain_usage_and_exit':
                                     show_toolchain_usage_and_exit})

# ==================================================
# save result
# --------------------------------------------------

tct.save_the_result(result, resultfile, params, facts, milestones, exitcode, CONTINUE)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
