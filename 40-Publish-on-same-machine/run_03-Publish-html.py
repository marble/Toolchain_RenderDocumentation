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

publish_dir = None
publish_dir_buildinfo = None
publish_html_done = None
publish_language_dir = None
publish_project_dir = None
publish_project_parent_dir = None
publish_removed_old = None


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append("CHECK PARAMS")

    build_html = lookup(milestones, "build_html", default=None)
    TheProjectResult = lookup(milestones, "TheProjectResult", default=None)
    TheProjectResultVersion = lookup(
        milestones, "TheProjectResultVersion", default=None
    )

    if not (1 and build_html and TheProjectResult and TheProjectResultVersion):
        # stop this folder
        exitcode = 22
        reason = "Bad params"

if exitcode == CONTINUE:
    loglist.append("CHECK PARAMS")

    publish_dir_planned = lookup(milestones, "publish_dir_planned", default=None)
    publish_language_dir_planned = lookup(
        milestones, "publish_language_dir_planned", default=None
    )
    publish_project_dir_planned = lookup(
        milestones, "publish_project_dir_planned", default=None
    )
    publish_project_parent_dir_planned = lookup(
        milestones, "publish_project_parent_dir_planned", default=None
    )
    TheProjectResult = lookup(milestones, "TheProjectResult", default=None)
    TheProjectResultVersion = lookup(
        milestones, "TheProjectResultVersion", default=None
    )

    if not (
        publish_dir_planned
        and publish_language_dir_planned
        and publish_project_dir_planned
        and publish_project_parent_dir_planned
        and TheProjectResult
        and TheProjectResultVersion
    ):
        # stop processing of rest of folder
        exitcode = 22
        reason = "Bad params"

if exitcode == CONTINUE:
    loglist.append("PARAMS are ok")
else:
    loglist.append("Bad PARAMS or nothing to do")


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:

    if not os.path.exists(publish_project_parent_dir_planned):
        os.makedirs(publish_project_parent_dir_planned)
    publish_project_parent_dir = publish_project_parent_dir_planned

    if not os.path.exists(publish_project_dir_planned):
        os.mkdir(publish_project_dir_planned)
    publish_project_dir = publish_project_dir_planned

    if not os.path.exists(publish_dir_planned):
        os.makedirs(publish_dir_planned)
    publish_dir = publish_dir_planned

if exitcode == CONTINUE:
    cmdlist = [
        "rsync",
        "-a",
        "--delete",
        "--exclude",
        ".doctrees",
        '"%s/"' % TheProjectResultVersion.rstrip("/"),
        '"%s/"' % publish_dir.rstrip("/"),
    ]
    exitcode, cmd, out, err = execute_cmdlist(cmdlist, cwd=workdir, ns=XeqParams)
    if exitcode != 0:
        publish_dir = None

if exitcode == CONTINUE:
    publish_language_dir = publish_project_dir_planned

if exitcode == CONTINUE:
    publish_html_done = 1
    publish_dir_buildinfo_planned = lookup(
        milestones, "publish_dir_buildinfo_planned", default=None
    )
    if publish_dir_buildinfo_planned and os.path.isdir(publish_dir_buildinfo_planned):
        publish_dir_buildinfo = publish_dir_buildinfo_planned


# ==================================================
# Set MILESTONE
# --------------------------------------------------

D = {}

if publish_html_done:
    D["publish_html_done"] = publish_html_done

if publish_removed_old:
    D["publish_removed_old"] = publish_removed_old

if publish_project_dir:
    D["publish_project_dir"] = publish_project_dir

if publish_project_parent_dir:
    D["publish_project_parent_dir"] = publish_project_parent_dir

if publish_dir:
    D["publish_dir"] = publish_dir

if publish_language_dir:
    D["publish_language_dir"] = publish_language_dir

if publish_project_dir:
    D["publish_project_dir"] = publish_project_dir

if publish_dir_buildinfo:
    D["publish_dir_buildinfo"] = publish_dir_buildinfo

if D:
    result["MILESTONES"].append(D)

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
