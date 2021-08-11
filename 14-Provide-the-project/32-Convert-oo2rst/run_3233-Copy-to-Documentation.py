#!/usr/bin/env python

from __future__ import print_function
from __future__ import absolute_import
import os
import tct
import sys

#
import normalize_empty_lines
import prepend_sections_with_labels
import tweak_dllisttables
import shutil

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

TheProjectDocumentation = None
TheProjectDocumentationManualFile = None
TheProjectDocumentationSaved = None
masterdoc_manual_rst_selected = None

dummy = {
    "masterdoc_manual_html_005_as_rst": {
        "dl": {
            "outfile": "/home/marble/Repositories/mbnas/mbgit/Rundir/00-TEMPROOT_NOT_VERSIONED/RenderDocumentation/2017-11-15_15-01-29_607017/TheProjectBuild/OpenOffice2Rest/manual-005.dl.rst"
        },
        "t3flt": {
            "outfile": "/home/marble/Repositories/mbnas/mbgit/Rundir/00-TEMPROOT_NOT_VERSIONED/RenderDocumentation/2017-11-15_15-01-29_607017/TheProjectBuild/OpenOffice2Rest/manual-005.t3flt.rst"
        },
    }
}


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append("CHECK PARAMS")
    masterdoc_manual_html_005_as_rst = lookup(
        milestones, "masterdoc_manual_html_005_as_rst"
    )
    oo_parser = lookup(milestones, "oo_parser", default="dl")
    TheProject = lookup(milestones, "TheProject")
    TheProjectBuildOpenOffice2Rest = lookup(
        milestones, "TheProjectBuildOpenOffice2Rest"
    )
    if not (
        masterdoc_manual_html_005_as_rst
        and oo_parser
        and TheProject
        and TheProjectBuildOpenOffice2Rest
    ):
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
    if masterdoc_manual_rst_selected is None:
        masterdoc_manual_rst_selected = lookup(
            masterdoc_manual_html_005_as_rst, oo_parser, "outfile", default=None
        )
    if not masterdoc_manual_rst_selected:
        exitcode = 22
        reason = "Masterdoc not found"


if exitcode == CONTINUE:
    TheProjectDocumentation = os.path.join(TheProject, "Documentation")
    if os.path.exists(TheProjectDocumentation):
        TheProjectDocumentationSaved = os.path.join(TheProject, "Documentation-Saved")
        shutil.move(TheProjectDocumentation, TheProjectDocumentationSaved)

    src = os.path.join(
        params["toolfolderabspath"], "Documentation_default_files", "Documentation"
    )
    shutil.copytree(src, TheProjectDocumentation)

    TheProjectDocumentationManualFolder = os.path.join(
        TheProjectDocumentation, "Manual"
    )
    TheProjectDocumentationManualFile = os.path.join(
        TheProjectDocumentation, "Manual", "Index.rst"
    )

    shutil.copyfile(masterdoc_manual_rst_selected, TheProjectDocumentationManualFile)

    for fname in os.listdir(TheProjectBuildOpenOffice2Rest):
        if os.path.splitext(fname)[1].lower() in [".gif", ".png", ".jpg", ".jpeg"]:
            src = os.path.join(TheProjectBuildOpenOffice2Rest, fname)
            dest = os.path.join(TheProjectDocumentationManualFolder, fname)
            shutil.copyfile(src, dest)

# ==================================================
# Set MILESTONES
# --------------------------------------------------

if TheProjectDocumentation:
    result["MILESTONES"].append({"TheProjectDocumentation": TheProjectDocumentation})

if TheProjectDocumentationManualFile:
    result["MILESTONES"].append(
        {"TheProjectDocumentationManualFile": TheProjectDocumentationManualFile}
    )

if TheProjectDocumentationSaved:
    result["MILESTONES"].append(
        {"TheProjectDocumentationSaved": TheProjectDocumentationSaved}
    )

if masterdoc_manual_rst_selected:
    result["MILESTONES"].append(
        {"masterdoc_manual_rst_selected": masterdoc_manual_rst_selected}
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
