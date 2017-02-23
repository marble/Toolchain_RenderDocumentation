#!/usr/bin/env python
# coding: utf-8

# Use the above shebang magic line with `env python` to always find the correct Python.
# The `coding: utf-8` comment prepares for non acii characters in the code.

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
import tct
import sys

# Simply always use the following lines to load the most often
# needed basic settings.

# TCT garantees: parameter 1 points to the params.json file
# TCT garantees: parameter 2 points to the `bin` folder
# `workdir` is a temp directory for sole use of this tools.

params = tct.readjson(sys.argv[1])
binabspath = sys.argv[2]
facts = tct.readjson(params['factsfile'])
milestones = tct.readjson(params['milestonesfile'])
resultfile = params['resultfile']
result = tct.readjson(resultfile)
toolname = params["toolname"]
toolname_pure = params['toolname_pure']
workdir = params['workdir']
loglist = result['loglist'] = result.get('loglist', [])
exitcode = CONTINUE = 0

# Execution should only continue while `exitcode == CONTINUE`.
# Make sure to "shield" all actions by an if statement to
# not run into an `undefined variable` situation.


# ==================================================
# Make a copy of milestones for later inspection?
# --------------------------------------------------

# The following call makes a copy of the current milestonesfile.
# It has the same file path as the params file, except that the
# name starts with 'milestones_' instead of 'params_'.
# The copy can be very useful as it shows what milestones existed
# when this tools was run.

if 0 or milestones.get('debug_always_make_milestones_snapshot'):
    tct.make_snapshot_of_milestones(params['milestonesfile'], sys.argv[1])


# ==================================================
# Get and check required milestone(s)
# --------------------------------------------------

# It has turned out that these helper functions are handy. They help to
# (1) retrieve a value by name from our knowledge base, (2) provide
# None or an optional default value and (3) leave an entry in the tools
# logfile

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

# It is good practise to "declare" all the variables here
# that this tool introduces. Set variables to some empty or
# None value for example.

import time

talk = None
time_started_at_unixtime = time.time()
time_started_at = tct.logstamp_finegrained(unixtime=time_started_at_unixtime, fmt='%Y-%m-%d %H:%M:%S %f')
xeq_name_cnt = 0


# ==================================================
# Check params
# --------------------------------------------------

# Usually a tool depends on parameters. It's good practise
# to check them here.

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    # required milestones:
    requirements = [
        'url_of_webroot',
    ]

    # just test:
    for requirement in requirements:
        v = milestones_get(requirement)
        if not v:
            loglist.append("'%s' not found" % requirement)
            exitcode = 2

            # do not break here to get info about all required milestones

    # fetch: the required parameter(s)
    toolchain_name = params_get('toolchain_name')

    # test: Make sure all parameters are set
    if not toolchain_name:
        # To stop the tool, make `exitcode != CONTINUE`.

        # When TCT sees exitcode >= `1`, processing of the following tools
        # IN THIS FOLDER (including subfolders) is skipped.
        # exitcode = 2

        # When TCT sees exitcode `99`, processing of THE WHOLE toolchain
        # is aborted
        exitcode = 99

# Now leave a note in the tool's logfile
if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('PROBLEM exists with required params')

if CONTINUE != 0:
    loglist.append({'CONTINUE': CONTINUE})
    loglist.append('NOTHING to do')

# ==================================================
# work
# --------------------------------------------------

# Here we actually work

# The basic idiom is:

if exitcode == CONTINUE:
    temp = "Do this and that"

if exitcode == CONTINUE:
    temp = "Do this 2 and that 2"

    # To stop further processing IN THIS TOOL:
    # make `exitcode != CONTINUE`

    # Example:

    # Alright, nothing more to do here:
    CONTINUE = -1


if exitcode == CONTINUE:
    # This is an example of how to get a value from deeply nested dictionaries (arrays with name-value-pairs)
    # `tct.deepget(adict, key1, key2, ..., keyN, default=x)` take an arbitrary number of parameters
    talk_builtin = 1
    talk_run_command = tct.deepget(facts, 'run_command', 'talk')
    talk_tctconfig = tct.deepget(facts, 'tctconfig', facts['toolchain_name'], 'talk', default=1)
    talk = int(talk_run_command or talk_tctconfig or talk_builtin)

# only in rare cases something is echoed to stdout
if talk > 1:
    print('# --------', facts['toolchain_name'], time_started_at)


# ==================================================
# Set MILESTONE
# --------------------------------------------------

# This is the usual way to report back achieved `milestones`:
# In the result file we use a key 'MILESTONES' which has a list as value.
# To report milestones we add to that list.

# NOTE:
# Only add milestones (= "things") that actually exist. Otherwise don't
# add the value. For example, use `{'outfile_abspath_planned': '...'}` if the tool only planned it
# but the file doesn't exist. If the tool reports milestone `{'outfile_abspath': '...'}` that file
# should actually exist.

# So in general you write here:

# if milestone_xyz:
#     result['MILESTONES'].append({'milestone_xyz': milestone_xyz})


# NOTE:

# These milestone reporting is usually not protected by the `if exitcode == CONTINUE`
# condition. For this reason you should define possible milestones as False in the
# `define` section at the top.

if talk is not None:
    result['MILESTONES'].append({'talk': talk})

if time_started_at:
    result['MILESTONES'].append({'time_started_at': time_started_at})

if time_started_at_unixtime:
    result['MILESTONES'].append({'time_started_at_unixtime': time_started_at_unixtime})


# ==================================================
# save result
# --------------------------------------------------

# always write the resultfile at the end

tct.writejson(result, resultfile)


# ==================================================
# Return with proper exitcode
# --------------------------------------------------

# always return with the exitcode

sys.exit(exitcode)
