#!/usr/bin/env python

from __future__ import print_function
from __future__ import absolute_import

import codecs
import json
import os
import posixpath
import sys
import tct

from sphinx.util.inventory import InventoryFile

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
    result = tct.deepget(D, *keys, **kwdargs)
    loglist.append((keys, result))
    return result


# ==================================================
# define
# --------------------------------------------------

objects_inv_json_path = None
objects_inv_path = None


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append("CHECK PARAMS")
    reason = "PARAMS are ok"

    build_html = lookup(milestones, "build_html")
    build_html_folder = lookup(milestones, "build_html_folder")

    if not (build_html and build_html_folder):
        exitcode = 22
        reason = "Bad PARAMS or nothing to do"

    loglist.append("PARAMS are ok")


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    f1path = os.path.join(build_html_folder, "objects.inv")
    f2path = os.path.join(build_html_folder, "objects.inv.json")
    if os.path.exists(f1path):
        try:
            with open(f1path, "rb") as f1:
                inventory = InventoryFile.load(f1, "", posixpath.join)
            objects_inv_path = f1path
        except:
            reason = "FAILED: InventoryFile.load()"
            exitcode = 2

if exitcode == CONTINUE:
    try:
        with codecs.open(f2path, "w", "utf-8") as f2:
            json.dump(inventory, f2, sort_keys=True, indent=3)
        objects_inv_json_path = f2path
    except:
        reason = "FAILED: json.dump(inventory)"
        exitcode = 2


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if objects_inv_path:
    result["MILESTONES"].append({"objects_inv_path": objects_inv_path})

if objects_inv_json_path:
    result["MILESTONES"].append({"objects_inv_json_path": objects_inv_json_path})


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
