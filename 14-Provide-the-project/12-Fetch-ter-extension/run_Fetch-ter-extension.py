#!/usr/bin/env python

from __future__ import print_function
from __future__ import absolute_import
import tct
import sys

#
import codecs
import os
import re
import shutil
import subprocess
from tctlib import execute_cmdlist

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
    result = tct.deepget(D, *keys, **kwdargs)
    loglist.append((keys, result))
    return result


# ==================================================
# define
# --------------------------------------------------

buildsettings_builddir_new = None
buildsettings_changed = False
extension_file = ""
extension_file_abspath = ""
extensions_rootfolder = None
gitbranch = ""
gitdir = ""
gitdir_unpacked = ""
giturl = ""
relative_part_of_builddir_new = None
ter_extkey = ""
ter_extversion = ""


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append("CHECK PARAMS")

    configset = lookup(milestones, "configset")
    buildsettings = lookup(milestones, "buildsettings")
    if not (configset and buildsettings):
        CONTINUE = -2
        reason = "Bad PARAMS or nothing to do"

if exitcode == CONTINUE:
    gitdir_is_ready_for_use = buildsettings.get("gitdir_is_ready_for_use")
    if gitdir_is_ready_for_use:
        CONTINUE = -2
        reason = "Bad PARAMS or nothing to do"

if exitcode == CONTINUE:
    builddir = lookup(milestones, "buildsettings", "builddir", default="")
    buildsettings_builddir = lookup(milestones, "buildsettings_builddir", default="")
    relative_part_of_builddir = lookup(
        milestones, "relative_part_of_builddir", default=""
    )

if exitcode == CONTINUE:
    ter_extkey = buildsettings.get("ter_extkey", "")
    ter_extversion = buildsettings.get("ter_extversion", "")
    if not (ter_extkey and ter_extversion):
        loglist.append("For a TER extension we need the key and the version.")
        CONTINUE = -2
        reason = "Bad PARAMS or nothing to do"

if exitcode == CONTINUE:
    extensions_rootfolder = lookup(
        facts, "tctconfig", configset, "extensions_rootfolder"
    )
    if not extensions_rootfolder:
        loglist.append("We need a place to unpack to")
        exitcode = 22
        reason = "Bad PARAMS or nothing to do"

if exitcode == CONTINUE:
    gitbranch = buildsettings.get("gitbranch", "")
    giturl = buildsettings.get("giturl", "")
    if giturl:
        loglist.append("We can't have both: TER_EXTKEY and GITURL")
        exitcode = 22
        reason = "Bad PARAMS or nothing to do"

#   gitdir = lookup(milestones, 'buildsettings', 'gitdir')


if exitcode == CONTINUE:
    loglist.append("PARAMS are ok")
else:
    loglist.append("Bad PARAMS or nothing to do")


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    foldername = ter_extkey + "_" + ter_extversion
    foldername = foldername.replace("*", "").replace("?", "")
    if not foldername:
        reason = "illegal extension specification"
        loglist.append(reason)
        exitcode = 22

if exitcode == CONTINUE:
    gitdir = os.path.join(extensions_rootfolder, foldername)
    if os.path.exists(gitdir):
        shutil.rmtree(gitdir)
    gitdir_unpacked = os.path.join(gitdir, "unpacked")
    os.makedirs(gitdir_unpacked)

if exitcode == CONTINUE:
    exitcode, cmd, out, err = execute_cmdlist(
        ["t3xutils.phar", "fetch", "--use-curl", ter_extkey, ter_extversion, gitdir],
        ns=XeqParams,
    )

if exitcode == CONTINUE:
    extension_file = ""
    for name in os.listdir(gitdir):
        if name.startswith(ter_extkey):
            extension_file = name
            break

    if extension_file:
        extension_file_abspath = os.path.join(gitdir, extension_file)

    if not extension_file_abspath:
        exitcode = 22
        reason = "Bad extension_file_abspath"


if exitcode == CONTINUE:
    exitcode, cmd, out, err = execute_cmdlist(
        ["t3xutils.phar", "extract", extension_file_abspath, gitdir_unpacked],
        ns=XeqParams,
    )

if exitcode == CONTINUE:
    xx_xx = re.compile("([a-z]{2}-[a-z]{2})|default")
    buildsettings["gitdir"] = gitdir_unpacked
    buildsettings_changed = True

# ==================================================
# Set MILESTONE
# --------------------------------------------------


D = {}

if buildsettings_builddir_new is not None:
    # Change! Overwrite! According to TER extensions
    D["buildsettings_builddir"] = buildsettings_builddir_new

if extension_file:
    D["extension_file"] = extension_file

if extension_file_abspath:
    D["extension_file_abspath"] = extension_file_abspath

if buildsettings_changed:
    # Change! Overwrite! According to TER extensions
    D["buildsettings"] = buildsettings

if relative_part_of_builddir_new:
    # Change! Overwrite! According to TER extensions
    D["relative_part_of_builddir"] = relative_part_of_builddir_new

if D:
    result["MILESTONES"].append(D)


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
