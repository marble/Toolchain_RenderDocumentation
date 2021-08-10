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
xeq_name_cnt = 0

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

    def cmdline(cmd, cwd=None):
        if cwd is None:
            cwd = os.getcwd()
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=cwd
        )
        bstdout, bstderr = process.communicate()
        exitcode2 = process.returncode
        return exitcode2, cmd, bstdout, bstderr

    def execute_cmdlist(cmdlist, cwd=None):
        global xeq_name_cnt
        cmd = " ".join(cmdlist)
        cmd_multiline = " \\\n   ".join(cmdlist) + "\n"

        xeq_name_cnt += 1
        filename_cmd = "xeq-%s-%d-%s.txt" % (toolname_pure, xeq_name_cnt, "cmd")
        filename_err = "xeq-%s-%d-%s.txt" % (toolname_pure, xeq_name_cnt, "err")
        filename_out = "xeq-%s-%d-%s.txt" % (toolname_pure, xeq_name_cnt, "out")

        with codecs.open(ospj(workdir, filename_cmd), "w", "utf-8") as f2:
            f2.write(cmd_multiline.decode("utf-8", "replace"))

        if 0 and "activateLocalSphinxDebugging":
            if cmdlist[0] == "sphinx-build":
                from sphinx.cmd.build import main as sphinx_cmd_build_main

                sphinx_cmd_build_main(cmdlist[1:])
                exitcode, cmd, out, err = 99, cmd, b"", b""
        else:
            exitcode, cmd, out, err = cmdline(cmd, cwd=cwd)

        loglist.append({"exitcode": exitcode, "cmd": cmd, "out": out, "err": err})

        with codecs.open(ospj(workdir, filename_out), "w", "utf-8") as f2:
            f2.write(out.decode("utf-8", "replace"))

        with codecs.open(ospj(workdir, filename_err), "w", "utf-8") as f2:
            f2.write(err.decode("utf-8", "replace"))

        return exitcode, cmd, out, err


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
        exitcode, cmd, out, err = execute_cmdlist(cmdlist)

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
