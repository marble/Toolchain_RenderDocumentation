#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function
from __future__ import absolute_import
import os
import tct
import sys

params = tct.readjson(sys.argv[1])
binabspath = sys.argv[2]
facts = tct.readjson(params["factsfile"])
milestones = tct.readjson(params["milestonesfile"])
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
# Get and check required milestone(s)
# --------------------------------------------------


def milestones_get(name, default=None):
    result = milestones.get(name, default)
    loglist.append((name, result))
    return result


def facts_get(name, default=None):
    result = facts.get(name, default)
    loglist.append((name, result))
    return result


def params_get(name, default=None):
    result = params.get(name, default)
    loglist.append((name, result))
    return result


# ==================================================
# define
# --------------------------------------------------


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append("CHECK PARAMS")

    latex_file = milestones_get("latex_file")

    if not (latex_file):
        exitcode = 22

if exitcode == CONTINUE:
    loglist.append("PARAMS are ok")
else:
    loglist.append("PROBLEMS with params")

if CONTINUE != 0:
    loglist.append({"CONTINUE": CONTINUE})
    loglist.append("NOTHING to do")


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:

    latex_make_file = os.path.join(os.path.split(latex_file)[0], "Makefile")

    import subprocess

    def cmdline(cmd, cwd=None):
        if cwd is None:
            cwd = os.getcwd()
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=cwd
        )
        out, err = process.communicate()
        exitcode = process.returncode
        return exitcode, cmd, out, err

    destfile = latex_make_file

    # a list of pairs for textreplacements to be done in latex
    #    sed -i"" 's/pdflatex /pdflatex -interaction=nonstopmode -halt-on-error /' $BUILDDIR/latex/Makefile
    # -interaction=STRING     set interaction mode (STRING=batchmode/nonstopmode/scrollmode/errorstopmode)

    sed_replacements = [
        (
            r"PDFLATEX = pdflatex",
            r"PDFLATEX = pdflatex -interaction=nonstopmode -halt-on-error ",
        )
    ]

    for searchstring, replacement in sed_replacements:
        if exitcode != CONTINUE:
            break
        x = searchstring
        x = searchstring.replace(r"~", r"\~")
        y = replacement
        y = replacement.replace(r"~", r"\~")
        cmdlist = ["sed", "--in-place", "'s~%s~%s~'" % (x, y), destfile]
        exitcode, cmd, out, err = cmdline(" ".join(cmdlist))
        loglist.append([exitcode, cmd, out, err])


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if exitcode == CONTINUE:
    builds_successful = milestones.get("builds_successful", [])
    builds_successful.append("latex")
    result["MILESTONES"].append(
        {
            "latex_make_file": latex_make_file,
            "latex_make_file_tweaked": True,
            "builds_successful": builds_successful,
        }
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
