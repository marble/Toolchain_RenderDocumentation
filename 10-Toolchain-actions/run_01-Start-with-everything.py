#!/usr/bin/env python

from __future__ import absolute_import, print_function

import codecs
import json
import os
from os.path import join as ospj

import sys
import tct
import time
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
initial_working_dir = facts["initial_working_dir"]


# ==================================================
# Make a copy of milestones for later inspection?
# --------------------------------------------------

if 1:
    tct.make_snapshot_of_milestones(params["milestonesfile"], sys.argv[1])


# ==================================================
# Set pre-initial values (0)
# --------------------------------------------------

jobfile_data = {}
jobfile_json = None
jobfile_json_abspath = None


# ==================================================
# Helper functions (1)
# --------------------------------------------------


def firstNotNone(*args):
    for arg in args:
        if arg is not None:
            return arg
    else:
        return None


def lookup(D, *keys, **kwdargs):
    result = deepget(D, *keys, **kwdargs)
    loglist.append((keys, result))
    return result


# ==================================================
# Process possible jobfile.json
# --------------------------------------------------

jobfile_json = lookup(facts, "run_command", "jobfile", default=None)
if jobfile_json:
    if os.path.isabs(jobfile_json):
        jobfile_json_abspath = jobfile_json
    else:
        jobfile_json_abspath = ospj(initial_working_dir, jobfile_json)

    jobfile_json_abspath = os.path.normpath(jobfile_json_abspath)
    with codecs.open(jobfile_json_abspath, "r", "utf-8") as f1:
        jobfile_data = json.load(f1)

# ==================================================
# Helper functions (2)
# --------------------------------------------------


def findRunParameter(key, default=None, D=None, fconv=None):
    a = deepget(milestones, key, default=None)
    b = deepget(jobfile_data, "tctconfig", key, default=None)
    c = deepget(facts, "run_command", key.lower(), default=None)
    d = deepget(facts, "tctconfig", configset.lower(), key.lower(), default=None)
    e = default
    f = None
    result = firstNotNone(a, b, c, d, e, f)
    # function convert
    if fconv is not None:
        result = fconv(result)
    if type(D) == type({}):
        D[key] = result
    return result


ATNM = all_the_new_milestones = {}


# ==================================================
# Set initial values (1) and store in milestones
# --------------------------------------------------

# configset = deepget(facts, 'run_command', 'configset', default='default')
ATNM["active_section"] = (
    0
    or milestones.get("active_section")
    or deepget(facts, "active_section", default="default")
)

# too bad we used both names:
configset = ATNM["active_section"]
ATNM["configset"] = configset

time_started_at_unixtime = time.time()
ATNM["time_started_at_unixtime"] = time_started_at_unixtime
time_started_at = logstamp_finegrained(
    unixtime=time_started_at_unixtime, fmt="%Y-%m-%d %H:%M:%S %f"
)
ATNM["time_started_at"] = time_started_at


# ==================================================
# Set initial values (2) and store in milestones
# --------------------------------------------------

activateLocalSphinxDebugging = findRunParameter(
    "activateLocalSphinxDebugging", 0, ATNM, int
)
allow_unsafe = findRunParameter("allow_unsafe", 0, ATNM, int)
debug_always_make_milestones_snapshot = findRunParameter(
    "debug_always_make_milestones_snapshot", 1, ATNM, int
)
disable_include_files_check = findRunParameter(
    "disable_include_files_check", 0, ATNM, int
)
force_rebuild_needed = findRunParameter("force_rebuild_needed", 1, ATNM, int)
force_html_postprocessing = findRunParameter("force_html_postprocessing", 0, ATNM, int)
ignore_lockfile = findRunParameter("ignore_lockfile", 0, ATNM, int)
latex_contrib_typo3_folder = findRunParameter("latex_contrib_typo3_folder", None, ATNM)
lockfile_name = findRunParameter("lockfile_name", "lockfile.json", ATNM)
make_html = findRunParameter("make_html", 1, ATNM, int)
make_latex = findRunParameter("make_latex", 1, ATNM, int)
make_pdf = findRunParameter("make_pdf", 1, ATNM, int)
make_singlehtml = findRunParameter("make_singlehtml", 1, ATNM, int)
makedir = findRunParameter("makedir", None, ATNM)
rebuild_needed = findRunParameter("rebuild_needed", 1, ATNM, int)
replace_static_in_html = findRunParameter("replace_static_in_html", 0, ATNM, int)
remove_docutils_conf = findRunParameter("remove_docutils_conf", 0, ATNM, int)
resultdir = findRunParameter("resultdir", None, ATNM)
reveal_exitcodes = findRunParameter("reveal_exitcodes", 1, ATNM, int)
reveal_milestones = findRunParameter("reveal_milestones", 1, ATNM, int)
smtp_host = findRunParameter("smtp_host", None, ATNM)
sphinx_build_options = findRunParameter("sphinx_build_options", (
    " -j auto"  # try to build in parallel
    " -n"       # nit-picky mode, warn about all missing references
    " -N"       # do not emit colored output
    " -T"       # show full traceback on exception
    " -v"       # verbose
).strip(), ATNM)
sphinxVerboseLevel = findRunParameter("sphinxVerboseLevel", 1, ATNM, int)
talk = findRunParameter("talk", 1, ATNM, int)
themesdir = findRunParameter("themesdir", "/THEMES", ATNM)
toolchain_help = findRunParameter("toolchain_help", 0, ATNM, int)
try_pdf_build_from_published_latex = findRunParameter(
    "try_pdf_build_from_published_latex", 0, ATNM, int
)

get_documentation_defaults = findRunParameter(
    "get_documentation_defaults",
    [
        "/PROJECT/* =>  /TheProject",
        "/PROJECT/Documentation/**/* =>  /TheProject/Documentation",
        "/PROJECT/doc/**/*           =>  /TheProject/doc",
    ],
    ATNM,
)

# do not keep milestones that do not exist
ATNM = {k: v for k, v in ATNM.items() if v is not None}

# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append("CHECK PARAMS")

if exitcode == CONTINUE:
    loglist.append("PARAMS are ok")
else:
    loglist.append("Bad PARAMS or nothing to do")


# ==================================================
# work
# --------------------------------------------------

if talk > 1:
    print("# --------", toolchain_name, time_started_at)


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if "ATNM - All The New Milestones":
    result["MILESTONES"].append(ATNM)

if jobfile_json_abspath is not None:
    result["MILESTONES"].append({"jobfile_json_abspath": jobfile_json_abspath})

if jobfile_data is not None:
    result["MILESTONES"].append({"jobfile_data": jobfile_data})

if 1:
    # read 255 as: Toolchain did not finish
    result["MILESTONES"].append({"FINAL_EXITCODE": 255})

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
