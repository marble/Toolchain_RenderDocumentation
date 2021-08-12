#!/usr/bin/env python

from __future__ import print_function
from __future__ import absolute_import
import os
import shutil
import sys
import tct
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
# Helper functions
# --------------------------------------------------


def lookup(D, *keys, **kwdargs):
    result = tct.deepget(D, *keys, **kwdargs)
    loglist.append((keys, result))
    return result


# ==================================================
# define
# --------------------------------------------------

documentation_folder = None
documentation_folder_created = None
documentation_folder_moved = None
masterdoc = None

readme_masterdoc_file = params["toolfolderabspath"] + "/README-masterdoc-Index.rst"

# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append("CHECK PARAMS")

    TheProject = lookup(milestones, "TheProject")
    masterdoc_candidates = lookup(milestones, "masterdoc_candidates")
    if not (TheProject and masterdoc_candidates):
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
    pandoc = lookup(milestones, "known_systemtools", "pandoc")
    buildsettings = lookup(milestones, "buildsettings")
    gitbranch = lookup(milestones, "buildsettings", "gitbranch")
    gitdir = lookup(milestones, "buildsettings", "gitdir")
    giturl = lookup(milestones, "buildsettings", "giturl")
    locale_folders = lookup(milestones, "locale_folders", default={})

if exitcode == CONTINUE:
    workdir_home = lookup(params, "workdir_home")
    masterdocs_initial = lookup(milestones, "masterdocs_initial")
    localization = lookup(milestones, "buildsettings", "localization", default="")
    documentation_folder = lookup(milestones, "documentation_folder")

if exitcode == CONTINUE and pandoc:
    # look for possible markdown masterdocs
    # if found and there's no corresponding rst masterdoc try to convert by pandoc
    for candidate in masterdoc_candidates:
        if not candidate.endswith(".md"):
            continue
        left, right = os.path.split(candidate)
        mdfile = os.path.join(TheProject, left, locale_folders[localization], right)
        if os.path.exists(mdfile):
            rstfile = mdfile[:-3] + ".rst"
            if not os.path.exists(rstfile):
                exitcode_, cmd, out, err = execute_cmdlist(
                    [pandoc, "--from markdown --to rst", mdfile, "-o", rstfile],
                    ns=XeqParams,
                )

if exitcode == CONTINUE:
    for candidate in masterdoc_candidates:
        left, right = os.path.split(candidate)
        fpath = os.path.join(TheProject, left, locale_folders[localization], right)
        loglist.append(("check: Is masterdoc?", fpath))
        if os.path.exists(fpath):
            masterdoc = fpath
            break
    else:
        candidate = None
        masterdoc = None

if (exitcode == CONTINUE) and masterdoc and candidate:

    if candidate.lower().startswith("documentation/index."):
        pass

    elif candidate.lower().startswith("readme."):
        fpath, fext = os.path.splitext(candidate)
        source = masterdoc

        # move that folder to Documentation/Documentation
        # as we move README as well
        if documentation_folder:
            dest = documentation_folder + "-TEMPORARY"
            shutil.move(documentation_folder, dest)
            os.mkdir(documentation_folder)
            documentation_folder_created = documentation_folder
            src = dest
            dest = os.path.join(documentation_folder, "Documentation")
            shutil.move(src, dest)
            documentation_folder_moved = dest
            for fname in os.listdir(dest):
                if fname in ["Settings.cfg", "Settings.yml"]:
                    shutil.copy(os.path.join(dest, fname), documentation_folder)

        if not documentation_folder:
            documentation_folder = os.path.join(TheProject, "Documentation")
            os.mkdir(documentation_folder)
            documentation_folder_created = documentation_folder

        masterdoc = os.path.join(documentation_folder, "Index.rst")
        shutil.copyfile(readme_masterdoc_file, masterdoc)
        shutil.copyfile(source, documentation_folder + "/" + candidate)

    elif masterdoc.lower().startswith("docs/"):
        # not yet implemented
        masterdoc = None


# ==================================================
# Set MILESTONE #1
# --------------------------------------------------

if masterdoc:
    masterdoc_no_ext = os.path.splitext(masterdoc)[0]
    buildsettings["masterdoc"] = masterdoc_no_ext
    result["MILESTONES"].append(
        {
            "masterdoc": masterdoc_no_ext,
            "masterdoc_with_ext": masterdoc,
        }
    )

if documentation_folder_created:
    result["MILESTONES"].append(
        {"documentation_folder_created": documentation_folder_created}
    )

if documentation_folder_moved:
    result["MILESTONES"].append(
        {"documentation_folder_moved": documentation_folder_moved}
    )

if documentation_folder:
    result["MILESTONES"].append({"documentation_folder": documentation_folder})


# ==================================================
# Set MILESTONE #2
# --------------------------------------------------

if buildsettings:
    result["MILESTONES"].append({"buildsettings": buildsettings})

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
