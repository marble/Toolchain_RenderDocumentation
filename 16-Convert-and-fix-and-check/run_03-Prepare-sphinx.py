#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function
from __future__ import absolute_import
import os
import tct
import sys
from tctlib import cmdline

params = tct.readjson(sys.argv[1])
facts = tct.readjson(params["factsfile"])
milestones = tct.readjson(params["milestonesfile"])
reason = ""
resultfile = params["resultfile"]
result = tct.readjson(resultfile)
toolname = params["toolname"]
toolname_pure = params["toolname_pure"]
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


def lookup(D, *keys, **kwdargs):
    result = tct.deepget(D, *keys, **kwdargs)
    loglist.append((keys, result))
    return result


# ==================================================
# define
# --------------------------------------------------

ready_for_build = False
ready_for_build_vars = None
SPHINXBUILD = None


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append("CHECK PARAMS")
    buildsettings_file_fixed = lookup(milestones, "buildsettings_file_fixed")
    makedir = lookup(milestones, "makedir")
    masterdoc = lookup(milestones, "masterdoc")
    TheProject = lookup(milestones, "TheProject")
    TheProjectBuild = lookup(milestones, "TheProjectBuild")
    TheProjectLog = lookup(milestones, "TheProjectLog")

    if not (
        buildsettings_file_fixed
        and makedir
        and masterdoc
        and TheProject
        and TheProjectBuild
        and TheProjectLog
    ):
        exitcode = 22
        reason = "Bad PARAMS or nothing to do"

if exitcode == CONTINUE:
    loglist.append("PARAMS are ok")
else:
    loglist.append("PROBLEM with params")

# ==================================================
# work
# --------------------------------------------------

import subprocess

if exitcode == CONTINUE:
    has_settingscfg = lookup(milestones, "has_settingscfg")
    rebuild_needed = lookup(milestones, "rebuild_needed")


if exitcode == CONTINUE:

    if not SPHINXBUILD:
        this_exitcode, cmd, out, err = cmdline("which sphinx-build")
        SPHINXBUILD = out.strip()
        loglist.append([this_exitcode, cmd, out, err])

    if "just a test":
        this_exitcode, cmd, out, err = cmdline("sphinx-build --help")
        loglist.append([this_exitcode, cmd, out, err])

    ready_for_build_vars = [
        TheProject,
        TheProjectBuild,
        TheProjectLog,
        SPHINXBUILD,
        makedir,
        masterdoc,
        buildsettings_file_fixed,
    ]
    ready_for_build_vars_str = "[TheProject, TheProjectBuild, TheProjectLog, SPHINXBUILD, makedir, masterdoc, buildsettings_file_fixed]"

    loglist.append(
        {
            "ready_for_build_vars_str": ready_for_build_vars_str,
            "ready_for_build_vars": ready_for_build_vars,
        }
    )

    # All variables set (!= False)?
    ready_for_build = not any([not v for v in ready_for_build_vars])


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if SPHINXBUILD:
    result["MILESTONES"].append({"SPHINXBUILD": SPHINXBUILD})

if ready_for_build:
    result["MILESTONES"].append({"ready_for_build": ready_for_build})

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
