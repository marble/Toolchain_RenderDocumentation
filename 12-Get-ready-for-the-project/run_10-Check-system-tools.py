#!/usr/bin/env python

from __future__ import absolute_import, print_function

import codecs
import os
import subprocess
import sys

import tct
from tctlib import execute_cmdlist

# Keeplist for PyCharm's `optimize imports`:
codecs, os, subprocess, sys, tct, execute_cmdlist

params = tct.readjson(sys.argv[1])
facts = tct.readjson(params["factsfile"])
milestones = tct.readjson(params["milestonesfile"])
reason = ""
resultfile = params["resultfile"]
result = tct.readjson(resultfile)
toolname = params["toolname"]
toolname_pure = params["toolname_pure"]
toolchain_name = facts["toolchain_name"]
workdir = params["workdir"]
loglist = result["loglist"] = result.get("loglist", [])
exitcode = CONTINUE = 0


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

deepget = tct.deepget


def lookup(D, *keys, **kwdargs):
    result = deepget(D, *keys, **kwdargs)
    loglist.append((keys, result))
    return result


# ==================================================
# define
# --------------------------------------------------

# Should we verify these do exist?

list_for_which = [
    "bzip2",
    "check_include_files.py",
    "dvips",
    "git",
    "git-restore-mtime",
    "git-restore-mtime-modified",
    "gzip",
    "html2text",
    "latex",
    "latexmk",
    "makeindex",
    "pandoc",
    "pdflatex",
    "pip",
    "pipenv" "python",
    "python2",
    "python3",
    "soffice",
    "sphinx-build",
    "t3xutils.phar",
    "tidy",
    "zip",
]

known_systemtools = {}
known_versions = {}
pip_freeze = None

# ==================================================
# prepare for shell calls
# --------------------------------------------------

if exitcode == CONTINUE:
    for k in list_for_which:
        cmdlist = ["which", k]
        xcode, cmd, out, err = execute_cmdlist(cmdlist, cwd=workdir, ns=XeqParams)
        if xcode == 0:
            known_systemtools[k] = out.strip()
        else:
            known_systemtools[k] = ""

if exitcode == CONTINUE:
    if "pip" in known_systemtools:
        cmdlist = ["which freeze"]
        xcode, cmd, out, err = execute_cmdlist(cmdlist, cwd=workdir, ns=XeqParams)
        if xcode == 0:
            pip_freeze = v.split("\n")

if exitcode == CONTINUE:
    imported = False
    try:
        import t3SphinxThemeRtd

        imported = True
    except ImportError:
        pass
    if imported:
        # t3SphinxThemeRtd.VERSION # (3, 6, 14)
        # t3SphinxThemeRtd.__version__ # 3.6.14
        known_versions["t3SphinxThemeRtd.VERSION"] = t3SphinxThemeRtd.VERSION
        known_versions["t3SphinxThemeRtd.__version__"] = t3SphinxThemeRtd.__version__

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if known_systemtools:
    result["MILESTONES"].append({"known_systemtools": known_systemtools})

if known_versions:
    result["MILESTONES"].append({"known_versions": known_versions})

if pip_freeze is not None:
    result["MILESTONES"].append({"pip_freeze": pip_freeze})

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
