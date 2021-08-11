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

from os.path import exists as ospe, join as ospj
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

latex_file_tweaked = None
build_latex_file_typo3 = None

# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append("CHECK PARAMS")

    build_latex_file = lookup(milestones, "build_latex_file")
    build_latex_folder = lookup(milestones, "build_latex_folder")

    if not (1 and build_latex_file and build_latex_folder):
        CONTINUE = -2
        reason = "Bad params or nothing to do"

if exitcode == CONTINUE:
    loglist.append("PARAMS are ok")
else:
    loglist.append("Bad PARAMS or nothing to do")


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:

    build_latex_file_typo3 = build_latex_file[:-3] + "typo3.tex"
    shutil.copy2(build_latex_file, build_latex_file_typo3)

    # a list of pairs for textreplacements to be done in latex
    sed_replacements = [
        (r"%%\usepackage{typo3}", r"\usepackage{typo3}"),
        (
            r"\\sphinxtableofcontents",
            r"\\hypersetup{linkcolor=black}\n\\sphinx"
            r"tableofcontents\n\\hypersetup{linkcol"
            r"or=typo3orange}\n",
        ),
        # ('tableofcontents', 'tableofcontents'),
    ]
    for searchstring, replacement in sed_replacements:
        if exitcode != CONTINUE:
            break
        x = searchstring.replace("\\", "\\\\").replace(r"~", r"\~")
        y = replacement.replace("\\", "\\\\").replace(r"~", r"\~")
        cmdlist = ["sed", "--in-place", "'s~%s~%s~'" % (x, y), build_latex_file_typo3]
        exitcode, cmd, out, err = execute_cmdlist(cmdlist, ns=XeqParams)

if exitcode == CONTINUE:
    latex_file_tweaked = 1

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if latex_file_tweaked:
    result["MILESTONES"].append({"latex_file_tweaked": latex_file_tweaked})

if build_latex_file_typo3:
    result["MILESTONES"].append({"build_latex_file_typo3": build_latex_file_typo3})


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
