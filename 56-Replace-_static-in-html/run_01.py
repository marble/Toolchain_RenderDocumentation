#!/usr/bin/env python
# coding: utf-8

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
import os
import tct
import sys

params = tct.readjson(sys.argv[1])
facts = tct.readjson(params['factsfile'])
milestones = tct.readjson(params['milestonesfile'])
resultfile = params['resultfile']
result = tct.readjson(resultfile)
toolname = params["toolname"]
loglist = result['loglist'] = result.get('loglist', [])
exitcode = CONTINUE = 0
errormsg = ''
helpmsg = ''

# ==================================================
# Check required milestone(s)
# --------------------------------------------------
def milestones_get(name, default=None):
    result = milestones.get(name, default)
    loglist.append((name, result))
    return result

if exitcode == CONTINUE:
    build_html_folder = milestones_get('build_html_folder')
    build_singlehtml_folder = milestones_get('build_singlehtml_folder')

if not (build_html_folder or build_singlehtml_folder):
    CONTINUE = -1

# ==================================================
# work
# --------------------------------------------------

# """
# old: href="../../_static/css/t3more.css"
# new: href="/t3SphinxThemeRtd/3.6.0/css/t3more.css"
#
# old: src="../../_static/jquery.js"
# new: src="/t3SphinxThemeRtd/3.6.0/jquery.js"
#
# """

if exitcode == CONTINUE:

    # Find the version. Look for a file like '_static/t3SphinxThemeRtd-3.6.0.txt'

    import codecs
    import glob
    import re

    # should become something like '3.6.0'
    version = None
    pattern = os.path.join(build_html_folder, '_static') + '/t3SphinxThemeRtd*.txt'
    files = sorted( glob.glob(pattern), reverse=1)
    loglist.append(['files', files])
    for fname in files:
        if version:
            break
        match = re.search('t3SphinxThemeRtd-([\d][\d\.]*)\.txt', fname)
        if match:
            version = match.group(1)
            loglist.append(['version', version])

    if not version:
        loglist.append('No version found. Cannot replace anything.')
        CONTINUE = -1

if exitcode == CONTINUE:

    regexpattern = re.compile(
        u"""
            (?P<intro>
            (?:href|src)           # non capturing href or src
            \s*                    # optional whitespace
            =
            \s*                    # optional whitespace
            )
            (?P<quote>"|')         # group "quote" is either ' or "
            \s*                    # unlikely whitespace
            (?P<relpart>[\./]*_static/)   # the relative part we want to replace
            (?P<payload>[\S]*)     # the payload
            \s*                    # unlikely whitespace
            (?P=quote)             # the quote again
        """,
        re.VERBOSE)

    replacement = unicode(r'\g<intro>\g<quote>/t3SphinxThemeRtd/' + version + '/' + '\g<payload>\g<quote>')

    for build_folder in [build_html_folder, build_singlehtml_folder]:
        builder_logname = os.path.split(build_folder)[1]
        toplen = len(build_folder)
        for top, dirs, files in os.walk(build_folder):
            dirs[:] = [d for d in dirs if d != '_static']
            dirs.sort()
            files.sort()
            for fname in files:
                if not fname.endswith('.html'):
                    continue
                fpath = os.path.join(top, fname)
                file_logname = fpath[toplen:].lstrip('/')
                with codecs.open(fpath, 'r', 'utf-8') as f1:
                    data = f1.read()
                data, cnt = regexpattern.subn(replacement, data)
                if cnt:
                    with codecs.open(fpath, 'w', 'utf-8') as f2:
                        f2.write(data)
                loglist.append('%s, %s, %s' % (cnt, builder_logname, file_logname))


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if exitcode == CONTINUE:
    result['MILESTONES'].append({'replace_static_in_html': True})

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
