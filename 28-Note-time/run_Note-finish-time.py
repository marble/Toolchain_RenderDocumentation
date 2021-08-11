#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function
from __future__ import absolute_import
import os
import tct
import sys

params = tct.readjson(sys.argv[1])
binabspath = sys.argv[2]
facts = tct.readjson(params["factsfile"])
milestones = tct.readjson(params["milestonesfile"])
reason = ""
resultfile = params["resultfile"]
result = tct.readjson(resultfile)
loglist = result["loglist"] = result.get("loglist", [])
toolname = params["toolname"]
toolname_pure = params["toolname_pure"]
workdir = params["workdir"]
exitcode = CONTINUE = 0


# ==================================================
# Make a copy of milestones for later inspection?
# --------------------------------------------------

if 0 or milestones.get("debug_always_make_milestones_snapshot"):
    tct.make_snapshot_of_milestones(params["milestonesfile"], sys.argv[1])


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

import time

# we need to "fake" a finish time now to be able to
# report that in the following notifications.

time_finished_at_unixtime = time.time()
time_finished_at = tct.logstamp_finegrained(
    unixtime=time_finished_at_unixtime, fmt="%Y-%m-%d %H:%M:%S %f"
)


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append("CHECK PARAMS")

if exitcode == CONTINUE:
    loglist.append("PARAMS are ok")
else:
    loglist.append("Bad PARAMS or nothing to do")


# ==================================================
# work
# --------------------------------------------------

pass


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if time_finished_at:
    result["MILESTONES"].append({"time_finished_at": time_finished_at})

if time_finished_at_unixtime:
    result["MILESTONES"].append(
        {"time_finished_at_unixtime": time_finished_at_unixtime}
    )


# ==================================================
# save result
# --------------------------------------------------

tct.save_the_result(
    result, resultfile, params, facts, milestones, exitcode, CONTINUE, reason
)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
