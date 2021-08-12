#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function
from __future__ import absolute_import

import codecs
import os
import shutil
import subprocess
import sys
import tct

from tct import deepget
from os.path import join as ospj, exists as ospe

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
initial_working_dir = facts["initial_working_dir"]
exitcode = CONTINUE = 0

from tctlib import execute_cmdlist


class XeqParams:
    loglist = loglist
    toolname_pure = toolname_pure
    workdir = workdir
    xeq_name_cnt = 0


# ==================================================0
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

gitloginfo_jsonfile = None


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append("CHECK PARAMS")

    buildsettings = lookup(milestones, "buildsettings")
    gitdir = lookup(milestones, "buildsettings", "gitdir")
    TheProject = lookup(milestones, "TheProject")
    TheProjectMakedir = lookup(milestones, "TheProjectMakedir")

    if not (1 and buildsettings and gitdir and TheProject and TheProjectMakedir):
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

    jsonfile_dest = ospj(TheProjectMakedir, "gitloginfo.json")

    # first attempt
    git = lookup(milestones, "known_systemtools", "git")
    if git and not gitloginfo_jsonfile:
        loglist.append(("running in cwd:", gitdir))
        scriptfile = ospj(
            params["toolfolderabspath"],
            "git-restore-mtime/git-restore-mtime-modified.py",
        )
        cmdlist = [
            "python",
            scriptfile,
            "--test",  # don't touch files
            "--no-directories",  # unnotably faster
            "--destfile-gitloginfo=" + jsonfile_dest,
            ".",  # restrict to this tree only
        ]
        exitcode_git, cmd, out, err = execute_cmdlist(cmdlist, cwd=gitdir, ns=XeqParams)
        if exitcode_git == 0 and ospe(jsonfile_dest):
            gitloginfo_jsonfile = jsonfile_dest

    # second attempt
    if not gitloginfo_jsonfile:
        jsonfile_candidate = ospj(TheProject, ".gitloginfo-GENERATED.json")
        if ospe(jsonfile_candidate):
            shutil.copyfile(jsonfile_candidate, jsonfile_dest)
        if ospe(jsonfile_dest):
            gitloginfo_jsonfile = jsonfile_dest

    # third attempt - did a miracle happen?
    if not gitloginfo_jsonfile:
        if ospe(jsonfile_dest):
            gitloginfo_jsonfile = jsonfile_dest


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if gitloginfo_jsonfile:
    result["MILESTONES"].append({"gitloginfo_jsonfile": gitloginfo_jsonfile})


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
