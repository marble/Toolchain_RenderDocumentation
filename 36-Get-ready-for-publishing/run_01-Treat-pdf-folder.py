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

pdf_dest_folder_htaccess = ""
pdf_url_relpath = ""
xeq_name_cnt = 0


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append("CHECK PARAMS")

    # required milestones
    requirements = ["configset"]

    # just test
    for requirement in requirements:
        v = milestones_get(requirement)
        if not v:
            loglist.append("'%s' not found" % requirement)
            exitcode = 22
            reason = "Bad PARAMS or nothing to do"

if exitcode == CONTINUE:
    configset = milestones_get("configset")
    # fetch
    webroot_abspath = tct.deepget(facts, "tctconfig", configset, "webroot_abspath")
    loglist.append(("webroot_abspath", webroot_abspath))

    if not webroot_abspath:
        exitcode = 22
        reason = "Bad PARAMS or nothing to do"

if exitcode == CONTINUE:
    loglist.append("PARAMS are ok")
else:
    loglist.append("Bad PARAMS or nothing to do")


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    pdf_dest_file = milestones_get("pdf_dest_file")
    pdf_dest_folder = milestones_get("pdf_dest_folder")
    publish_dir_pdf_planned = milestones_get("publish_dir_pdf_planned")

    if not (pdf_dest_file and pdf_dest_folder and publish_dir_pdf_planned):
        CONTINUE = -2
        reason = "Nothing to do"
        loglist.append(reason)


if exitcode == CONTINUE:
    temp = os.path.join(publish_dir_pdf_planned, os.path.split(pdf_dest_file)[1])
    pdf_url_relpath = temp[len(webroot_abspath) :]
    loglist.append(("pdf_url_relpath", pdf_url_relpath))

    htaccess_contents = (
        "RewriteEngine On\n"
        "RewriteCond %{REQUEST_FILENAME} !-f\n"
        "RewriteRule ^(.*)$ " + pdf_url_relpath + " [L,R=301]\n"
    )

    pdf_dest_folder_htaccess = os.path.join(pdf_dest_folder, ".htaccess")

    with open(pdf_dest_folder_htaccess, "w") as f2:
        f2.write(htaccess_contents)


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if pdf_url_relpath:
    result["MILESTONES"].append({"pdf_dest_folder_htaccess": pdf_dest_folder_htaccess})

if pdf_url_relpath:
    result["MILESTONES"].append({"pdf_url_relpath": pdf_url_relpath})


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
