#!/usr/bin/env python

from __future__ import print_function
from __future__ import absolute_import
import os
import tct
import sys

#
import shutil

ospe = os.path.exists
ospj = os.path.join

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


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append("CHECK PARAMS")

    documentation_folder = lookup(milestones, "documentation_folder")
    pandoc = lookup(milestones, "known_systemtools", "pandoc")
    if not (documentation_folder and pandoc):
        exitcode = 22
        reason = "Bad PARAMS or nothing to do"

if exitcode == CONTINUE:
    loglist.append("PARAMS are ok")
else:
    loglist.append("Bad PARAMS or nothing to do")


# ==================================================
# work
# --------------------------------------------------

markdown_files = []
result_list = []

if exitcode == CONTINUE:
    for relpath, dirs, files in os.walk(documentation_folder):
        for fname in files:
            if fname.endswith(".md"):
                markdown_files.append(ospj(relpath, fname))

    if markdown_files:
        for fpath in markdown_files:
            mdfile = ospj(documentation_folder, fpath)
            rstfile = mdfile[:-3] + ".rst"
            if ospe(rstfile):
                reason = "existed"
                converted = 0
            else:
                thisexitcode, cmd, out, err = execute_cmdlist(
                    [pandoc, "--from markdown --to rst", mdfile, "-o", rstfile]
                )
                if thisexitcode == 0:
                    reason = ""
                    converted = 1
                else:
                    reason = "exitcode " + str(thisexitcode)
                    converted = 0
            result_list.append((converted, fpath, reason))
    loglist.append((len(result_list), "found"))


# ==================================================
# Set MILESTONE
# --------------------------------------------------
if result_list:
    result["MILESTONES"].append({"markdown_files": result_list})


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
