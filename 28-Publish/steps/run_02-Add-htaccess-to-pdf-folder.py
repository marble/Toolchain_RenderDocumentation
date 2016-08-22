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

# ==================================================
# Check required milestone(s)
# --------------------------------------------------

def milestones_get(name, default=None):
    result = milestones.get(name, default)
    loglist.append((name, result))
    return result

def facts_get(name, default=None):
    result = facts.get(name, default)
    loglist.append((name, result))
    return result

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')
    toolchain_name = facts_get('toolchain_name')
    if not toolchain_name:
        exitcode = 2

if exitcode == CONTINUE:
    pdf_dest_file = milestones_get('pdf_dest_file')
    pdf_dest_folder = milestones_get('pdf_dest_folder')
    publish_dir_pdf_planned = milestones_get('publish_dir_pdf_planned')
    webroot_abspath = tct.deepget(facts, 'tctconfig', toolchain_name, 'webroot_abspath')
    loglist.append(('webroot_abspath', webroot_abspath))

if exitcode == CONTINUE:
    if not (pdf_dest_file and pdf_dest_folder and publish_dir_pdf_planned and webroot_abspath):
        loglist.append(('parameter PROBLEM'))
        exitcode = 2

if exitcode == CONTINUE:
    loglist.append(('PARAMS are ok'))

# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    temp = os.path.join(publish_dir_pdf_planned, os.path.split(pdf_dest_file)[1])
    pdf_url_path = temp[len(webroot_abspath):]
    loglist.append(('pdf_url_path', pdf_url_path))

    htaccess_contents = (
        "RewriteEngine On\n"
        "RewriteCond %{REQUEST_FILENAME} !-f\n"
        "RewriteRule ^(.*)$ " + pdf_url_path + " [L,R=301]\n")

    pdf_dest_folder_htaccess = os.path.join(pdf_dest_folder, '.htaccess')
    with file(pdf_dest_folder_htaccess, 'w') as f2:
        f2.write(htaccess_contents)

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if exitcode == CONTINUE:
    result['MILESTONES'].append({
        'pdf_dest_folder_htaccess': pdf_dest_folder_htaccess,
        'pdf_url_path': pdf_url_path,
        })

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
