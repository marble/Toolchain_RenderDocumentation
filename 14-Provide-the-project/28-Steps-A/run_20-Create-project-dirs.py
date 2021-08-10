#!/usr/bin/env python

from __future__ import print_function
from __future__ import absolute_import
import os
import sys
import tct

params = tct.readjson(sys.argv[1])
facts = tct.readjson(params["factsfile"])
milestones = tct.readjson(params["milestonesfile"])
reason = ""
resultfile = params["resultfile"]
result = tct.readjson(resultfile)
toolname = params["toolname"]
toolname_pure = params["toolname_pure"]
toolchain_name = facts["toolchain_name"]
workdir = params["workdir"]
loglist = result["loglist"] = result.get("loglist", [])
exitcode = CONTINUE = 0


# ==================================================
# Make a copy of milestones for later inspection?
# --------------------------------------------------

if 0 or milestones.get("debug_always_make_milestones_snapshot"):
    tct.make_snapshot_of_milestones(params["milestonesfile"], sys.argv[1])


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

TheProjectLog = None
TheProjectBuild = None
TheProjectWebroot = None


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append("CHECK PARAMS")

    TheProject = lookup(milestones, "TheProject", default=None)

    if not TheProject:
        exitcode = 22
        reason = "Bad PARAMS or nothing to do"

if exitcode == CONTINUE:
    loglist.append("PARAMS are ok")
else:
    loglist.append("Bad PARAMS or nothing to do")


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:

    resultdir = lookup(milestones, "resultdir", default=None)

    TheProjectLog = TheProject + "Log"
    if not os.path.exists(TheProjectLog):
        os.makedirs(TheProjectLog)

    TheProjectBuild = TheProject + "Build"
    if not os.path.exists(TheProjectBuild):
        os.makedirs(TheProjectBuild)

    if resultdir:
        TheProjectWebroot = os.path.join(resultdir, "Result")
    else:
        TheProjectWebroot = TheProject + "Webroot"

    if not os.path.exists(TheProjectWebroot):
        os.makedirs(TheProjectWebroot)


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if TheProjectBuild:
    result["MILESTONES"].append({"TheProjectBuild": TheProjectBuild})

if TheProjectLog:
    result["MILESTONES"].append({"TheProjectLog": TheProjectLog})

if TheProjectWebroot:
    result["MILESTONES"].append({"TheProjectWebroot": TheProjectWebroot})


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
