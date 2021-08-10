#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function
from __future__ import absolute_import

import codecs
import os
import subprocess
import sys
import tct

from tct import deepget

from os.path import join as ospj, exists as ospe

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

documentation_folder_for_sphinx = ""
final_outdir = None
xeq_name_cnt = 0


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append("CHECK PARAMS")

    make_singlehtml = lookup(milestones, "make_singlehtml")
    if not make_singlehtml:
        CONTINUE = -2
        reason = "Nothing to do"

if exitcode == CONTINUE:
    disable_include_files_check = lookup(milestones, "disable_include_files_check")
    included_files_check_is_ok = lookup(milestones, "included_files_check_is_ok")
    allow_unsafe = lookup(milestones, "allow_unsafe")
    if not any([disable_include_files_check, included_files_check_is_ok, allow_unsafe]):
        exitcode = 22
        reason = "Bad params or nothing to do"

if exitcode == CONTINUE:
    build_html = lookup(milestones, "build_html")
    ready_for_build = lookup(milestones, "ready_for_build", default=None)
    rebuild_needed = lookup(milestones, "rebuild_needed", default=None)

    if not (1 and build_html and ready_for_build and rebuild_needed):
        exitcode = 22
        reason = "Bad params or nothing to do"

if exitcode == CONTINUE:
    masterdoc = lookup(milestones, "masterdoc", default=None)
    SPHINXBUILD = lookup(milestones, "SPHINXBUILD", default=None)
    SYMLINK_THE_MAKEDIR = lookup(milestones, "SYMLINK_THE_MAKEDIR", default=None)
    SYMLINK_THE_OUTPUT = lookup(milestones, "SYMLINK_THE_OUTPUT", default=None)
    SYMLINK_THE_PROJECT = lookup(milestones, "SYMLINK_THE_PROJECT", default=None)
    TheProject = lookup(milestones, "TheProject", default=None)
    TheProjectBuild = lookup(milestones, "TheProjectBuild", default=None)
    TheProjectLog = lookup(milestones, "TheProjectLog", default=None)
    TheProjectMakedir = lookup(milestones, "TheProjectMakedir", default=None)

    if not (
        1
        and masterdoc
        and SPHINXBUILD
        and SYMLINK_THE_MAKEDIR
        and SYMLINK_THE_OUTPUT
        and SYMLINK_THE_PROJECT
        and TheProject
        and TheProjectBuild
        and TheProjectLog
        and TheProjectMakedir
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

if exitcode == CONTINUE:
    html_doctrees_folder = lookup(milestones, "html_doctrees_folder")

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

        exitcode, cmd, out, err = cmdline(cmd, cwd=cwd)

        loglist.append({"exitcode": exitcode, "cmd": cmd, "out": out, "err": err})

        with codecs.open(ospj(workdir, filename_out), "w", "utf-8") as f2:
            f2.write(out.decode("utf-8", "replace"))

        with codecs.open(ospj(workdir, filename_err), "w", "utf-8") as f2:
            f2.write(err.decode("utf-8", "replace"))

        return exitcode, cmd, out, err


if exitcode == CONTINUE:
    # 1
    builder = "singlehtml"
    confpy_folder = TheProjectMakedir
    documentation_folder_for_sphinx = os.path.split(masterdoc)[0]
    localization_bs = lookup(milestones, "buildsettings", "localization", default="")
    localization_bs_as_path = localization_bs.lower().replace("_", "-")
    t3docdir = lookup(milestones, "buildsettings", "t3docdir", default="")
    TheProjectCacheDir = lookup(milestones, "TheProjectCacheDir", default=None)
    if localization_bs_as_path == "default":
        localization_bs_as_path = ""

if exitcode == CONTINUE:
    outdir = ospj(TheProjectBuild, builder)
    if TheProjectCacheDir:
        outdir_in_cache = ospj(TheProjectCacheDir, builder)
        if localization_bs_as_path:
            outdir_in_cache += "-" + localization_bs_as_path
    else:
        outdir_in_cache = None
    sourcedir = documentation_folder_for_sphinx
    warnings_file_folder = ospj(TheProjectLog, builder)

    # 3
    warnings_file = ospj(warnings_file_folder, "warnings.txt")

    # 4
    for k in [outdir, outdir_in_cache, warnings_file_folder]:
        if k and not os.path.isdir(k):
            os.makedirs(k)


if exitcode == CONTINUE:
    for k in [SYMLINK_THE_MAKEDIR, SYMLINK_THE_OUTPUT, SYMLINK_THE_PROJECT]:
        if os.path.islink(k):
            os.unlink(k)

    os.symlink(TheProjectMakedir, SYMLINK_THE_MAKEDIR)
    loglist.append(
        (
            "os.symlink(TheProjectMakedir, SYMLINK_THE_MAKEDIR)",
            TheProjectMakedir,
            SYMLINK_THE_MAKEDIR,
        )
    )

    # If there is cache build there
    if outdir_in_cache:
        final_outdir = outdir_in_cache
        os.symlink(outdir_in_cache, SYMLINK_THE_OUTPUT)
        loglist.append(
            (
                "os.symlink(outdir_in_cache, SYMLINK_THE_OUTPUT)",
                outdir_in_cache,
                SYMLINK_THE_OUTPUT,
            )
        )

    # Else if there is no cache build in TheProjectBuild
    else:
        final_outdir = outdir
        os.symlink(outdir, SYMLINK_THE_OUTPUT)
        loglist.append(
            ("os.symlink(outdir, SYMLINK_THE_OUTPUT)", outdir, SYMLINK_THE_OUTPUT)
        )

    # os.symlink(sourcedir, SYMLINK_THE_PROJECT)
    # loglist.append(('os.symlink(sourcedir, SYMLINK_THE_PROJECT)', sourcedir,
    #                SYMLINK_THE_PROJECT))

    # todo: do it correctly. This isn't the general form atm. Hack!
    os.symlink(TheProject, SYMLINK_THE_PROJECT)
    loglist.append(
        ("os.symlink(TheProject, SYMLINK_THE_PROJECT)", TheProject, SYMLINK_THE_PROJECT)
    )

if exitcode == CONTINUE:
    if html_doctrees_folder and final_outdir:
        cmdlist = ["rsync", "-av", "--delete", html_doctrees_folder, final_outdir]
        exitcode, cmd, out, err = execute_cmdlist(cmdlist, cwd=workdir)

if exitcode == CONTINUE:
    if 1:
        cmdlist = [
            "sphinx-build",
        ]
    if milestones.get("activateLocalSphinxDebugging"):
        cmdlist.extend(["-v", "-v", "-v"])
    else:
        cmdlist.extend(["-v"])
    if 0:
        cmdlist.extend(
            [
                "-a",  # write all files; default is to only write new and changed files
            ]
        )
    if 0:
        cmdlist.extend(
            [
                "-E",  # don't use a saved environment, always read all files
            ]
        )
    if 1:
        if t3docdir:
            t3docdir_relpath = "/" + t3docdir
        else:
            t3docdir_relpath = ""
        cmdlist.extend(
            [
                "-b",
                builder,  # builder to use; default is html
                "-c",
                SYMLINK_THE_MAKEDIR,  # path where configuration file(conf.py) is located (default: same as sourcedir)
                # '-d ', doctree_folder,     # path for the cached environment and doctree files (default: outdir /.doctrees)
                "-n",  # nit-picky mode, warn about all missing references
                "-N",  # do not emit colored output
                "-T",  # show full traceback on exception
                "-w",
                warnings_file,  # write warnings (and errors) to given file
                SYMLINK_THE_PROJECT
                + t3docdir_relpath,  # need a stable name for Sphinx caching
                SYMLINK_THE_OUTPUT,  # # need a stable name for Sphinx caching
            ]
        )

    exitcode, cmd, out, err = execute_cmdlist(cmdlist, cwd=workdir)

if exitcode == CONTINUE:
    for k in [SYMLINK_THE_MAKEDIR, SYMLINK_THE_OUTPUT, SYMLINK_THE_PROJECT]:
        if os.path.islink(k):
            os.unlink(k)


if exitcode == CONTINUE:
    if outdir_in_cache:
        # copy from TheProjectCache to TheProjectBuild
        # TheProjectCache is "outside" in the user's space
        # TheProjectBuild is internal
        cmdlist = [
            "rsync",
            "-a",
            "--delete",
            '"%s/"' % outdir_in_cache,
            '"%s/"' % outdir,
        ]
        exitcode, cmd, out, err = execute_cmdlist(cmdlist, cwd=workdir)


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if exitcode == CONTINUE:
    builds_successful = milestones.get("builds_successful", [])
    builds_successful.append("singlehtml")
    result["MILESTONES"].append(
        {
            "build_singlehtml": "success",
            "builds_successful": builds_successful,
            "build_" + builder + "_folder": outdir,
        }
    )

if documentation_folder_for_sphinx:
    result["MILESTONES"].append(
        {"documentation_folder_for_sphinx": documentation_folder_for_sphinx}
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
