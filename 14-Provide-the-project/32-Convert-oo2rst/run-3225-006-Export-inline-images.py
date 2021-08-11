#!/usr/bin/env python

from __future__ import print_function
from __future__ import absolute_import
import os
import tct
import sys

#
import PIL

params = tct.readjson(sys.argv[1])
binabspath = sys.argv[2]
facts = tct.readjson(params["factsfile"])
milestones = tct.readjson(params["milestonesfile"])
resultfile = params["resultfile"]
result = tct.readjson(resultfile)
loglist = result["loglist"] = result.get("loglist", [])
toolname = params["toolname"]
toolname_pure = params["toolname_pure"]
workdir = params["workdir"]
exitcode = CONTINUE = 0

CONTINUE = -1

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

masterdoc_manual_html_gifs_fixed = None


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append("CHECK PARAMS")

    masterdoc_manual_000_html = lookup(milestones, "masterdoc_manual_000_html")
    TheProjectBuildOpenOffice2Rest = lookup(
        milestones, "TheProjectBuildOpenOffice2Rest"
    )
    if not (masterdoc_manual_000_html and TheProjectBuildOpenOffice2Rest):
        CONTINUE = -2

if exitcode == CONTINUE:
    loglist.append("PARAMS are ok")
else:
    loglist.append("Bad PARAMS or nothing to do")


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:

    # .. |img-1|      image:: data:image/png;base64,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

    from __future__ import print_function
    import email
    import codecs
    from pprint import pprint
    import re
    import sys

    f1path = "infile.eml"
    f2stem = "outfile"

    cidmapping = {}
    f1 = codecs.open(f1path, "r", "utf-8")
    msg = email.message_from_file(f1)
    f1.close()

    # email.iterators._structure(msg)
    parts = []
    for part in email.iterators.typed_subpart_iterator(msg):
        print(list(part.items()))

    for part in email.iterators.typed_subpart_iterator(msg, "text", "html"):
        parts.append(part)

    for part in email.iterators.typed_subpart_iterator(msg, "image"):
        parts.append(part)

    for part in parts:
        pprint(list(part.items()))
        payload = part.get_payload(decode=True)
        content_type = part.get_content_type()
        print(part.get_content_type(), len(part), repr(payload))
        if content_type == "text/html":
            f2path = f2stem + ".html"
            f2 = codecs.open(f2path, "w", "utf-8")
            f2.write(payload)
            f2.close()
        elif content_type.startswith("image/"):
            s = re.search('filename="(.+)"', part["Content-Disposition"])
            if s and s.groups():
                filename = s.groups()[0]
                f2path = f2stem + "-" + filename
                f2 = open(f2path, "w")
                f2.write(payload)
                f2.close()
            cidmapping[part["Content-ID"]] = filename

        pprint(cidmapping)

    f2path = f2stem + ".html"
    data = codecs.open(f2path, "r", "utf-8").read()

    for k, v in cidmapping.items():
        ka = "cid:" + k[1:-1]
        va = f2stem + "-" + v
        print(ka, va)
        data = data.replace(ka, va)

    codecs.open(f2path, "w", "utf-8").write(data)

    masterdoc_manual_html_gifs_fixed = os.path.join(
        TheProjectBuildOpenOffice2Rest, "manual-001-gifs-fixed.html"
    )

    L = []
    for fname in os.listdir(TheProjectBuildOpenOffice2Rest):
        if fname.lower().startswith("manual_html_") and fname.lower().endswith(".gif"):
            L.append(fname)
    if L:
        for fname in L:
            gifFile = os.path.join(TheProjectBuildOpenOffice2Rest, fname)
            im = PIL.Image.open(gifFile)
            pngFile = gifFile + ".png"
            im.save(pngFile)

    with open(masterdoc_manual_000_html, "rb") as f1:
        data = f1.read()

    for fname in L:
        data = data.replace(fname, fname + ".png")

    with open(masterdoc_manual_html_gifs_fixed, "wb") as f2:
        f2.write(data)


# ==================================================
# Set MILESTONES
# --------------------------------------------------

if masterdoc_manual_html_gifs_fixed:
    result["MILESTONES"].append(
        {"masterdoc_manual_html_gifs_fixed": masterdoc_manual_html_gifs_fixed}
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
