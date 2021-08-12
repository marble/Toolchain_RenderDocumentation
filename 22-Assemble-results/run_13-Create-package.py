#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function
from __future__ import absolute_import

import codecs
import os
import re
import shutil
import subprocess
import sys
import tct

ospj = os.path.join
ospe = os.path.exists

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

build_package = None
package_file = None
package_name = None
TheProjectResultCopyForPackage = None

talk = milestones.get("talk", 0)

# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append("CHECK PARAMS")

    make_package = lookup(milestones, "make_package")
    TheProjectResultVersion = lookup(milestones, "TheProjectResultVersion")
    TheProjectResult = lookup(milestones, "TheProjectResult")

    if not (1 and make_package and TheProjectResult and TheProjectResultVersion):
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
    package_folder = "html_result"
    TheProjectResultCopyForPackage = TheProjectResult + "CopyForPackage"
    the_copy = ospj(TheProjectResultCopyForPackage, package_folder)
    if not ospe(the_copy):
        os.makedirs(the_copy)
    cmd = [
        "rsync",
        "-a",
        "--exclude=.doctrees",
        TheProjectResultVersion.rstrip("/") + "/",
        the_copy.rstrip("/") + "/",
    ]
    exitcode, cmd, out, err = execute_cmdlist(cmd, ns=XeqParams)
    if exitcode:
        the_copy = None
        exitcode = 22
        reason = "rsync failed"


if exitcode == CONTINUE:

    html_fonts_folder = ospj(the_copy, "_static", "fonts")
    if ospe(html_fonts_folder):
        # remove some font files
        for f2name in os.listdir(html_fonts_folder):
            if not ("fontawesome" in f2name):
                f2path = ospj(html_fonts_folder, f2name)
                if os.path.isfile(f2path):
                    os.remove(f2path)
                elif os.path.isdir(f2path):
                    shutil.rmtree(f2path, ignore_errors=True)

    singlehtml_fonts_folder = ospj(the_copy, "singlehtml", "_static", "fonts")
    if ospe(singlehtml_fonts_folder):
        # remove some font files
        for f2name in os.listdir(singlehtml_fonts_folder):
            if not ("fontawesome" in f2name):
                f2path = ospj(singlehtml_fonts_folder, f2name)
                if os.path.isfile(f2path):
                    os.remove(f2path)
                elif os.path.isdir(f2path):
                    shutil.rmtree(f2path, ignore_errors=True)

    # use theme without fonts
    html_theme_css = ospj(the_copy, "_static", "css", "theme.css")
    html_theme_no_fonts_css = ospj(the_copy, "_static", "css", "theme-no-fonts.css")
    if ospe(html_theme_css) and ospe(html_theme_no_fonts_css):
        os.remove(html_theme_css)
        os.rename(html_theme_no_fonts_css, html_theme_css)

    # use theme without fonts
    singlehtml_theme_css = ospj(the_copy, "singlehtml", "_static", "css", "theme.css")
    singlehtml_theme_no_fonts_css = ospj(
        the_copy, "singlehtml", "_static", "css", "theme-no-fonts.css"
    )
    if ospe(singlehtml_theme_css) and ospe(singlehtml_theme_no_fonts_css):
        os.remove(singlehtml_theme_css)
        os.rename(singlehtml_theme_no_fonts_css, singlehtml_theme_css)

    # find:  <script type = "text/javascript" id="idPiwikScript" src="/js/piwik.js"></script>
    # <script type="text/javascript" id="idPiwikScriptPlaceholder"></script>
    needle = 'id="idPiwikScript" src="'
    for top, dirs, fnames in os.walk(the_copy):
        for fname in fnames:
            if not fname.endswith(".html"):
                continue
            fpath = ospj(top, fname)
            bytedata = open(fpath, "rb").read()
            bytedata, cnt = re.subn(
                b'<script .+?idPiwikScript".+?<\\/script>',
                b'<script type="text/javascript" id="idPiwikScriptPlaceholder"></script>',
                bytedata,
            )
            if cnt:
                open(fpath, "wb").write(bytedata)
                if talk > 1:
                    print(fpath)

if exitcode == CONTINUE:
    localization_bs_as_path = lookup(milestones, "localization_bs_as_path", default="")
    if localization_bs_as_path:
        package_name = "package-" + localization_bs_as_path + ".zip"
    else:
        package_name = "package.zip"
    package_file = ospj(workdir, package_name)
    cmd = ["zip", "-r", "-9", "-q", package_file, package_folder]
    exitcode, cmd, out, err = execute_cmdlist(
        cmd, cwd=TheProjectResultCopyForPackage, ns=XeqParams
    )
    if exitcode:
        package_name = None
        package_file = None
    else:
        build_package = "success"
        shutil.rmtree(TheProjectResultCopyForPackage, ignore_errors=True)

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if package_name:
    result["MILESTONES"].append({"package_name": package_name})

if package_file:
    result["MILESTONES"].append({"package_file": package_file})

if build_package:
    result["MILESTONES"].append({"build_package": build_package})


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
