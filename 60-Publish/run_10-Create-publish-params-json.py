#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function
from __future__ import absolute_import

import os
import sys
import tct

from tct import deepget

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

publish_params_json_file = None
publish_params_data = {}
xeq_name_cnt = 0

# ==================================================
# example - just for demonstration
# --------------------------------------------------

example_list = [
    {
        "publish_dir": "/ALL/dummy_webroot/typo3cms/extensions/blog/blog/8.7.0",
        "publish_dir_buildinfo": "/ALL/dummy_webroot/typo3cms/extensions/blog/blog/8.7.0/_buildinfo",
        "publish_html_done": 1,
        "publish_language_dir": "/ALL/dummy_webroot/typo3cms/extensions/blog",
        "publish_package_file": "/ALL/dummy_webroot/typo3cms/extensions/blog/packages/blog-8.7.0-default.zip",
        "publish_packages_xml_file": "/ALL/dummy_webroot/typo3cms/extensions/blog/packages/packages.xml",
        "publish_project_dir": "/ALL/dummy_webroot/typo3cms/extensions/blog",
        "publish_project_parent_dir": "/ALL/dummy_webroot/typo3cms/extensions",
        "publish_removed_old": 1,
        "webroot_abspath": "/ALL/dummy_webroot",
    },
    {
        "publish_dir": "typo3cms/extensions/sphinx/fr-fr/2.5.1",
        "publish_dir_buildinfo": "typo3cms/extensions/sphinx/fr-fr/2.5.1/_buildinfo",
        "publish_language_dir": "typo3cms/extensions/sphinx",
        "publish_package_file": "typo3cms/extensions/sphinx/packages/sphinx-2.5.1-fr-fr.zip",
        "publish_packages_xml_file": "typo3cms/extensions/sphinx/packages/packages.xml",
        "publish_project_dir": "typo3cms/extensions/sphinx",
        "publish_project_parent_dir": "typo3cms/extensions",
        "todo_update_stable_symlink": 1,
    },
]


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append("CHECK PARAMS")

    publish_html_done = lookup(milestones, "publish_html_done")
    if not publish_html_done:
        exitcode = 22
        reason = "Bad PARAMS or nothing to do"

    publish_dir = lookup(milestones, "publish_dir", default=None)
    publish_language_dir = lookup(milestones, "publish_language_dir", default=None)
    publish_project_dir = lookup(milestones, "publish_project_dir", default=None)
    publish_project_parent_dir = lookup(
        milestones, "publish_project_parent_dir", default=None
    )
    TheProjectWebroot = lookup(milestones, "TheProjectWebroot", default=None)
    # webroot_abspath = lookup(milestones, "webroot_abspath")

    if not (
        1
        and publish_dir
        and publish_language_dir
        and publish_project_dir
        and publish_project_parent_dir
        and TheProjectWebroot
    ):
        exitcode = 22
        reason = "Bad PARAMS or nothing to do"

if exitcode == CONTINUE:
    publish_dir_buildinfo = lookup(milestones, "publish_dir_buildinfo", default="")
    publish_package_file = lookup(milestones, "publish_package_file", default="")
    publish_packages_xml_file = lookup(
        milestones, "publish_packages_xml_file", default=""
    )
    ter_extension = lookup(milestones, "buildsettings", "ter_extension")

if exitcode == CONTINUE:
    loglist.append("PARAMS are ok")
else:
    loglist.append("Bad PARAMS or nothing to do")


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    len_TheProjectWebroot = len(TheProjectWebroot)

    def fixparm(fpath):
        result = fpath
        if fpath.startswith(TheProjectWebroot):
            result = fpath[len_TheProjectWebroot:]
        return result.strip("/")


if exitcode == CONTINUE:
    publish_params_data["publish_dir"] = fixparm(publish_dir)
    publish_params_data["publish_dir_buildinfo"] = fixparm(publish_dir_buildinfo)
    publish_params_data["publish_language_dir"] = fixparm(publish_language_dir)
    publish_params_data["publish_package_file"] = fixparm(publish_package_file)
    publish_params_data["publish_packages_xml_file"] = fixparm(
        publish_packages_xml_file
    )
    publish_params_data["publish_project_dir"] = fixparm(publish_project_dir)
    publish_params_data["publish_project_parent_dir"] = fixparm(
        publish_project_parent_dir
    )
    publish_params_data["todo_update_stable_symlink"] = 1 if ter_extension else 0

    publish_params_json_file = os.path.join(TheProjectWebroot, "publish-params.json")

    if os.path.exists(publish_params_json_file):
        publish_params_existing_data = tct.readjson(publish_params_json_file)
    else:
        publish_params_existing_data = []

    publish_params_existing_data.append(publish_params_data)
    tct.writejson(publish_params_existing_data, publish_params_json_file)


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if publish_params_json_file:
    result["MILESTONES"].append({"publish_params_json_file": publish_params_json_file})

if publish_params_data:
    result["MILESTONES"].append({"publish_params_data": publish_params_data})


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
