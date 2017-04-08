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

CONTINUE = -1


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

TheProjectResultBuildinfoMessageObsolete = ''
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
            exitcode = 22

    # fetch
    TheProjectResultBuildinfo = milestones_get('TheProjectResultBuildinfo')
    TheProjectResult = milestones_get('TheProjectResult')
    TheProjectResultVersion = milestones_get('TheProjectResultVersion')
    buildsettings = milestones_get('buildsettings')
    webroot_part_of_builddir = milestones_get('webroot_part_of_builddir')
    url_of_webroot = milestones_get('url_of_webroot')
    buildsettings_builddir = milestones_get('buildsettings_builddir')
    relative_part_of_builddir = milestones_get('relative_part_of_builddir')
    webroot_abspath = milestones_get('webroot_abspath')

    # test
    if not (TheProjectResult and TheProjectResultVersion and
            TheProjectResultBuildinfo and buildsettings and
            webroot_part_of_builddir and url_of_webroot and
            buildsettings_builddir and relative_part_of_builddir and
            webroot_abspath):
        exitcode = 22

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

if exitcode == CONTINUE:
    build_html = milestones_get('build_html')
    settingscfg_file = milestones_get('settingscfg_file')
    warnings_file = milestones_get('warnings_file')
    warnings_file_size = milestones_get('warnings_file_size')
    TheProjectLog = milestones_get('TheProjectLog')
    TheProjectResultBuildinfoPdfFilesCnt = milestones_get('TheProjectResultBuildinfoPdfFilesCnt')
    TheProjectResultBuildinfoPdfLogFile = milestones_get('TheProjectResultBuildinfoPdfLogFile')
    email_notify_about_new_build = milestones_get('email_notify_about_new_build')
    email_user_do_not_send = milestones_get('email_user_do_not_send', 0) # config, commandline
    email_user_notify_is_turned_off = milestones_get('email_user_notify_is_turned_off')
    logstamp_finish = milestones_get('logstamp_finish', tct.logstamp())
    subject = u''

import codecs
import shutil

letter_to_owner = [u'']
subject = u'Documentation rendered: '

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
    if not os.path.exists(TheProjectResultBuildinfo):
        os.makedirs(TheProjectResultBuildinfo)

