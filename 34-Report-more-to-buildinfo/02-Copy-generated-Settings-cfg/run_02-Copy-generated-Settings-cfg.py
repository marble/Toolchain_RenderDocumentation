#!/usr/bin/env python
# coding: utf-8

"""..."""

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
from __future__ import absolute_import
import os
import shutil
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
toolchain_name = facts["toolchain_name"]
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
# define 1
# --------------------------------------------------

buildinfo_settingscfg_file = None


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append("CHECK PARAMS")

    has_settingscfg = lookup(milestones, "has_settingscfg")
    has_settingscfg_generated = lookup(milestones, "has_settingscfg_generated")
    settingscfg_file = lookup(milestones, "settingscfg_file")
    TheProjectResultBuildinfo = lookup(milestones, "TheProjectResultBuildinfo")

    if not (
        has_settingscfg
        and has_settingscfg_generated
        and settingscfg_file
        and TheProjectResultBuildinfo
    ):
        CONTINUE = -2
        reason = "Bad PARAMS or nothing to do"

if exitcode == CONTINUE:
    loglist.append("PARAMS are ok")
else:
    loglist.append("Nothing to do for these PARAMS.")


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    buildinfo_settingscfg_file = os.path.join(TheProjectResultBuildinfo, "Settings.cfg")
    shutil.copy(settingscfg_file, buildinfo_settingscfg_file)

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if buildinfo_settingscfg_file:
    result["MILESTONES"].append(
        {"buildinfo_settingscfg_file": buildinfo_settingscfg_file}
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
