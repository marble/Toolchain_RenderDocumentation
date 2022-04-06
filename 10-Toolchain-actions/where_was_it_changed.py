#!/usr/bin/env python
# coding: utf-8
# This is a helper tool that is under development. It is not run automatically
# as part of the toolchain.

from __future__ import absolute_import, print_function

import os
import shutil

import sys
import tct
from pprint import pprint as pp
from tct import deepget as lookup

params_json_path = ""
params_json_path = "/home/marble/Repositories/mbnas/mbgit/tct/test/job01/tmp-GENERATED-temp/RenderDocumentation/2021-11-25_12-10-53_156452/10-Toolchain-actions/params_01-Start-with-everything.py.json"

toolchain_RenderDocumentation = "/home/marble/Repositories/mbnas/mbgit/Toolchains/RenderDocumentation"

rendering = None
for dirname in list(
    sorted(
        os.listdir(
            "/home/marble/Repositories/mbnas/mbgit/tct/test/job01/tmp-GENERATED-temp/RenderDocumentation"
        ),
        reverse=True,
    )
):
    if dirname.startswith("2021-12"):
        rendering = dirname
        break

if not rendering:
    print("No rendering.")
    sys.exit(1)
else:
    print(rendering)

params_json_path = f"/home/marble/Repositories/mbnas/mbgit/tct/test/job01/tmp-GENERATED-temp/RenderDocumentation/{rendering}/10-Toolchain-actions/params_01-Start-with-everything.py.json"


params = tct.readjson(params_json_path or sys.argv[1])
facts = tct.readjson(params["factsfile"])
binabspath = facts.get("binabspath") or sys.argv[2]

milestones = tct.readjson(params["milestonesfile"])
reason = ""
resultfile = params["resultfile"]
result = tct.readjson(resultfile)
loglist = result["loglist"] = result.get("loglist", [])
toolname = params["toolname"]
toolname_pure = params["toolname_pure"]
workdir = params["workdir"]
workdir_home = params["workdir_home"]
exitcode = CONTINUE = 0

all = [
    "binabspath",
    "CONTINUE",
    "exitcode",
    "loglist",
    "milestones",
    "reason",
    "result",
    "resultfile",
    "toolname",
    "toolname_pure",
    "workdir",
    "workdir_home",
]

if 0:
    for k in all:
        print(f"{k}: {globals()[k]!r}")


# ==================================================
#
# --------------------------------------------------


def tool_file_has_keys(tool, keys):
    result = True
    with open(tool) as f1:
        data = f1.read()
    for k in keys:
        result = result and ((f'"{keys[0]}"' in data) or (f"'{keys[0]}'" in data))
        if not result:
            break
    return result


def milestones_files(root):
    later = []
    for top, dirs, files in os.walk(root):
        dirs.sort()
        files.sort()
        for fname in files:
            if fname == "milestones.json":
                later.append(os.path.join(top, fname))
            elif fname.startswith("milestones") and fname.endswith(".json"):
                yield os.path.join(top, fname)
    for fpath in later:
        yield fpath


def iter_tool_files(root):
    later = []
    for top, dirs, files in os.walk(root):
        dirs.sort()
        files.sort()
        for fname in files:
            if fname == "nixda":
                later.append(os.path.join(top, fname))
            elif fname.startswith("run_") and fname.endswith(".py"):
                yield os.path.join(top, fname)
    for fpath in later:
        yield fpath


if 1:
    tool_files = []
    for e, tool in enumerate(iter_tool_files(toolchain_RenderDocumentation)):
        tool_files.append((e, tool))


def trace_milestone(*keys, default=None):
    # from global
    root = workdir_home
    # from global
    milestones_0 = milestones
    milestones_1 = {}
    rootlen = len(root)
    print()
    print(f"==================================================")
    print(f"{keys},   default={default!r}")
    print()

    files = list(milestones_files(workdir_home))
    for e in range(0, len(files)):
        fpath = files[e]
        milestones_1 = tct.readjson(fpath)
        v0 = lookup(milestones_0, *keys, default=default)
        v1 = lookup(milestones_1, *keys, default=default)
        if e == 0:
            v0 = not v1
        if 0 or v1 != v0:
            print(f"{e:3d} {fpath[rootlen:]}")
        if v1 != v0:
            print(f"        {v1!r}")
        # print(f"{e:3d} {fpath[rootlen:]}")
        if e + 1 == len(files):
            print()
            print("Final:")
            print(f"        {v1!r}")

        milestones_0 = milestones_1
        v0 = v1

    if 1:
        for e, tool in tool_files:
            if tool_file_has_keys(tool, keys):
                print(f"{e:3d}: {tool}")


# ==================================================
#
# --------------------------------------------------

if 0:
    pp(globals())

if 0:
    whlen = len(workdir_home)
    for fpath in milestones_files(workdir_home):
        print(fpath[whlen:])

if 1:
    alist = [
        # ["TheProjectCacheDir"],
        # ["buildsettings", "builddir"],
        # ["buildsettings", "masterdoc"],
        # ["buildsettings", "t3docdir"],
        # ["docsdir"],
        # ["documentation_folder"],
        # ["masterdoc"],
        # ["masterdoc_candidates_initial"],
        # ["masterdocs_selected"],
        # ["relative_part_of_builddir"],
        ["settings_cfg"],
        ["settingscfg_file"],
        ["settings_cfg_file"],
    ]
    for keys in alist:
        trace_milestone(*keys, default=None)

if 0:
    print()
    print(f"==================================================")
    print(f"All the tools")
    print(f"--------------------------------------------------")
    print()
    for e, tool in tool_files:
        print(f"{e:3d}: {tool}")

sys.exit(exitcode)
