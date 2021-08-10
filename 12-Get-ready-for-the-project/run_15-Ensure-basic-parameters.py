#!/usr/bin/env python

from __future__ import print_function
from __future__ import absolute_import

import tct
import os
import sys

from tct import deepget

ospabsp = os.path.abspath
ospe = os.path.exists
ospisabs = os.path.isabs
ospisdir = os.path.isdir
ospj = os.path.join
ospnormp = os.path.normpath

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
initial_working_dir = facts["initial_working_dir"]


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

latex_contrib_typo3_folder = None
makedir = ""
makedir_abspath = ""
makedir_missing = ""
resultdir = None
talk = milestones.get("talk", 1)


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append("CHECK PARAMS")
    makedir = lookup(milestones, "makedir", default=None)
    if not makedir:
        msg = (
            "fatal error: parameter 'makedir' is missing\n'"
            "usage:\n"
            "   tct run %s -c makedir MAKEDIR [--toolchain-help]\n" % toolchain_name
        )
        loglist.append(msg)
        print(msg)
        exitcode = 22
        reason = "'makedir' is missing"

if exitcode == CONTINUE:
    loglist.append("PARAMS are ok")
else:
    loglist.append("PROBLEMS with params")


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    if not os.path.isabs(makedir):
        makedir = os.path.join(initial_working_dir, makedir)
    makedir = os.path.abspath(os.path.normpath(makedir))
    if not os.path.isdir(makedir):
        makedir_missing = makedir
        makedir = None
        msg = "makedir not found: %s" % makedir_missing
        loglist.append(msg)
        print(msg)
        exitcode = 22
        reason = "makedir not found"

if exitcode == CONTINUE:
    makedir_abspath = makedir
    if talk > 1:
        print("makedir:", os.path.split(makedir)[1])
        print("makedir_abspath:", makedir_abspath)

if exitcode == CONTINUE:
    resultdir = lookup(milestones, "resultdir")
    if resultdir:
        if not os.path.isabs(resultdir):
            resultdir = ospabsp(ospj(initial_working_dir, resultdir))
        resultdir = os.path.normpath(resultdir)
        if not os.path.isdir(resultdir):
            msg = "fatal error: directory '%s' (resultdir) does not exist." % resultdir
            loglist.append(msg)
            print(msg)
            exitcode = 90
            reason = "resultdir does not exist"

if exitcode == CONTINUE:
    temp = lookup(milestones, "latex_contrib_typo3_folder")
    if temp and not os.path.isabs(temp):
        temp = ospj(initial_working_dir, temp)
        latex_contrib_typo3_folder = os.path.normpath(os.path.abspath(temp))


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if latex_contrib_typo3_folder:
    result["MILESTONES"].append(
        {"latex_contrib_typo3_folder": latex_contrib_typo3_folder}
    )

if makedir:
    result["MILESTONES"].append({"makedir": makedir})

if makedir_abspath:
    result["MILESTONES"].append({"makedir_abspath": makedir_abspath})

if makedir_missing:
    result["MILESTONES"].append({"makedir_missing": makedir_missing})

if resultdir:
    result["MILESTONES"].append({"resultdir": resultdir})

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
