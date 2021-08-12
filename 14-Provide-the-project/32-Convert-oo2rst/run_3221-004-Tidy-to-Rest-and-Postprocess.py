#!/usr/bin/env python

from __future__ import absolute_import, print_function

import os

import sys

#
import normalize_empty_lines
import ooxhtml2rst
import prepend_sections_with_labels
import tct
import tweak_dllisttables

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

masterdoc_manual_html_004_as_rst = {}
masterdoc_manual_html_005_as_rst = {}


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append("CHECK PARAMS")

    masterdoc_manual_html_003_from_tidy = lookup(
        milestones, "masterdoc_manual_html_003_from_tidy"
    )
    TheProjectBuildOpenOffice2Rest = lookup(
        milestones, "TheProjectBuildOpenOffice2Rest"
    )

    if not (masterdoc_manual_html_003_from_tidy and TheProjectBuildOpenOffice2Rest):
        CONTINUE = -2
        reason = "Bad PARAMS or nothing to do"

if exitcode == CONTINUE:
    loglist.append("PARAMS are ok")
else:
    loglist.append("Bad PARAMS or nothing to do")


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:

    infile = masterdoc_manual_html_003_from_tidy
    outfile = os.path.join(TheProjectBuildOpenOffice2Rest, "manual-004.rst")
    outfile005 = os.path.join(TheProjectBuildOpenOffice2Rest, "manual-005.rst")

    appendlog = 0
    taginfo = 0
    tabletypes = ["t3flt", "dl"]

    for i, tablesas in enumerate(tabletypes):
        thisFiles004 = {}
        thisFiles005 = {}
        thisOutfile = outfile[:-3] + tablesas + ".rst"
        thisOutfile005 = outfile005[:-3] + tablesas + ".rst"
        thisTreefile = thisOutfile + ".restparser-tree.txt"
        thisLogfile = thisOutfile + ".restparser-log.txt"

        ooxhtml2rst.main(
            infile, thisOutfile, thisTreefile, thisLogfile, appendlog, taginfo, tablesas
        )

        if os.path.exists(thisOutfile):
            exitcode = 0
            normalize_empty_lines.main(thisOutfile, thisOutfile005, 2)
        else:
            exitcode = 1

        if exitcode == 0:
            if thisOutfile and os.path.exists(thisOutfile):
                thisFiles004["outfile"] = thisOutfile
            if thisTreefile and os.path.exists(thisTreefile):
                thisFiles004["treefile"] = thisTreefile
            if thisLogfile and os.path.exists(thisLogfile):
                thisFiles004["logfile"] = thisLogfile

        if thisFiles004:
            masterdoc_manual_html_004_as_rst[tablesas] = thisFiles004

        if os.path.exists(thisOutfile005):
            thisFiles005["outfile"] = thisOutfile005

        if thisFiles005:
            masterdoc_manual_html_005_as_rst[tablesas] = thisFiles005


if exitcode == CONTINUE:

    # postprocess
    for i, tablesas in enumerate(tabletypes):
        thisFiles = masterdoc_manual_html_005_as_rst.get(tablesas, {})
        rstfile = thisFiles.get("outfile")
        if rstfile:
            if exitcode == CONTINUE:
                prepend_sections_with_labels.processRstFile(rstfile)

            if exitcode == CONTINUE:
                tweak_dllisttables.processRstFile(rstfile)

            if exitcode == CONTINUE:
                with open(rstfile, "rb") as f1:
                    data = f1.read()
                data = data.replace(
                    ".. .. include:: ./FIXME/Includes.txt",
                    ".. include:: ../Includes.txt",
                )
                with open(rstfile, "wb") as f2:
                    f2.write(data)
    if 0:
        pass
        # for each of our newly created *.rst provide a Docutils rendering
        # errorfilename = 'sxw2html-conversion-error.txt'
        # self.t3docutils_stylesheet_path
        # self.usr_bin_python
        # self.t3rst2html_script
        # self.safetempdir

        # for f2path_rst in self.rstfilepaths:
        #    normalize_empty_lines.main(f2path_rst, self.f2path_rst_temp, 2)
        #    os.remove(f2path_rst)
        #    os.rename(self.f2path_rst_temp, f2path_rst)


# ==================================================
# Set MILESTONES
# --------------------------------------------------

if masterdoc_manual_html_004_as_rst:
    result["MILESTONES"].append(
        {"masterdoc_manual_html_004_as_rst": masterdoc_manual_html_004_as_rst}
    )

if masterdoc_manual_html_005_as_rst:
    result["MILESTONES"].append(
        {"masterdoc_manual_html_005_as_rst": masterdoc_manual_html_005_as_rst}
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
