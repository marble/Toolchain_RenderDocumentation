#!/usr/bin/env python

from __future__ import print_function
from __future__ import absolute_import

import codecs
import json
import os
import subprocess
import sys
import tct

from os.path import exists as ospe, join as ospj
from tct import deepget, cmdline

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

remove_docutils_conf_done = None
TheProjectMakedir = None
TheProjectMakedirThemes = None
buildsettings_jsonfile_in_makedir = None


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append("CHECK PARAMS")

    buildsettings = lookup(milestones, "buildsettings")
    makedir = lookup(milestones, "makedir")
    TheProject = lookup(milestones, "TheProject")

    if not (1 and buildsettings and makedir and TheProject):
        exitcode = 22
        reason = "Bad PARAMS or nothing to do"

if exitcode == CONTINUE:
    loglist.append("PARAMS are ok")
else:
    loglist.append("Bad PARAMS or nothing to do")

# ==================================================
# define
# --------------------------------------------------

xeq_name_cnt = 0


# ==================================================
# work
# --------------------------------------------------

allow_unsafe = lookup(milestones, "allow_unsafe")
remove_docutils_conf = lookup(milestones, "remove_docutils_conf")

if exitcode == CONTINUE:

    def execute_cmdlist(cmdlist, cwd=None):
        global xeq_name_cnt
        exitcode, out, err = 88, None, None

        cmd = " ".join(cmdlist)
        cmd_multiline = " \\\n   ".join(cmdlist) + "\n"

        xeq_name_cnt += 1
        filename_cmd = "xeq-%s-%d-%s.txt" % (toolname_pure, xeq_name_cnt, "cmd")
        filename_err = "xeq-%s-%d-%s.txt" % (toolname_pure, xeq_name_cnt, "err")
        filename_out = "xeq-%s-%d-%s.txt" % (toolname_pure, xeq_name_cnt, "out")

        with codecs.open(ospj(workdir, filename_cmd), "w", "utf-8") as f2:
            f2.write(cmd_multiline)

        if (
            0
            and milestones.get("activateLocalSphinxDebugging")
            and cmdlist[0] == "sphinx-build"
            and 1
        ):
            from sphinx.cmd.build import main as sphinx_cmd_build_main

            exitcode = sphinx_cmd_build_main(cmdlist[1:])
        else:
            exitcode, cmd, out, err = cmdline(cmd, cwd=cwd)

        loglist.append({"exitcode": exitcode, "cmd": cmd, "out": out, "err": err})

        if out:
            with codecs.open(ospj(workdir, filename_out), "w", "utf-8") as f2:
                f2.write(out.decode("utf-8", "replace"))

        if err:
            with codecs.open(ospj(workdir, filename_err), "w", "utf-8") as f2:
                f2.write(err.decode("utf-8", "replace"))

        return exitcode, cmd, out, err


# ==================================================
# work
# --------------------------------------------------

themesdir = lookup(milestones, "themesdir")

if exitcode == CONTINUE:
    TheProjectMakedir = TheProject + "Makedir"
    cmdlist = [
        # run rsync
        "rsync",
        # in archive mode, that is equivalent to -rlptgoD
        "-a",
        # but we want to resolve symlinks
        # -L, --copy-links When symlinks are encountered, the item that they
        # point to (the referent) is copied, rather than the symlink.
        "-L",
        # Exclude SYMLINK_THE_PROJECT and similar that may exist
        "--exclude",
        '"SYMLINK_*"',
        # srcdir - slash at the end!
        makedir.rstrip("/") + "/",
        # destdir - slash at the end!
        TheProjectMakedir + "/",
    ]

    exitcode, cmd, out, err = execute_cmdlist(cmdlist, cwd=workdir)


if exitcode == CONTINUE:

    if not themesdir:
        reason = "No themes to copy, because 'themesdir' is not given"
        loglist.append(reason)
        CONTINUE = -2
    if exitcode == CONTINUE:
        if not ospe(themesdir):
            reason = "themesdir '" + themesdir + "' does not exist."
            loglist.append(reason)
            CONTINUE = -2

    if exitcode == CONTINUE:
        destthemes = TheProjectMakedir + "/_themes"
        if ospe(destthemes):
            reason = (
                "We don't want to overwrite the existing "
                '"TheProjectMakedir/_themes" folder'
            )
            loglist.append(reason)
            CONTINUE = -2

    if exitcode == CONTINUE:
        cmdlist = [
            # run rsync
            "rsync",
            # in archive mode, that is equivalent to -rlptgoD
            "-a",
            # leave out symlinks
            "--no-links",
            # srcdir - slash at the end!
            themesdir.rstrip("/") + "/",
            # destdir - slash at the end!
            destthemes.rstrip("/") + "/",
        ]

        exitcode, cmd, out, err = execute_cmdlist(cmdlist, cwd=workdir)

    if exitcode == CONTINUE:
        TheProjectMakedirThemes = destthemes

if exitcode == CONTINUE:
    if remove_docutils_conf or allow_unsafe:
        docutils_conf_file = ospj(TheProjectMakedir, "docutils.conf")
        if ospe(docutils_conf_file):
            os.remove(docutils_conf_file)
            remove_docutils_conf_done = 1

if exitcode == CONTINUE:
    buildsettings_jsonfile_in_makedir = ospj(TheProjectMakedir, "buildsettings.json")
    with codecs.open(buildsettings_jsonfile_in_makedir, "w", "utf-8") as f2:
        json.dump(buildsettings, f2, indent=4, sort_keys=True)


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if TheProjectMakedir:
    result["MILESTONES"].append({"TheProjectMakedir": TheProjectMakedir})

if TheProjectMakedirThemes:
    result["MILESTONES"].append({"TheProjectMakedirThemes": TheProjectMakedirThemes})

if remove_docutils_conf_done:
    result["MILESTONES"].append(
        {"remove_docutils_conf_done": remove_docutils_conf_done}
    )

if buildsettings_jsonfile_in_makedir:
    result["MILESTONES"].append(
        {"buildsettings_jsonfile_in_makedir": buildsettings_jsonfile_in_makedir}
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
