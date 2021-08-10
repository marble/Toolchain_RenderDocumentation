#!/usr/bin/env python

from __future__ import print_function
from __future__ import absolute_import
import os
import tct
import sys

#
import PIL

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

masterdoc_manual_html_gifs_fixed = None
xeq_name_cnt = 0


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append("CHECK PARAMS")

    masterdoc_manual_000_html = lookup(milestones, "masterdoc_manual_000_html")
    TheProjectBuildOpenOffice2Rest = lookup(
        milestones, "TheProjectBuildOpenOffice2Rest"
    )
    if not (masterdoc_manual_000_html and TheProjectBuildOpenOffice2Rest):
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
    masterdoc_manual_html_gifs_fixed = os.path.join(
        TheProjectBuildOpenOffice2Rest, "manual-001-gifs-fixed.html"
    )

    L = []
    for fname in os.listdir(TheProjectBuildOpenOffice2Rest):
        if fname.lower().startswith("manual_html_") and fname.lower().endswith(".gif"):
            L.append(fname)
    if L:
        for fname in L:
            gifFile = os.path.join(TheProjectBuildOpenOffice2Rest, fname)
            im = PIL.Image.open(gifFile)
            pngFile = gifFile + ".png"
            im.save(pngFile)

    with open(masterdoc_manual_000_html, "rb") as f1:
        data = f1.read()

    for fname in L:
        data = data.replace(fname, fname + ".png")

    with open(masterdoc_manual_html_gifs_fixed, "wb") as f2:
        f2.write(data)


# ==================================================
# Set MILESTONES
# --------------------------------------------------

if masterdoc_manual_html_gifs_fixed:
    result["MILESTONES"].append(
        {"masterdoc_manual_html_gifs_fixed": masterdoc_manual_html_gifs_fixed}
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
