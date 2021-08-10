#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function
from __future__ import absolute_import
import cgi
import codecs
import os
import re
import shutil
import subprocess
import sys
import tct
from six.moves import range

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
    lines = open(fileabspath, "rb").readlines()
    for i in range(len(lines)):
        lines[i] = pattern_re.sub(u"", lines[i])
    with open(fileabspath, "wb") as f2:
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

    def cmdline(cmd, cwd=None):
        if cwd is None:
            cwd = os.getcwd()
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=cwd
        )
        out, err = process.communicate()
        exitcode = process.returncode
        return exitcode, cmd, out, err


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
    cmd = " ".join(cmdlist)
    cmd_multiline = " \\\n   ".join(cmdlist) + "\n"

    exitcode, cmd, out, err = cmdline(cmd, cwd=workdir)

    loglist.append({"exitcode": exitcode, "cmd": cmd, "out": out, "err": err})

    xeq_name_cnt += 1
    filename_cmd = "xeq-%s-%d-%s.txt" % (toolname_pure, xeq_name_cnt, "cmd")
    filename_err = "xeq-%s-%d-%s.txt" % (toolname_pure, xeq_name_cnt, "err")
    filename_out = "xeq-%s-%d-%s.txt" % (toolname_pure, xeq_name_cnt, "out")

    with codecs.open(os.path.join(workdir, filename_cmd), "w", "utf-8") as f2:
        f2.write(cmd_multiline.decode("utf-8", "replace"))

    with codecs.open(os.path.join(workdir, filename_out), "w", "utf-8") as f2:
        f2.write(out.decode("utf-8", "replace"))

    with codecs.open(os.path.join(workdir, filename_err), "w", "utf-8") as f2:
        f2.write(err.decode("utf-8", "replace"))

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
    cmd = " ".join(cmdlist)
    cmd_multiline = " \\\n   ".join(cmdlist) + "\n"

    exitcode, cmd, out, err = cmdline(cmd, cwd=workdir)

    loglist.append({"exitcode": exitcode, "cmd": cmd, "out": out, "err": err})

    xeq_name_cnt += 1
    filename_cmd = "xeq-%s-%d-%s.txt" % (toolname_pure, xeq_name_cnt, "cmd")
    filename_err = "xeq-%s-%d-%s.txt" % (toolname_pure, xeq_name_cnt, "err")
    filename_out = "xeq-%s-%d-%s.txt" % (toolname_pure, xeq_name_cnt, "out")

    with codecs.open(os.path.join(workdir, filename_cmd), "w", "utf-8") as f2:
        f2.write(cmd_multiline.decode("utf-8", "replace"))

    with codecs.open(os.path.join(workdir, filename_out), "w", "utf-8") as f2:
        f2.write(out.decode("utf-8", "replace"))

    with codecs.open(os.path.join(workdir, filename_err), "w", "utf-8") as f2:
        f2.write(err.decode("utf-8", "replace"))

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
    cmd = " ".join(cmdlist)
    cmd_multiline = " \\\n   ".join(cmdlist) + "\n"

    exitcode, cmd, out, err = cmdline(cmd, cwd=workdir)

    loglist.append({"exitcode": exitcode, "cmd": cmd, "out": out, "err": err})

    xeq_name_cnt += 1
    filename_cmd = "xeq-%s-%d-%s.txt" % (toolname_pure, xeq_name_cnt, "cmd")
    filename_err = "xeq-%s-%d-%s.txt" % (toolname_pure, xeq_name_cnt, "err")
    filename_out = "xeq-%s-%d-%s.txt" % (toolname_pure, xeq_name_cnt, "out")

    with codecs.open(os.path.join(workdir, filename_cmd), "w", "utf-8") as f2:
        f2.write(cmd_multiline.decode("utf-8", "replace"))

    with codecs.open(os.path.join(workdir, filename_out), "w", "utf-8") as f2:
        f2.write(out.decode("utf-8", "replace"))

    with codecs.open(os.path.join(workdir, filename_err), "w", "utf-8") as f2:
        f2.write(err.decode("utf-8", "replace"))

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