if exitcode == CONTINUE:
    builddir = webroot_abspath + relative_part_of_builddir
    builddir_parent = webroot_abspath + os.path.split(relative_part_of_builddir)[0]
    builddir_url = url_of_webroot + relative_part_of_builddir
    builddir_parent_url = url_of_webroot + os.path.split(relative_part_of_builddir)[0]

    packages_url = builddir_parent_url + '/packages/'
    package_url = None
    package_file = milestones_get('package_file')
    if package_file:
        package_url = packages_url + os.path.split(package_file)[1]

    subject = u'%s %s: Documentation rendered' % (bs['project'], bs['version'])

    # try to keep line length <= 60 chars

    tell_owner(u"""\
    From: Toolchain_RenderDocumentation@typo3.org

    """)

    tell_owner(u"""\
    -----

    DEAR PROJECT OWNER,

    thank you very much for providing a TYPO3 project
    that contains documentation.

    I am '""" + params['toolchain_name'] + """', the toolchain
    that renders (builds) documentation for you on the TYPO3
    documentation server http://docs.typo3.org/. You can find me
    at https://github.com/marble/Toolchain_RenderDocumentation.

    """)

    if email_notify_about_new_build:
        tell_owner("""\
            I am sending this mail because I found an entry like

            [notify]
            about_new_build = email-1, email-2, ...

            in the file PROJECT/Documentation/Settings.cfg. Therefore I'm
            sending this report to:

            """)
        for email_address in email_notify_about_new_build:
            tell_owner("%s\n" % email_address)
        tell_owner('\n')
    else:
        tell_owner("""\
            I have looked for file PROJECT/Documentation/Settings.cfg and
            an entry like:

            [notify]
            about_new_build = email-1, email2, ...

            But I couldn't find email addresses.

            """)

    emails_user_from_project = milestones.get('emails_user_from_project')
    if not email_notify_about_new_build and emails_user_from_project:
        tell_owner("""\
            Therefore I looked around for email addresses in the project.
            So I'm sending this report to:

            """)
        for email_address in emails_user_from_project:
            tell_owner("%s\n" % email_address)
        tell_owner('\n')

    if email_user_do_not_send:
        tell_owner("""\
            Actually, I will not really send a mail in the end because I saw that
            'no' in the list of possible receivers. But I still compile this info.

            """)

    tell_owner("""\
        Leave an option in file PROJECT/Documentation/Settings.cfg to have control:

        [notify]
        # have one or more receivers notified
        about_new_build = email-1 [, email2, ...]

        [notify]
        # turn off notification mails like so:
        about_new_build = no

        """)


    tell_owner("""\
    -----

    FOR YOUR INFORMATION

    A new build was run and finished right now: """ + logstamp_finish + """

    PROJECT: """ + bs['project'] + """
    VERSION: """ + bs['version'] + """

    """)

    if milestones_get('has_settingscfg_generated'):
        settingscfg_file
        shutil.copy(settingscfg_file, os.path.join(TheProjectResultBuildinfo, 'Settings.cfg'))
        subject = u'Attention: Action needed! ' + subject
        tell_owner("""\
            ==========
            ATTENTION:
            ----------

            The file format of the settings configuration file
            has changed:

            Settings.yml is the OLD format.
            Settings.cfg is the NEW format.

            I have found the old format but I did not find the
            new format in your project. So I generated a new
            Settings.cfg file from the old Settings.yml file.

            Please grab the new file from:

            """ + builddir_url + """/_buildinfo/Settings.cfg

            and add it to your project as:

            Documentation/Settings.cfg

            Please keap the old Yaml file as well. The reason
            for this is that right at the moment BOTH rendering
            processes are in action. So keep this file. We will
            tell you when it's not needed any more:

            Documentation/Settings.yml

            Thank you in advance!


        """)

    tell_owner("""\
        -----

        RESULTS

        """)
    assembled = milestones_get('assembled', [])

    if 'html' in assembled:
        tell_owner("HTML: Success!\n%s/\n\n" % builddir_url, ltrim=False)
    else:
        tell_owner("HTML: Failure!\n\n")

    if 'singlehtml' in assembled:
        tell_owner("SINGLEHTML: Success!\n%s/%s\n\n" % (builddir_url, 'singlehtml/'), ltrim=False)
    else:
        tell_owner("SINGLEHTML: Failure!\n\n")

    if 'pdf' in assembled:
        tell_owner("PDF: Success!\n%s/%s\n\n" % (builddir_url, '_pdf/manual.pdf'), ltrim=False)
    else:
        tell_owner("PDF: Failure!\n\n")

    if package_url:
        tell_owner("PACKAGE: Success!\n%s\n\n" % package_url, ltrim=False)
    else:
        tell_owner("PACKAGE: Failure!\n\n")

    if 1:
        tell_owner("BUILDINFO: Success!\n%s/%s\n\n" % (builddir_url, '_buildinfo/'), ltrim=False)
    tell_owner('\n')

    if warnings_file:
        tell_owner("""\
            -----

            SPHINX WARNINGS AND ERRORS

            """)

        if warnings_file_size is not None:
            if warnings_file_size:
                tell_owner("""\
                There are warnings!

                """)
            else:
                tell_owner("""\
                There are no warnings!

                """)

        tell_owner("""\
            Find the warnings file at
            %s%s

            """ % (builddir_url, '/_buildinfo/warnings.txt'))

        if warnings_file_size is not None:
            if warnings_file_size:
                tell_owner("""\
                The file 'warnings.txt' is %s bytes long. This means
                that Sphinx has reported warnings which you should
                look at.

                """ % warnings_file_size)
            else:
                tell_owner("""\
                    Congratulations!

                    The file 'warnings.txt' is empty. This means
                    that Sphinx didn't find errors and there wasn't even a warning.

                    Great!

                    """)


    # PDF

    tell_owner(u"""\
        -----

        PDF GENERATION

        """)

    if not TheProjectResultBuildinfoPdfFilesCnt:
        tell_owner(u"""\
            It looks there is no information at all about PDF
            generation in the buildinfo.

            """)
    else:
        tell_owner(u"""\
            Look at the buildinfo

            %s/%s

            for details about the PDF generation process.

            """ % (builddir_url, '_buildinfo/'))
        if TheProjectResultBuildinfoPdfLogFile:
            filename = os.path.split(TheProjectResultBuildinfoPdfLogFile)[1]
            tell_owner(u"""\
                The logfile probably is most interesting:

                %s/%s/%s

                """ % (builddir_url, '_buildinfo/', filename))
        if not 'pdf' in assembled:
            tell_owner(u"""\
                If the PDF logfile has a line '! LaTeX Error: Too deeply nested.'
                this propably means that the nesting of lists is too deep in
                your manuscript. The indentation of the lists sums up and
                doesn't fit on the PDF page. To overcome this you should
                rearrange the lists. As this FAQ [1] puts it to words:
                "What can be done about the problem? Not much, short of
                rewriting LaTeX — you really need to rewrite your document
                in a slightly less labyrinthine way."
                [1] http://www.tex.ac.uk/FAQ-toodeep.html

""")

    # Localization

    localization_has_localization = milestones_get('localization_has_localization')
    if localization_has_localization:

        tell_owner(u"""\
            -----

            LOCALIZATION

            This project contains a localization.

            (( describe that at the moment only the default language ))
            (( has been rendered but a makefolder for the localized ))
            (( version has been created. ))

            """)

    # list buildsettings

    if bs:
        tell_owner(u"""\
            -----

            SETTINGS

            These were the buildsettings:

            """)
        maxlen = max([len(k) for k in bs.keys()])
        filler = ' ' * maxlen
        for k in sorted(bs.keys()):
            tell_owner(u'%s%s: %s\n' % (k, filler[0:(maxlen - len(k))], bs[k]), ltrim=False)
        tell_owner(u'\n')

    tell_owner("""\
        -----

        ADDITIONAL INFORMATION

        General advice: Take a look at the BUILDINFO to
        see what happened. The buildinfo only changes when
        a new build is run.

        About output formats:

        HTML
        is the usual html output. Paths to static files for css,
        js, fonts are absolute so manuals on the server in general
        share the same static files.

        SINGLEHTML
        has everything in one html file.

        PDF
        is a pdf file generated from LaTeX.

        PACKAGE
        is a zip archive with the HTML output. It is well suited
        for offline reading since css and js files are included
        and paths are relative. If a PDF was generated that file
        is included too.

        BUILDINFO
        is a folder on the server with information about the last
        build.

        """)

    tell_owner("""\
        -----

        That's it - have a nice day.

        Regards,

        RenderDocumentation
        Toolchain for rendering documentation
    """)

    # This would be the original destination
    TheProjectResultBuildinfoMessageObsolete = os.path.join(TheProjectResultBuildinfo, 'DearProjectOwner.txt')

    # But since we now have the HTML-result message we just save this one - for nostalgic reasons -
    # in the workdir until we totally drop this step
    TheProjectResultBuildinfoMessageObsolete = os.path.join(workdir, 'DearProjectOwner.txt')

    with codecs.open(TheProjectResultBuildinfoMessageObsolete, 'w', 'utf-8') as f2:
        f2.write(letter_to_owner[0])

    # print(letter_to_owner[0])


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if exitcode == CONTINUE:
    result['MILESTONES'].append({'create_buildinfo': True,
                                 'TheProjectResultBuildinfo': TheProjectResultBuildinfo,
                                 'TheProjectResultBuildinfoMessageObsolete':TheProjectResultBuildinfoMessageObsolete,
                                 'logstamp_finish': logstamp_finish})
    if subject:
        result['MILESTONES'].append({'email_user_subject': subject})


# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)


# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
