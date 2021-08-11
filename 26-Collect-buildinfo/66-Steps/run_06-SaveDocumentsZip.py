#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function
from __future__ import absolute_import

import codecs
import os
import subprocess
import sys
import tct

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
toolchain_name = facts["toolchain_name"]
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

TheProjectResultBuildinfoDocumentationGenerated = None
DocumentationGeneratedZipFile = None


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append("CHECK PARAMS")

    TheProject = lookup(milestones, "TheProject", default=None)
    TheProjectBuildOpenOffice2Rest = lookup(
        milestones, "TheProjectBuildOpenOffice2Rest", default=None
    )
    TheProjectDocumentation = lookup(
        milestones, "TheProjectDocumentation", default=None
    )
    TheProjectResultBuildinfo = lookup(
        milestones, "TheProjectResultBuildinfo", default=None
    )
    zip_systemtool = lookup(milestones, "known_systemtools", "zip", default="").strip()

    if not (
        1
        and TheProject
        and TheProjectResultBuildinfo
        and TheProjectBuildOpenOffice2Rest
        and TheProjectDocumentation
        and zip_systemtool
    ):
        CONTINUE = -2
        reason = "warnings.txt file not found"

if exitcode == CONTINUE:
    loglist.append("PARAMS are ok")
else:
    loglist.append("Bad PARAMS or nothing to do")

# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    DocumentationGeneratedZipFile = "Documentation.zip.GENERATED.zip"
    TheProjectResultBuildinfoDocumentationGenerated = os.path.join(
        TheProjectResultBuildinfo, DocumentationGeneratedZipFile
    )

    exitcode_, cmd, out, err = execute_cmdlist(
        [
            zip_systemtool,
            "-r",
            TheProjectResultBuildinfoDocumentationGenerated,
            TheProjectDocumentation[len(TheProject) :].lstrip("/"),
        ],
        cwd=TheProject,
        ns=XeqParams,
    )

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if TheProjectResultBuildinfoDocumentationGenerated:
    result["MILESTONES"].append(
        {"TheProjectResultBuildinfoDocumentationGenerated": TheProjectDocumentation}
    )

if DocumentationGeneratedZipFile:
    result["MILESTONES"].append(
        {"DocumentationGeneratedZipFile": DocumentationGeneratedZipFile}
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
