#!/usr/bin/env python
# coding: utf-8

from __future__ import absolute_import, print_function

import codecs
import os
import re

import sys
import tct
from six.moves import range
from tctlib import execute_cmdlist

execute_cmdlist

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
toolchain_name = facts["toolchain_name"]
workdir = params["workdir"]
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

TheProjectLogHtmlmail = ""
TheProjectLogHtmlmailMessageMdTxt = ""
TheProjectLogHtmlmailMessageRstTxt = ""
TheProjectLogHtmlmailMessageTxt = ""
xeq_name_cnt = 0


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append("CHECK PARAMS")

    # fetch
    TheProjectLogHtmlmail = milestones_get("TheProjectLogHtmlmail")
    TheProjectResultBuildinfoMessage = milestones_get(
        "TheProjectResultBuildinfoMessage"
    )
    TheProjectLogHtmlmailMessageHtml = milestones_get(
        "TheProjectLogHtmlmailMessageHtml"
    )

    # test
    if not (
        TheProjectLogHtmlmail
        and TheProjectResultBuildinfoMessage
        and TheProjectLogHtmlmailMessageHtml
    ):
        exitcode = 22
        reason = "Bad params or nothing to do"

if exitcode == CONTINUE:
    loglist.append("PARAMS are ok")
else:
    loglist.append("Bad PARAMS or nothing to do")


# ==================================================
# work
# --------------------------------------------------

pattern_re = re.compile('\{.*?"\}')


def fix_pandoc_output(fileabspath):
    lines = open(fileabspath, "r").readlines()
    for i in range(len(lines)):
        lines[i] = pattern_re.sub(u"", lines[i])
    with open(fileabspath, "w") as f2:
        f2.writelines(lines)


if exitcode == CONTINUE:
    TheProjectResultBuildinfoMessageFstem = os.path.split(
        TheProjectResultBuildinfoMessage
    )[1]

    logDestfileMdTxt = (
        TheProjectLogHtmlmail + "/" + TheProjectResultBuildinfoMessageFstem + ".md.txt"
    )
    logDestfileRstTxt = (
        TheProjectLogHtmlmail + "/" + TheProjectResultBuildinfoMessageFstem + ".rst.txt"
    )
    logDestfileTxt = (
        TheProjectLogHtmlmail + "/" + TheProjectResultBuildinfoMessageFstem + ".txt"
    )


if exitcode == CONTINUE:
    if os.path.exists(logDestfileMdTxt):
        os.remove(logDestfileRstTxt)
    cmdlist = [
        "pandoc",
        "--from html",
        "--to   rst",
        "--output " + logDestfileRstTxt,
        TheProjectLogHtmlmailMessageHtml,
    ]
    exitcode, cmd, out, err = execute_cmdlist(cmdlist, cwd=workdir, ns=XeqParams)

    if os.path.exists(logDestfileRstTxt):
        TheProjectLogHtmlmailMessageRstTxt = logDestfileRstTxt


if exitcode == CONTINUE:
    if os.path.exists(logDestfileMdTxt):
        os.remove(logDestfileMdTxt)
    cmdlist = [
        "pandoc",
        "--from html",
        "--to   markdown",
        "--output " + logDestfileMdTxt,
        TheProjectLogHtmlmailMessageHtml,
    ]
    exitcode, cmd, out, err = execute_cmdlist(cmdlist, cwd=workdir, ns=XeqParams)

    if os.path.exists(logDestfileMdTxt):
        fix_pandoc_output(logDestfileMdTxt)
        TheProjectLogHtmlmailMessageMdTxt = logDestfileMdTxt

if exitcode == CONTINUE:
    if os.path.exists(logDestfileTxt):
        os.remove(logDestfileTxt)
    cmdlist = [
        "pandoc",
        "--from html",
        "--to   plain",
        "--output " + logDestfileTxt,
        TheProjectLogHtmlmailMessageHtml,
    ]
    exitcode, cmd, out, err = execute_cmdlist(cmdlist, cwd=workdir, ns=XeqParams)


    if os.path.exists(logDestfileTxt):
        fix_pandoc_output(logDestfileTxt)
        TheProjectLogHtmlmailMessageTxt = logDestfileTxt

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if TheProjectLogHtmlmailMessageMdTxt:
    result["MILESTONES"].append(
        {"TheProjectLogHtmlmailMessageMdTxt": TheProjectLogHtmlmailMessageMdTxt}
    )

if TheProjectLogHtmlmailMessageRstTxt:
    result["MILESTONES"].append(
        {"TheProjectLogHtmlmailMessageRstTxt": TheProjectLogHtmlmailMessageRstTxt}
    )

if TheProjectLogHtmlmailMessageTxt:
    result["MILESTONES"].append(
        {"TheProjectLogHtmlmailMessageTxt": TheProjectLogHtmlmailMessageTxt}
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
