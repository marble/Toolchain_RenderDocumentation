#!/usr/bin/env python
# coding: utf-8

"""..."""

# ==================================================
# open
# --------------------------------------------------

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
toolchain_name = facts["toolchain_name"]
workdir = params["workdir"]
exitcode = CONTINUE = 0

# Let's disable this feature. It's wasting disk space
# and doesn't seem necessary any more since the Docker
# container for easy local rendering is available.

CONTINUE = -2
reason = "Tool is turned OFF for now"


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

buildinfo_latex_folder = None

# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append("CHECK PARAMS")

    # essential
    TheProjectResultBuildinfo = lookup(milestones, "TheProjectResultBuildinfo")
    latex_file = lookup(milestones, "latex_file")
    if not latex_file:
        loglist.append("Nothing to do - we have no PROJECT.tex file")
        CONTINUE = -2

if exitcode == CONTINUE:
    pdf_file = lookup(milestones, "pdf_file")
    if pdf_file:
        loglist.append("Nothing to do - we already have the PROJECT.pdf file")
        CONTINUE = -2

if exitcode == CONTINUE:
    # may be of interest
    builds_successful = lookup(milestones, "builds_successful", default=[])
    latex_successful = "latex" in builds_successful
    latex_make_file = lookup(milestones, "latex_make_file")
    latex_make_file_tweaked = lookup(milestones, "latex_make_file_tweaked")

if exitcode == CONTINUE:
    loglist.append("Ok, PARAMS permit continuation.")
else:
    loglist.append("No, cannot work with these PARAMS.")


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    source_folder = os.path.split(latex_file)[0]
    source_folder_name = os.path.split(source_folder)[1]
    buildinfo_latex_folder = os.path.join(TheProjectResultBuildinfo, source_folder_name)
    destination_folder = buildinfo_latex_folder
    loglist.append(
        [
            "shutil.copytree(source_folder, destination_folder) with",
            source_folder,
            destination_folder,
        ]
    )

    # import shutil
    # doesn't work. Why???
    # shutil.copytree(source_folder, destination_folder)

    import subprocess

    cmd = "cp -r " + source_folder + " " + TheProjectResultBuildinfo
    subprocess.call(cmd, shell=True)


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if buildinfo_latex_folder:
    result["MILESTONES"].append({"buildinfo_latex_folder": buildinfo_latex_folder})


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
