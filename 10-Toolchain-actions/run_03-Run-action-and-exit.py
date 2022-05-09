#!/usr/bin/env python
# coding: utf-8

from __future__ import absolute_import, print_function

import os
import shutil

import sys
import tct

VERSION = "v3.1.0"

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
# Helper functions
# --------------------------------------------------


def lookup(D, *keys, **kwdargs):
    result = tct.deepget(D, *keys, **kwdargs)
    loglist.append((keys, result))
    return result


# ==================================================
# define
# --------------------------------------------------

lockfiles_removed = []
removed_dirs = []
toolchain_actions = lookup(params, "toolchain_actions", default=[])


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append("CHECK PARAMS")

    lockfile_name = lookup(milestones, "lockfile_name")
    run_id = lookup(facts, "run_id")
    toolchain_temp_home = lookup(params, "toolchain_temp_home")
    if not (lockfile_name and run_id and toolchain_temp_home):
        exitcode = 22
        reason = "Bad params or nothing to do"

if exitcode == CONTINUE:
    loglist.append("PARAMS are ok")
else:
    loglist.append("PROBLEM with required params")


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    if "version" in toolchain_actions:
        print(VERSION)
        exitcode = 90
        reason = "Just show version and stop."

if exitcode == CONTINUE:
    if "unlock" in toolchain_actions:
        for top, dirs, files in os.walk(toolchain_temp_home):
            dirs[:] = []  # stop recursion
            for fname in files:
                if fname == lockfile_name:
                    lockfile = os.path.join(top, fname)
                    os.remove(lockfile)
                    lockfiles_removed.append(lockfile)
        exitcode = 90
        reason = "Just unlock and stop."

if exitcode == CONTINUE:
    if "clean" in toolchain_actions:
        for top, dirs, files in os.walk(toolchain_temp_home):
            dirs.sort()
            for adir in dirs:
                fpath = os.path.join(top, adir)
                if not run_id in adir:
                    if os.path.isdir(fpath):
                        shutil.rmtree(fpath)
            dirs[:] = []  # stop recursion
        exitcode = 90
        reason = "Just clean and stop."


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if exitcode == 90:
    result["MILESTONES"].append({"FINAL_EXITCODE": 0})

if lockfiles_removed:
    result["MILESTONES"].append({"lockfiles_removed": lockfiles_removed})


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
