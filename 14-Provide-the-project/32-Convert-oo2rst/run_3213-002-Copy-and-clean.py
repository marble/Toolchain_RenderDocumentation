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

masterdoc_manual_html_copy_cleaned = None
xeq_name_cnt = 0


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append("CHECK PARAMS")

    masterdoc_manual_html_gifs_fixed = lookup(
        milestones, "masterdoc_manual_html_gifs_fixed"
    )
    TheProjectBuildOpenOffice2Rest = lookup(
        milestones, "TheProjectBuildOpenOffice2Rest"
    )
    if not (masterdoc_manual_html_gifs_fixed and TheProjectBuildOpenOffice2Rest):
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
    masterdoc_manual_html_copy_cleaned = os.path.join(
        TheProjectBuildOpenOffice2Rest, "manual-002-copy-cleaned.html"
    )

    with open(masterdoc_manual_html_gifs_fixed, "rb") as f1:
        data = f1.read()

    positions = []
    for pattern in ["<SDFIELD", "</SDFIELD", "<sdfield", "</sdfield"]:
        p1 = data.find(pattern)
        while p1 >= 0:
            p2 = data.find(">", p1 + 1)
            if p2 >= 0:
                positions.append((p1, (p1, p2)))
            p1 = data.find(pattern, p1 + 1)
    positions.sort()

    with open(masterdoc_manual_html_copy_cleaned, "wb") as f2:
        startpos = 0
        lendata = len(data)
        for p in positions:
            p1, p2 = p[1]
            f2.write(data[startpos:p1])
            startpos = p2 + 1
        f2.write(data[startpos:lendata])

# ==================================================
# Set MILESTONES
# --------------------------------------------------

if masterdoc_manual_html_copy_cleaned:
    result["MILESTONES"].append(
        {"masterdoc_manual_html_copy_cleaned": masterdoc_manual_html_copy_cleaned}
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
