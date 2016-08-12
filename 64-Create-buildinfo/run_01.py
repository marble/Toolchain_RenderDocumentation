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
    TheProjectResult = milestones_get('TheProjectResult')
    TheProjectResultVersion = milestones_get('TheProjectResultVersion')
    buildsettings = milestones_get('buildsettings')
    logstamp_finish = milestones_get('logstamp_finish', tct.logstamp())

if not (TheProjectResult and TheProjectResultVersion and buildsettings):
    CONTINUE = -1

# ==================================================
# work
# --------------------------------------------------

letter_to_owner = [u'']
subject = u''

def create_letter_writer(letter=None, ltrim=True):
    if letter is None:
        letter = [u'']
    def write_letter(ustr, ltrim=ltrim):
        resultlines = []
        for line in ustr.split(u'\n'):
            if not resultlines:
                indent = len(line) - len(line.lstrip())
            if ltrim:
                if not line[0:indent].strip():
                    resultlines.append(line[indent:])
                else:
                    resultlines.append(line.lstrip())
            else:
                resultlines.append(line)
        letter[0] = letter[0] + u'\n'.join(resultlines)
    return write_letter

tell_owner = create_letter_writer(letter_to_owner)

if exitcode == CONTINUE:
    bs = buildsettings
    TheProjectResultBuildinfo = os.path.join(TheProjectResult, '_buildinfo')
    if not os.path.exists(TheProjectResultBuildinfo):
        os.makedirs(TheProjectResultBuildinfo)

    # "builddir": "/home/mbless/public_html/typo3cms/extensions/sphinx/latest",
    builddir = buildsettings['builddir']
    builddir_parent = os.path.split(builddir)[0]
    builddir_parent_url = builddir_parent.replace('/home/mbless/public_html/', 'https://docs.typo3.org/typo3cms/')
    builddir_url = builddir.replace('/home/mbless/public_html/', 'https://docs.typo3.org/typo3cms/')
    packages_url = builddir_parent_url + 'packages/'
    package_url = None
    package_file = milestones_get('package_file')
    if package_file:
        package_url = packages_url + os.path.split(package_file)[1]


    tell_owner(u"""\
    Dear project owner,

    thank you very much for providing a TYPO3 project that contains documentation.

    I am '""" + params['toolchainname'] + """', the toolchain that renders (builds) the documentation for you
    on the TYPO3 documentation server http://docs.typo3.org/. You can find me currently
    at https://github.com/marble/TCT. This may change in future.

    """)

    emails_user = milestones.get('emails_user')
    if emails_user:
        if len(emails_user) == 1:
            tell_owner("""\
                I am sending this mail because I found an email address in the project.
                Write to documentation@typo3.org if this is not appropriate:
                   %s\n\n""" % emails_user[0])
        else:
            tell_owner("""\
                I am sending this mail because I found email addresses in the project.
                Write to documentation@typo3.org if this is not appropriate:
                   %s\n\n""" % emails_user)

    tell_owner("""\
    A new build was run and finished right now.

    PROJECT: """ + bs['project'] + """
    VERSION: """ + bs['version'] + """
    DONE   : """ + logstamp_finish + """

    """)

    if milestones_get('has_settingscfg_generated'):
        subject += "((es muss was getan werden))"
        tell_owner("""\
            ==================================================
            ATTENTION:
            --------------------------------------------------
            The file format of the settings configuration file has changed.
               Settings.yml is the OLD format.
               Settings.cfg is the NEW format.

            We found the old format but not the new format in your project.
            So we generated the new Settings.cfg from the old Settings.yml.

            Please grab the new file from:
               """ + builddir_url + """_buildinfo/Settings.cfg

            and add it to your project as:
               Documentation/Settings.cfg

            You should then remove:
               Documentation/Settings.yml

            Thank you for understanding!
            ==================================================

        """)

    tell_owner("""\
        These are the build results:
        """)
    assembled = milestones_get('assembled', [])

    if 'html' in assembled:
        tell_owner("   HTML      : success : %s/\n" % builddir_url, ltrim=False)
    else:
        tell_owner("   HTML      : failure : %s/\n" % builddir_url, ltrim=False)

    if 'singlehtml' in assembled:
        tell_owner("   SINGLEHTML: success : %s/%s\n" % (builddir_url, 'singlehtml/'), ltrim=False)
    else:
        tell_owner("   SINGLEHTML: failure : %s/%s\n" % (builddir_url, 'singlehtml/'), ltrim=False)

    if 'pdf' in assembled:
        tell_owner("   PDF       : success : %s/%s\n" % (builddir_url, '_pdf/'), ltrim=False)
    else:
        tell_owner("   PDF       : success : %s/%s\n" % (builddir_url, '_pdf/'), ltrim=False)

    if package_url:
        tell_owner("   PACKAGE   : success : %s\n" % package_url, ltrim=False)
    else:
        tell_owner("   PACKAGE   : failure : %s\n" % package_url, ltrim=False)

    if 1:
        tell_owner("   BUILDINFO : success : %s/%s\n" % (builddir_url, '_buildinfo/'), ltrim=False)
    tell_owner('\n')



    tell_owner("""\
        ((Todo marble: PACKAGE: The package Index has to be updated!))

        Hints:
           Look at the BUILDINFO to see if there's something
           in file 'warnings.txt'.

           Look at the BUILDINFO to find details about the
           PDF generation process.

    """)


    # list buildsettings
    if bs and 1:
        tell_owner(u"""\
            These were the buildsettings:
            """)
        maxlen = max([len(k) for k in bs.keys()])
        filler = ' ' * maxlen
        for k in sorted(bs.keys()):
            tell_owner(u'   %s%s: %s\n' % (k, filler[0:(maxlen - len(k))], bs[k]), ltrim=False)
        tell_owner(u'\n')

    tell_owner("""\
        About output formats:
           HTML       is the usual html output.
           SINGLEHTML has everything in one html file.
           PDF        is a pdf file generated from LaTeX.
           PACKAGE    is a zip archive with the HTML output and the PDF, if present.
                      It is suitable for offline reading.
           BUILDINFO  is a folder on the server with information about the last build process.

        """)

    tell_owner("""\
        That's it - have a nice day.

        Regards,

        RenderDocumentation
        Toolchain for rendering documentation
    """)

    print(letter_to_owner[0])



CONTINUE = -1

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if exitcode == CONTINUE:
    result['MILESTONES'].append({'create_buildinfo': True,
                                 'logstamp_finish': logstamp_finish})

#builddir = buildsettings['builddir']
#project_basedir = os.path.split(builddir)[0]
#project_url = project_basedir.replace('/home/mbless/public_html/', 'https://docs.typo3.org/typo3cms/')
#project_version_url = builddir.replace('/home/mbless/public_html/', 'https://docs.typo3.org/typo3cms/')

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
