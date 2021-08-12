#!/usr/bin/env python

from __future__ import print_function
from __future__ import absolute_import

import os
import shutil
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
    loglist = loglist
    toolname_pure = toolname_pure
    workdir = workdir
    xeq_name_cnt = 0


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

masterdoc_manual_openoffice = None
masterdoc_manual_000_html = None
TheProjectBuildOpenOffice2Rest = None


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append("CHECK PARAMS")

    TheProject = lookup(milestones, "TheProject")
    TheProjectBuild = lookup(milestones, "TheProjectBuild")
    soffice = (lookup(milestones, "known_systemtools", "soffice") or "").strip()
    tidy = (lookup(milestones, "known_systemtools", "tidy") or "").strip()

    if not (TheProject and TheProjectBuild and soffice and tidy):
        CONTINUE = -1

if exitcode == CONTINUE:
    loglist.append("PARAMS are ok")
else:
    loglist.append("Bad PARAMS or nothing to do")

# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    if not os.path.exists(os.path.join(TheProject, "doc", "manual.sxw")):
        reason = "./doc/manual.sxw does not exist"
        loglist.append(reason)
        CONTINUE = -2

if exitcode == CONTINUE:
    for candidate in [
        "README.rst",
        "README.md",
        "Documentation/Index.rst",
        "Documentation/index.rst",
        "Documentation/Index.md",
        "Documentation/index.md",
    ]:
        if os.path.exists(os.path.join(TheProject, candidate)):
            reason = candidate + " exists"
            loglist.append(reason)
            CONTINUE = -2
            break

if exitcode == CONTINUE:
    masterdoc_manual_openoffice = os.path.join(TheProject, "doc", "manual.sxw")
    TheProjectBuildOpenOffice2Rest = os.path.join(TheProjectBuild, "OpenOffice2Rest")
    if not os.path.exists(TheProjectBuildOpenOffice2Rest):
        os.mkdir(TheProjectBuildOpenOffice2Rest)

    exitcode_, cmd, out, err = execute_cmdlist(
        [
            soffice.strip(),
            "--headless",
            "--convert-to",
            "html",
            "--outdir",
            TheProjectBuildOpenOffice2Rest,
            # provide configdir, otherwise soffice will not run with user permissions
            "-env:UserInstallation=file:///tmp/soffice_config",
            masterdoc_manual_openoffice,
        ],
        ns=XeqParams,
    )

if exitcode == CONTINUE:
    src = os.path.join(TheProjectBuildOpenOffice2Rest, "manual.html")
    masterdoc_manual_000_html = os.path.join(
        TheProjectBuildOpenOffice2Rest, "manual-000-from-openoffice.html"
    )
    shutil.move(src, masterdoc_manual_000_html)


# ==================================================
# Set MILESTONES
# --------------------------------------------------

if TheProjectBuildOpenOffice2Rest:
    result["MILESTONES"].append(
        {"TheProjectBuildOpenOffice2Rest": TheProjectBuildOpenOffice2Rest}
    )

if masterdoc_manual_000_html:
    result["MILESTONES"].append(
        {"masterdoc_manual_000_html": masterdoc_manual_000_html}
    )

if masterdoc_manual_openoffice:
    result["MILESTONES"].append(
        {"masterdoc_manual_openoffice": masterdoc_manual_openoffice}
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
