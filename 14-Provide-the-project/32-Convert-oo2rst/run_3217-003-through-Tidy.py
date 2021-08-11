#!/usr/bin/env python

from __future__ import print_function
from __future__ import absolute_import

import codecs
import os
import os
import PIL
import subprocess
import sys
import tct

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
    result = tct.deepget(D, *keys, **kwdargs)
    loglist.append((keys, result))
    return result


# ==================================================
# define
# --------------------------------------------------

masterdoc_manual_html_003_from_tidy = None
masterdoc_manual_html_003_from_tidy_error_log = None


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append("CHECK PARAMS")

    tidy = (lookup(milestones, "known_systemtools", "tidy") or "").strip()
    masterdoc_manual_html_copy_cleaned = lookup(
        milestones, "masterdoc_manual_html_copy_cleaned"
    )
    TheProjectBuildOpenOffice2Rest = lookup(
        milestones, "TheProjectBuildOpenOffice2Rest"
    )

    if not (
        masterdoc_manual_html_copy_cleaned and TheProjectBuildOpenOffice2Rest and tidy
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
    masterdoc_manual_html_003_from_tidy = os.path.join(
        TheProjectBuildOpenOffice2Rest, "manual-003-from-tidy.html"
    )
    masterdoc_manual_html_003_from_tidy_error_log = os.path.join(
        TheProjectBuildOpenOffice2Rest, "manual-003-from-tidy-error-log.txt"
    )

    exitcode_, cmd, out, err = execute_cmdlist(
        [
            tidy,
            "-asxhtml",
            "-utf8",
            "-f",
            masterdoc_manual_html_003_from_tidy_error_log,
            "-o",
            masterdoc_manual_html_003_from_tidy,
            masterdoc_manual_html_copy_cleaned,
        ],
        ns=XeqParams,
    )

# ==================================================
# Set MILESTONES
# --------------------------------------------------

if masterdoc_manual_html_003_from_tidy_error_log:
    result["MILESTONES"].append(
        {
            "masterdoc_manual_html_003_from_tidy_error_log": masterdoc_manual_html_003_from_tidy_error_log
        }
    )

if masterdoc_manual_html_003_from_tidy:
    result["MILESTONES"].append(
        {"masterdoc_manual_html_003_from_tidy": masterdoc_manual_html_003_from_tidy}
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
