#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function
from __future__ import absolute_import
import codecs
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
exitcode = CONTINUE = 0


# masterdoc ?
# t3docdir  ?


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

buildsettings_file = None
buildsettings_file_fixed = None
LOGDIR_line = None
MASTERDOC_line = None
T3DOCDIR_line = None


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append("CHECK PARAMS")
    TheProjectLog = lookup(milestones, "TheProjectLog")
    if not (TheProjectLog):
        exitcode = 22
        reason = "Bad PARAMS or nothing to do"

if exitcode == CONTINUE:
    loglist.append("PARAMS are ok")
else:
    loglist.append("PROBLEMS with params")


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    documentation_folder = lookup(milestones, "documentation_folder")
    masterdoc = lookup(milestones, "masterdoc")
    TheProjectMakedir = lookup(milestones, "TheProjectMakedir")
    if not (masterdoc and TheProjectMakedir and documentation_folder):
        loglist.append("SKIPPING")
        CONTINUE = -2
        reason = "Skipping"


if exitcode == CONTINUE:
    buildsettings_file = os.path.join(TheProjectMakedir, "buildsettings.sh")
    if not os.path.exists(buildsettings_file):
        with open(buildsettings_file, "w") as f2:
            pass
    original = buildsettings_file + ".original"
    shutil.move(buildsettings_file, original)

if exitcode == CONTINUE:
    masterdoc_without_fileext = os.path.splitext(masterdoc)[0]
    with codecs.open(original, "r", "utf-8") as f1:
        with codecs.open(buildsettings_file, "w", "utf-8") as f2:
            for line in f1:
                if line.startswith("MASTERDOC="):
                    MASTERDOC_line = "MASTERDOC=" + masterdoc_without_fileext + "\n"
                    loglist.append(("MASTERDOC_line", MASTERDOC_line))
                    line = MASTERDOC_line
                elif line.startswith("LOGDIR="):
                    LOGDIR_line = "LOGDIR=" + TheProjectLog + "\n"
                    loglist.append(("LOGDIR_line", LOGDIR_line))
                    line = LOGDIR_line
                elif line.startswith("T3DOCDIR="):
                    tail = ""
                    line = line.strip()
                    if not line.endswith("/Documentation"):
                        splitted = line.split("/Documentation")
                        if len(splitted) > 1:
                            tail = splitted[-1].strip().strip("/")
                        if tail:
                            # tail should be 'Localization.xx_XX'
                            tail = "/" + tail
                    T3DOCDIR_line = "T3DOCDIR=" + documentation_folder + tail + "\n"
                    loglist.append(("T3DOCDIR_line", T3DOCDIR_line))
                    line = T3DOCDIR_line
                f2.write(line)
    buildsettings_file_fixed = True


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if buildsettings_file:
    result["MILESTONES"].append({"buildsettings_file": buildsettings_file})

if buildsettings_file_fixed:
    result["MILESTONES"].append({"buildsettings_file_fixed": buildsettings_file_fixed})


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
