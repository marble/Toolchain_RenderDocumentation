#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function
from __future__ import absolute_import

import os
import tct
import sys

from tct import deepget, logstamp_finegrained

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

import time

# This is the time that we really finish
time_finished_at_2_unixtime = time.time()
time_finished_at_2 = logstamp_finegrained(
    unixtime=time_finished_at_2_unixtime, fmt="%Y-%m-%d %H:%M:%S %f"
)

age_message = ""
xeq_name_cnt = 0


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append("CHECK PARAMS")

    checksum_ttl_seconds = lookup(milestones, "checksum_ttl_seconds", default=1)
    if not checksum_ttl_seconds:
        exitcode = 22
        reason = "Bad PARAMS or nothing to do"

if exitcode == CONTINUE:
    loglist.append("PARAMS are ok")
else:
    loglist.append("Bad PARAMS or nothing to do")


# ==================================================
# work
# --------------------------------------------------

achieved = milestones.get("assembled", [])[:]
checksum_time = milestones.get("checksum_time", 0)
masterdoc = milestones.get("masterdoc")
masterdoc_candidates = milestones.get("masterdoc_candidates", [])
masterdoc_selected = milestones.get("masterdoc_selected")
rebuild_needed = milestones.get("rebuild_needed")
talk = milestones.get("talk", 1)
time_started_at = milestones.get("time_started_at", "")
time_started_at_unixtime = milestones.get("time_started_at_unixtime", 0)

if milestones.get("package_file"):
    achieved.append("package")
if milestones.get("publish_dir_buildinfo"):
    achieved.append("buildinfo")
achieved.sort()
cmdline_reportlines = milestones.get("cmdline_reportlines", [])


if talk:
    indent = "   "
    print()
    print(
        lookup(milestones, "buildsettings", "project", default="PROJECT"),
        lookup(milestones, "buildsettings", "version", default="VERSION"),
        os.path.split(milestones.get("makedir", "MAKEDIR"))[1],
        sep=" : ",
        end="\n",
    )
    print(indent, "makedir ", milestones.get("makedir", "MAKEDIR"), sep="", end="\n")
    print(
        indent,
        time_started_at,
        ",  took: ",
        "%4.2f seconds" % (time_finished_at_2_unixtime - time_started_at_unixtime),
        ",  toolchain: ",
        toolchain_name,
        sep="",
    )

    age_seconds = time_finished_at_2_unixtime - checksum_time
    age_message = "age %3.1f of %3.1f hours" % (
        age_seconds / 3600.0,
        checksum_ttl_seconds / 3600.0,
    )
    age_message += ",  %3.1f of %3.1f days" % (
        age_seconds / 3600.0 / 24.0,
        checksum_ttl_seconds / 3600.0 / 24.0,
    )

    if rebuild_needed:
        cause = "because of "
        if milestones.get("rebuild_needed_because_of_change"):
            cause += "change"
        elif milestones.get("rebuild_needed_because_of_age"):
            cause += "age"
        elif milestones.get("rebuild_needed_run_command"):
            cause += "parameter"
        elif milestones.get("rebuild_needed_tctconfig"):
            cause += "config"
        else:
            cause += "???"
        print(indent, "REBUILD_NEEDED ", cause, ",  ", age_message, sep="")
        print(indent, "OK: ", ", ".join(achieved), sep="")
    else:
        print(indent, "still ok, ", age_message, sep="")

    print()

    if cmdline_reportlines:
        for line in cmdline_reportlines:
            print(indent, line, sep="")
        print()

if talk > 1:

    if exitcode == CONTINUE:

        if talk > 1:
            if achieved:
                s = ", ".join(sorted(achieved))
            else:
                s = "nothing"
            print("Produced: %s" % s)

    if exitcode == CONTINUE:
        if talk > 1:
            duration = ""
            if time_started_at_unixtime and time_finished_at_2_unixtime:
                duration = "duration: %4.2f seconds" % (
                    time_finished_at_2_unixtime - time_started_at_unixtime
                )
            print(time_finished_at_2, duration)

if 1:
    if not masterdoc:
        print(
            "ATTENTION:\n"
            "\n"
            "   No documentation found! No documentation rendered!\n"
            "\n"
            "   Reason: None of the possible starting files (called \n"
            '   "masterdoc") could not be found. Please provide at\n'
            "   least one of the following. They will be taken into\n"
            "   account in this order of preference:\n"
        )
        for i, masterdoc_name in enumerate(masterdoc_candidates):
            print("      %s. %s" % (i + 1, masterdoc_name))

        print(
            "\n"
            "   Find more information at "
            "https://docs.typo3.org/typo3cms/HowToDocument/\n"
        )


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if time_finished_at_2:
    result["MILESTONES"].append({"time_finished_at_2": time_finished_at_2})

if time_finished_at_2_unixtime:
    result["MILESTONES"].append(
        {"time_finished_at_2_unixtime": time_finished_at_2_unixtime}
    )

if "html" in milestones.get("builds_successful", []):
    # 0 means: Toolchain did finish and 'html' was build
    result["MILESTONES"].append({"FINAL_EXITCODE": 0})
    print(
        "   ------------------------------------------------\n"
        "   FINAL STATUS is: SUCCESS (exitcode 0)\n"
        "                    because HTML builder succeeded"
    )
else:
    print(
        "   ------------------------------------------------\n"
        "   FINAL STATUS is: FAILURE (exitcode 255)\n"
        "                    because HTML builder failed"
    )

if not milestones.get("disable_include_files_check") and not milestones.get(
    "included_files_check_is_ok"
):
    print(
        "   ------------------------------------------------\n"
        "   An attempt was made to include a file external to the project.\n"
        "   This prevents any build."
    )

print("   ------------------------------------------------")

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
