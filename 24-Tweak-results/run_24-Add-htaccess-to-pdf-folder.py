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
    pdf_dest_file = milestones_get('pdf_dest_file')
    pdf_dest_folder = milestones_get('pdf_dest_folder')
    bs = milestones.get('buildsettings', {})
    buildsettings_builddir = bs.get('builddir')
    # yyyyyyyyy
    webroot_abspath = tct.deepget(facts, 'tctconfig', 'RenderDocumentation', 'webroot_abspath')


if not (pdf_dest_file and pdf_dest_folder and buildsettings_builddir and webroot_abspath):
    CONTINUE = -1


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    example = "/typo3cms/drafts/github/TYPO3-Documentation/DocsTypo3Org-Homepage/latest/_pdf/manual.DocsTypo3Org-Homepage-1.0.0.pdf"
    temp = os.path.join(buildsettings_builddir, '_pdf', os.path.split(pdf_dest_file)[1])
    pdf_abspath_on_server = temp[len(webroot_abspath):]

    htaccess_contents = (
        "RewriteEngine On\n"
        "RewriteCond %{REQUEST_FILENAME} !-f\n"
        "RewriteRule ^(.*)$ " + pdf_abspath_on_server + " [L,R=301]\n")

    pdf_dest_folder_htaccess = os.path.join(pdf_dest_folder, '.htaccess')
    with file(pdf_dest_folder_htaccess, 'w') as f2:
        f2.write(htaccess_contents)

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if exitcode == CONTINUE:
    result['MILESTONES'].append({'pdf_dest_folder_htaccess': pdf_dest_folder_htaccess,
                                 })

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
