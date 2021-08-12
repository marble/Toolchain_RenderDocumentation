#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function
from __future__ import absolute_import

import codecs
import os
import subprocess
import shutil
import sys
import tct

from os.path import join as ospj, exists as ospe

params = tct.readjson(sys.argv[1])
binabspath = sys.argv[2]
facts = tct.readjson(params["factsfile"])
milestones = tct.readjson(params["milestonesfile"])
resultfile = params["resultfile"]
reason = ""
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

pdf_files_from_published_latex = []
publish_dir_pdf = None
make_pdf_script_to_execute = None


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append("CHECK PARAMS")

    make_pdf = lookup(milestones, "make_pdf")
    publish_dir_latex = lookup(milestones, "publish_dir_latex")
    run_latex_make_sh_file = lookup(milestones, "run_latex_make_sh_file")
    try_pdf_build_from_published_latex = lookup(
        milestones, "try_pdf_build_from_published_" "latex"
    )

    if not (
        1
        and make_pdf
        and publish_dir_latex
        and try_pdf_build_from_published_latex
        and run_latex_make_sh_file
    ):
        CONTINUE = -2
        reason = "Bad params"

if exitcode == CONTINUE:
    loglist.append("PARAMS are ok")
else:
    loglist.append("PROBLEM with required params")


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:

    make_pdf_script_to_execute = os.path.join(
        publish_dir_latex, os.path.basename(run_latex_make_sh_file)
    )
    workdir = publish_dir_latex

    exitcode, cmd, out, err = execute_cmdlist(
        [make_pdf_script_to_execute], cwd=workdir, ns=XeqParams
    )

if exitcode == CONTINUE:
    publish_dir_pdf = os.path.normpath(os.path.join(publish_dir_latex, "..", "pdf"))
    if not ospe(publish_dir_pdf):
        os.makedirs(publish_dir_pdf)
    for fname in os.listdir(publish_dir_latex):
        if fname.endswith(".pdf"):
            destfile = os.path.join(publish_dir_pdf, fname)
            shutil.copy2(os.path.join(publish_dir_latex, fname), destfile)
            pdf_files_from_published_latex.append(destfile)

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if make_pdf_script_to_execute:
    result["MILESTONES"].append(
        {"make_pdf_script_to_execute": make_pdf_script_to_execute}
    )
if pdf_files_from_published_latex:
    result["MILESTONES"].append(
        {"pdf_files_from_published_latex": pdf_files_from_published_latex}
    )

if publish_dir_pdf:
    result["MILESTONES"].append({"publish_dir_pdf": publish_dir_pdf})

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
