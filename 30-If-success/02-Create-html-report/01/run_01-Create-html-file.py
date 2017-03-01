#!/usr/bin/env python
# coding: utf-8

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
import cgi
import os
import shutil
import sys
import tct

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

# Set to true to generate an email with all textblocks for the purpose of reviewing
debugkeepAllBlocks = 0

HKV = html_key_values = {}
htmlesc = lambda x: cgi.escape(x, True)
htmlmail_template_file = None
milestone_abc = None
talk = milestones.get('talk', 1)
TheProjectLogHtmlmail = ''
TheProjectLogHtmlmailMessageHtml = ''
TheProjectResultBuildinfoMessage = ''
TheProjectResultHtmlmailMessageHtml = ''
TheProjectLogHtmlmailMessageMdTxt = ''
TheProjectLogHtmlmailMessageRstTxt = ''
TheProjectLogHtmlmailMessageTxt = ''
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

    # fetch
    create_buildinfo = milestones_get('create_buildinfo')
    TheProjectLog = milestones_get('TheProjectLog')
    TheProjectResultBuildinfo = milestones_get('TheProjectResultBuildinfo')
    toolchain_name = params_get('toolchain_name')

    # test
    if not (
        create_buildinfo and
        TheProjectLog and
        TheProjectResultBuildinfo and
        toolchain_name):

        CONTINUE = -1


if exitcode == CONTINUE:
    TheProjectResultBuildinfoMessage = milestones_get('TheProjectResultBuildinfoMessage')
    if not TheProjectResultBuildinfoMessage:
        TheProjectResultBuildinfoMessage = os.path.join(TheProjectResultBuildinfo, 'DearProjectOwner')
    TheProjectResultHtmlmailMessageHtml = TheProjectResultBuildinfoMessage + '.html'

    toolfolderabspath = params_get('toolfolderabspath')
    if not toolfolderabspath:
        exitcode = 2


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
    TheProjectLogHtmlmail = milestones_get('TheProjectLogHtmlmail')
    if not TheProjectLogHtmlmail:
        TheProjectLogHtmlmail = os.path.join(TheProjectLog, 'htmlmail')
    if not os.path.exists(TheProjectLogHtmlmail):
        os.mkdir(TheProjectLogHtmlmail)

if exitcode == CONTINUE:
    htmlmail_template_file = os.path.join(toolfolderabspath, 'templates', 't3docs.html')
    if not os.path.isfile(htmlmail_template_file):
        loglist.append(('fatal: htmlmail_template_file not found', htmlmail_template_file))
        exitcode = 2

if exitcode == CONTINUE:
    # use individual variables for nice code completion in PyCharm
    absurl_buildinfo_dir        = milestones_get('absurl_buildinfo_dir')
    absurl_html_dir             = milestones_get('absurl_html_dir')
    absurl_package_dir          = milestones_get('absurl_package_dir')
    absurl_package_file         = milestones_get('absurl_package_file')
    absurl_parent_dir           = milestones_get('absurl_parent_dir')
    absurl_parent_parent_dir    = milestones_get('absurl_parent_parent_dir')
    absurl_pdf_dir              = milestones_get('absurl_pdf_dir')
    absurl_pdf_file             = milestones_get('absurl_pdf_file')
    absurl_settings_cfg_file    = milestones_get('absurl_settings_cfg_file')
    absurl_singlehtml_dir       = milestones_get('absurl_singlehtml_dir')
    absurl_warnings_txt_file    = milestones_get('absurl_warnings_txt_file')

    email_notify_about_new_build = milestones_get('email_notify_about_new_build', [])
    email_user_notify_is_turned_off = milestones_get('email_user_notify_is_turned_off', 0)
    emails_user_from_project = milestones_get('emails_user_from_project')

# ==================================================
# work
# --------------------------------------------------

