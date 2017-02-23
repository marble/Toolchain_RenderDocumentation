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
binabspath = sys.argv[2]
facts = tct.readjson(params['factsfile'])
milestones = tct.readjson(params['milestonesfile'])
resultfile = params['resultfile']
result = tct.readjson(resultfile)
loglist = result['loglist'] = result.get('loglist', [])
toolname = params["toolname"]
toolname_pure = params['toolname_pure']
workdir = params['workdir']
exitcode = CONTINUE = 0


# ==================================================
# Make a copy of milestones for later inspection?
# --------------------------------------------------

if 0 or milestones.get('debug_always_make_milestones_snapshot'):
    tct.make_snapshot_of_milestones(params['milestonesfile'], sys.argv[1])


# ==================================================
# Get and check required milestone(s)
# --------------------------------------------------

def milestones_get(name, default=None):
    result = milestones.get(name, default)
    loglist.append((name, result))
    return result

def facts_get(name, default=None):
    result = facts.get(name, default)
    loglist.append((name, result))
    return result

def params_get(name, default=None):
    result = params.get(name, default)
    loglist.append((name, result))
    return result


# ==================================================
# define
# --------------------------------------------------

xeq_name_cnt = 0


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    # required milestones
    requirements = []

    # just test
    for requirement in requirements:
        v = milestones_get(requirement)
        if not v:
            loglist.append("'%s' not found" % requirement)
            exitcode = 2

    build_html_folder = milestones_get('build_html_folder')
    build_singlehtml_folder = milestones_get('build_singlehtml_folder')

    if not (build_html_folder):
        CONTINUE = -1

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('PROBLEMS with params')

if CONTINUE != 0:
    loglist.append({'CONTINUE': CONTINUE})
    loglist.append('NOTHING to do')


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
    version_major_minor = None
    pattern = os.path.join(build_html_folder, '_static') + '/t3SphinxThemeRtd*.txt'
    files = sorted( glob.glob(pattern), reverse=1)
    loglist.append(['files', files])
    re_searcher = re.compile('t3SphinxThemeRtd-(?P<version>(?P<version_major_minor>\d+\.\d+)(\.\d+)*)\.txt')
    for fname in files:
        if version:
            break
        match = re_searcher.search(fname)
        if match:
            version = match.groupdict()['version']
            loglist.append(['version', version])
            version_major_minor = match.groupdict()['version_major_minor']
            loglist.append(['version_major_minor', version_major_minor])

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

    replacement = unicode(r'\g<intro>\g<quote>/t3SphinxThemeRtd/' + version_major_minor +
                          '/' + '\g<payload>\g<quote>')

    for build_folder in [build_html_folder, build_singlehtml_folder]:
        if not build_folder:
            continue
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
