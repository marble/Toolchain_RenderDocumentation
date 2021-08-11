#!/usr/bin/env python

from __future__ import print_function
from __future__ import absolute_import

import codecs
import os
import subprocess
import sys
import tct

from os.path import join as ospj
from tct import deepget

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

from tctlib import execute_cmdlist


class XeqParams:
    xeq_name_cnt = 0
    workdir = workdir
    toolname_pure = toolname_pure


# ==================================================
# Make a copy of milestones for later inspection?
# --------------------------------------------------

if 0 or milestones.get("debug_always_make_milestones_snapshot"):
    tct.make_snapshot_of_milestones(params["milestonesfile"], sys.argv[1])


# ==================================================
# Helper functions
# --------------------------------------------------


def lookup(D, *keys, **kwdargs):
    result = deepget(D, *keys, **kwdargs)
    loglist.append((keys, result))
    return result


# ==================================================
# define
# --------------------------------------------------

publish_dir_latex = None


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append("CHECK PARAMS")

    build_latex = lookup(milestones, "build_latex", default=None)
    builder_latex_folder = lookup(milestones, "builder_latex_folder", default=None)
    resultdir = lookup(milestones, "resultdir", default=None)

    if not (1 and build_latex and builder_latex_folder and resultdir):
        CONTINUE = -2
        reason = "Bad PARAMS or nothing to do"

if exitcode == CONTINUE:
    loglist.append("PARAMS are ok")
else:
    loglist.append("Bad PARAMS or nothing to do")


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    tmp_publish_dir_Result = ospj(resultdir, "Result")
    if not os.path.exists(tmp_publish_dir_Result):
        # strange - not expected
        exitcode = 22
        reason = "Publish dir does not exist"

if exitcode == CONTINUE:
    cmdlist = [
        "rsync",
        "-a",
        "--delete",
        "--exclude",
        ".doctrees",
        '"%s"' % builder_latex_folder.rstrip("/"),
        '"%s/"' % tmp_publish_dir_Result.rstrip("/"),
    ]
    exitcode, cmd, out, err = execute_cmdlist(cmdlist, cwd=workdir, ns=XeqParams)

if exitcode == CONTINUE:
    publish_dir_latex = ospj(
        tmp_publish_dir_Result, os.path.split(builder_latex_folder)[1]
    )


# ==================================================
# Set MILESTONE
# --------------------------------------------------

D = {}

if publish_dir_latex:
    result["MILESTONES"].append({"publish_dir_latex": publish_dir_latex})


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