def do_the_work():

    global email_notify_about_new_build
    global emails_user_from_project

    from bs4 import BeautifulSoup
    import codecs
    import sys

    with codecs.open(htmlmail_template_file, 'r', 'utf-8') as f1:
        html_doc = f1.read()

    soup = BeautifulSoup(html_doc, 'html.parser')

    def first_or_none(resultset):
        result = None
        if len(resultset):
            result = resultset[0]
        return result

    def decompose_these(*args):
        result = []
        for i, arg in enumerate(args):
            if arg:
                arg.decompose()
                result.append(None)
            else:
                result.append(arg)
        return result




    # gather information

    h1 = soup.h1
    h2 = soup.h2
    h3 = soup.h3
    h4 = soup.h4
    p = soup.p
    a = soup.a

    idDivYourProject = first_or_none(soup.find_all(id="idDivYourProject"))
    idCalloutSettingsFile = first_or_none(soup.find_all(id="idCalloutSettingsFile"))
    idCalloutCongratulations = first_or_none(soup.find_all(id="idCalloutCongratulations"))
    idCalloutThereAreWarnings = first_or_none(soup.find_all(id="idCalloutThereAreWarnings"))
    idDivAboutThisMail = first_or_none(soup.find_all(id="idDivAboutThisMail"))
    idDivGeneralInformation = first_or_none(soup.find_all(id="idDivGeneralInformation"))

    idSpanISendToReceivers = first_or_none(soup.find_all(id="idSpanISendToReceivers"))
    idSpanISawANo = first_or_none(soup.find_all(id="idSpanISawANo"))
    idFoundSettingAboutEmailing = first_or_none(soup.find_all(id="idFoundSettingAboutEmailing"))
    idFoundNoSettingAboutEmailing = first_or_none(soup.find_all(id="idFoundNoSettingAboutEmailing"))
    idSendToProjectEmails = first_or_none(soup.find_all(id="idSendToProjectEmails"))

    idABUILDINFO = first_or_none(soup.find_all(id="idABUILDINFO"))
    idAHTML= first_or_none(soup.find_all(id="idAHTML"))
    idASINGLEHTML= first_or_none(soup.find_all(id="idASINGLEHTML"))
    idAPDF = first_or_none(soup.find_all(id="idAPDF"))
    idAPACKAGE= first_or_none(soup.find_all(id="idAPACKAGE"))


    # What succeeded? What failed?

    successparts = []
    failparts = []

    build_html = milestones_get('build_html')
    if build_html and absurl_html_dir:
        attrs = a.attrs.copy()
        attrs['href'] = absurl_html_dir
        atag = soup.new_tag('a', **attrs)
        atag.string = 'html'
        successparts.append(unicode(atag))
    else:
        failparts.append('html')

    build_singlehtml = milestones_get('build_singlehtml')
    if build_singlehtml and absurl_singlehtml_dir:
        attrs = a.attrs.copy()
        attrs['href'] = absurl_singlehtml_dir
        atag = soup.new_tag('a', **attrs)
        atag.string = 'singlehtml'
        successparts.append(unicode(atag))
    else:
        failparts.append('singlehtml')

    if absurl_pdf_file:
        attrs = a.attrs.copy()
        attrs['href'] = absurl_pdf_file
        atag = soup.new_tag('a', **attrs)
        atag.string = 'pdf'
        successparts.append(unicode(atag))
    else:
        failparts.append('pdf')

    if absurl_package_file:
        attrs = a.attrs.copy()
        attrs['href'] = absurl_package_file
        atag = soup.new_tag('a', **attrs)
        atag.string = 'package'
        successparts.append(unicode(atag))
    else:
        failparts.append('package')

    if absurl_buildinfo_dir:
        attrs = a.attrs.copy()
        attrs['href'] = absurl_buildinfo_dir
        atag = soup.new_tag('a', **attrs)
        atag.string = 'buildinfo'
        successparts.append(unicode(atag))
    else:
        failparts.append('buildinfo')

    successparts = successparts if successparts else ['nothing']
    failparts = failparts if failparts else ['nothing']


    # Example of suitable values for the html template:

    HKV['project_name'] = 'Projectname'
    HKV['project_version'] = '1.2.3'
    HKV['build_time'] = '2017-02-02 16:41:13'
    HKV['this_was_made'] = 'html, pdf.'
    HKV['this_failed'] = 'singlehtml, package.'
    HKV['absurl_buildinfo'] = '#absurl_buildinfo'
    HKV['absurl_warnings_txt'] = '#absurl_warnings_txt'
    HKV['absurl_settings_cfg'] = '#absurl_settings_cfg'
    HKV['receivers_from_settings_cfg'] = '<a href="mailto:one@mail.com>one@mail.com</a>, <a href="mailto:two@mail.com>two@mail.com</a>'
    HKV['receivers_from_project'] = '<a href="mailto:three@mail.com>three@mail.com</a>'

    build_time = milestones.get('time_finished_at')
    if build_time:
        build_time = ' '.join(build_time.split(' ')[:2])


    # email_user_receivers_exlude_list

    project_name = tct.deepget(milestones, 'settings_cfg', 'general', 'project', default='PROJECT?')
    project_version = tct.deepget(milestones, 'settings_cfg', 'general', 'version', default='VERSION?')
    build_time = build_time if build_time else 'BUILDTIME?'

    # The values are filled into the HTML code directly.
    # So we have to escape them.
    HKV['project_name']         = htmlesc(project_name)
    HKV['project_version']      = htmlesc(project_version)
    HKV['build_time']           = htmlesc(build_time)
    HKV['this_was_made']        = u', '.join(successparts) + '.'
    HKV['this_failed']          = u', '.join(failparts) + '.'
    HKV['absurl_buildinfo']     = htmlesc(absurl_buildinfo_dir)
    HKV['absurl_publish_dir']   = htmlesc(absurl_html_dir)
    HKV['absurl_warnings_txt']  = htmlesc(absurl_warnings_txt_file)
    HKV['absurl_settings_cfg']  = htmlesc(absurl_settings_cfg_file)

    HKV['receivers_from_settings_cfg']  = '<a href="mailto:one@mail.com>one@mail.com</a>, <a href="mailto:two@mail.com>two@mail.com</a>'
    HKV['receivers_from_project']       = '<a href="mailto:three@mail.com>three@mail.com</a>, <a href="mailto:four@mail.com>four@mail.com</a>'

    v = 'None'
    if email_notify_about_new_build:
        temp = []
        for email in email_notify_about_new_build:
            attrs = a.attrs.copy()
            attrs['href'] = 'mailto:' + email
            atag = soup.new_tag('a', **attrs)
            atag.string = email
            temp.append(unicode(atag))
        v = u', '.join(temp)
    HKV['receivers_from_settings_cfg'] = v

    v = 'None'
    if emails_user_from_project:
        temp = []
        for email in emails_user_from_project:
            attrs = a.attrs.copy()
            attrs['href'] = 'mailto:' + email
            atag = soup.new_tag('a', **attrs)
            atag.string = email
            temp.append(unicode(atag))
        v = u', '.join(temp)
    HKV['receivers_from_project'] = v


    # text block logic
    # we remove textblocks that shall not appear

    has_settingscfg_generated = milestones_get('has_settingscfg_generated')
    if has_settingscfg_generated:
        # We have created a Settings.cfg from a Yaml file
        pass
    else:
        if not debugkeepAllBlocks:
            idCalloutSettingsFile = decompose_these(idCalloutSettingsFile)

    warnings_file_size = milestones_get('warnings_file_size')
    if warnings_file_size == 0:
        # Congratulations!
        if not debugkeepAllBlocks:
            idCalloutThereAreWarnings = decompose_these(idCalloutThereAreWarnings)
    else:
        # Sphinx shows errors
        if not debugkeepAllBlocks:
            idCalloutCongratulations = decompose_these(idCalloutCongratulations)

    # explicitly turn off by config or commandline
    email_user_do_not_send = milestones_get('email_user_do_not_send', 0)
    # explicitly turn off by 'no' as email
    email_user_notify_is_turned_off = milestones_get('email_user_notify_is_turned_off')

    # list of emails. May be empty.
    email_notify_about_new_build = milestones_get('email_notify_about_new_build')

    if not email_user_notify_is_turned_off: # and email_notify_about_new_build: # ?
        # We really send to receivers we found in settings
        if not debugkeepAllBlocks:
            idSpanISawANo = decompose_these(idSpanISawANo)
    else:
        # We really found a 'no' in the settings
        if not debugkeepAllBlocks:
            idSpanISendToReceivers = decompose_these(idSpanISendToReceivers)

    email_user_notify_setting_exists = milestones_get('email_user_notify_setting_exists')
    if email_user_notify_setting_exists:
        # We found an entry about emailing in the settings
        if not debugkeepAllBlocks:
            idFoundNoSettingAboutEmailing, idSendToProjectEmails = decompose_these(idFoundNoSettingAboutEmailing, idSendToProjectEmails)
    else:
        # We did not find an entry about emailing in the settings
        if not debugkeepAllBlocks:
            decompose_these(idFoundSettingAboutEmailing)

    emails_user_from_project = milestones_get('emails_user_from_project')
    if idSendToProjectEmails and not email_user_do_not_send and not email_notify_about_new_build and emails_user_from_project:
        pass
    else:
        if not debugkeepAllBlocks:
            idSendToProjectEmails = decompose_these(idSendToProjectEmails)



    # handle links in the General Info section

    if absurl_buildinfo_dir:
        # if we have BUILDINFO '#buildinfo
        idABUILDINFO.attrs['href'] = absurl_buildinfo_dir
    else:
        # if we have no BUILDINFO
        new_strong_tag = soup.new_tag("strong")
        new_strong_tag.string = idABUILDINFO.string
        idABUILDINFO.replace_with(new_strong_tag)

    if absurl_html_dir:
        # if we have HTML '#html'
        idAHTML.attrs['href'] = absurl_html_dir
    else:
        # if we have no HTML
        new_strong_tag = soup.new_tag("strong")
        new_strong_tag.string = idAHTML.string
        idAHTML.replace_with(new_strong_tag)

    if absurl_singlehtml_dir:
        # if we have SINGLEHTML '#singlehtml'
        idASINGLEHTML.attrs['href'] = absurl_singlehtml_dir
    else:
        # if we have no SINGLEHTML
        new_strong_tag = soup.new_tag("strong")
        new_strong_tag.string = idASINGLEHTML.string
        idASINGLEHTML.replace_with(new_strong_tag)

    if absurl_pdf_file:
        # if we have a PDF '#pdf'
        idAPDF.attrs['href'] = absurl_pdf_file
    else:
        # if we have no PDF
        new_strong_tag = soup.new_tag("strong")
        new_strong_tag.string = idAPDF.string
        idAPDF.replace_with(new_strong_tag)

    if absurl_package_file:
        # if we have no PACKAGE '#package'
        idAPACKAGE.attrs['href'] = absurl_package_file
    else:
        # if we have no PACKAGE
        new_strong_tag = soup.new_tag("strong")
        new_strong_tag.string = idAPACKAGE.string
        idAPACKAGE.replace_with(new_strong_tag)


    # lstrip the <pre> blocks

    for pre in soup.find_all('pre'):
        pre.string.replace_with(u'\n'.join([part.lstrip() for part in pre.string.split('\n')]))
        print(pre.string)

    # create outfile
    # replace variables

    with codecs.open('DearProjectOwner-prettified.html', 'w', 'utf-8') as f2:
        prettified = soup.prettify()
        prettified = prettified.replace('%', '%%').replace('%%(', '%(') % HKV
        f2.write(prettified)

    with codecs.open('DearProjectOwner.html', 'w', 'utf-8') as f2:
        prettified = unicode(soup)
        prettified = prettified.replace('%', '%%').replace('%%(', '%(') % HKV
        f2.write(prettified)

