#!/usr/bin/env python

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

# ==================================================
# define
# --------------------------------------------------

publish_package_dir = ''
publish_packages_xml_file = ''

# ==================================================
# Get and check required milestone(s)
# --------------------------------------------------

def milestones_get(name, default=None):
    result = milestones.get(name, default)
    loglist.append((name, result))
    return result

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

if exitcode == CONTINUE:
    package_file = milestones_get('package_file')
    publish_package_dir_planned = milestones_get('publish_package_dir_planned')

if exitcode == CONTINUE:
    if not (package_file and publish_package_dir_planned):
        exitcode = 2
        loglist.append(('PROBLEM with params'))

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')

# ==================================================
# work
# --------------------------------------------------

import hashlib
import re
import time

def hashfile(f1, hasher, blocksize=4096):
    buf = f1.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = f1.read(blocksize)
    return hasher.hexdigest()
# [(fname, hashfile(open(fname, 'rb'), hashlib.sha256())) for fname in fnamelst]

if exitcode == CONTINUE:
    if not os.path.exists(publish_package_dir_planned):
        os.mkdir(publish_package_dir_planned)
    publish_package_dir = publish_package_dir_planned

    if os.path.exists(package_file):
        filename = os.path.split(package_file)[1]
        dest = os.path.join(publish_package_dir, filename)
        loglist.append(('dest', dest))
        if os.path.isfile(dest):
            os.remove(dest)
        os.rename(package_file, dest)
    else:
        # should not occurr unless developing
        pass

if exitcode == CONTINUE:
    publish_packages_xml_file = os.path.join(publish_package_dir, 'packages.xml')
    if os.path.exists(publish_packages_xml_file):
        os.remove(publish_packages_xml_file)

if exitcode == CONTINUE:
    re_package_name = re.compile(
        '(?P<name>.+)'
        '-'
        '(?P<version>  [\d.]+ | latest)'
        '-'
        '(?P<language> [a-z][a-z]-[a-z][a-z] | default)'
        '(?P<fileext>  \.zip )',
        re.VERBOSE + re.IGNORECASE)

    for top, dirs, files in os.walk(publish_package_dir):
        dirs[:] = []
    files = [f for f in files if f.endswith('.zip')]
    files.sort()
    # files = ["sphinx-2.4-default.zip", "sphinx-latest-default.zip", "sphinx-2.3.4-fr-fr.zip", ]
    items = []
    for afile in files:
        fpath = os.path.join(publish_package_dir, afile)
        with file(fpath, 'rb') as f1:
            md5 = hashfile(f1, hashlib.md5())
        m = re_package_name.match(afile)
        if m:
            gd = m.groupdict()
            gd['md5'] = md5
            if '-' in gd['language']:
                L = gd['language']
                gd['language'] = L[0:2].lower() + '_' + L[3:5].upper()
            items.append(gd)
    unixtime = time.time()
    leadin = (
        '<?xml version="1.0" standalone="yes" ?>\n'
        '<documentationPackIndex>\n'
        '\t<meta>\n'
        '\t\t<timestamp>%d</timestamp>\n'
        '\t\t<date>%s</date>\n'
        '\t</meta>\n'
        '\t<languagePackIndex>\n' % (unixtime, tct.logstamp(unixtime=unixtime, fmt='%F %T')))
    leadout = (
        '\t</languagePackIndex>\n'
        '</documentationPackIndex>\n')

    with file(publish_packages_xml_file, 'w') as f2:
        f2.write(leadin)
        for item in items:
            f2.write(
                '\t\t<languagepack version="%(version)s" language="%(language)s">\n'
                '\t\t\t<md5>%(md5)s</md5>\n'
                '\t\t</languagepack>\n' % item)
        f2.write(leadout)

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if publish_packages_xml_file:
    result['MILESTONES'].append({
        'publish_packages_xml_file': publish_packages_xml_file})

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------
sys.exit(exitcode)