if exitcode == CONTINUE:
    do_the_work()


if 0:
    # atm there may be a DearProjectOwner.txt as well. Rename that file
    # so it is flagged as disabled
    TheProjectResultBuildinfoMessage = milestones_get('TheProjectResultBuildinfoMessage')
    if TheProjectResultBuildinfoMessage:
        fpath, fname = os.path.split(TheProjectResultBuildinfoMessage)
        obsolete = os.path.join(fpath, 'zzz-OBSOLETE-' + fname)
        shutil.move(TheProjectResultBuildinfoMessage, obsolete)
    TheProjectResultBuildinfoMessage = ''

if exitcode == CONTINUE:
    src = 'DearProjectOwner-prettified.html'
    TheProjectLogHtmlmailMessageHtml = TheProjectLogHtmlmail + '/DearProjectOwner.html'
    shutil.copy(src, TheProjectLogHtmlmailMessageHtml)

if exitcode == CONTINUE:
    src = 'DearProjectOwner-prettified.html'
    TheProjectResultBuildinfoMessage = os.path.join(TheProjectResultBuildinfo, 'DearProjectOwner')
    TheProjectResultBuildinfoMessageHtml = TheProjectResultBuildinfoMessage + '.html'
    shutil.copy(TheProjectLogHtmlmailMessageHtml, TheProjectResultBuildinfoMessageHtml)

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if 'always!':
    result['MILESTONES'].append({
        'TheProjectResultBuildinfoMessage': TheProjectResultBuildinfoMessage,
        'TheProjectResultHtmlmailMessageHtml': TheProjectResultHtmlmailMessageHtml,
    })

if html_key_values:
    result['MILESTONES'].append({'html_key_values': html_key_values})

if TheProjectLogHtmlmail: result['MILESTONES'].append(
    {'TheProjectLogHtmlmail': TheProjectLogHtmlmail})

if TheProjectLogHtmlmailMessageHtml: result['MILESTONES'].append(
    {'TheProjectLogHtmlmailMessageHtml': TheProjectLogHtmlmailMessageHtml})



# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
