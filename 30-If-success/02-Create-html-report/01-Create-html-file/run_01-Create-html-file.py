#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function
from __future__ import absolute_import
import tct
import sys

#
import copy
import os
import shutil
import six

# excpecting 'pip install future'
from html import escape as htmlesc

params = tct.readjson(sys.argv[1])
facts = tct.readjson(params["factsfile"])
milestones = tct.readjson(params["milestonesfile"])
reason = ""
resultfile = params["resultfile"]
result = tct.readjson(resultfile)
toolname = params["toolname"]
toolname_pure = params["toolname_pure"]
toolchain_name = facts["toolchain_name"]
workdir = params["workdir"]
loglist = result["loglist"] = result.get("loglist", [])
exitcode = CONTINUE = 0


# ==================================================
# Make a copy of milestones for later inspection?
# --------------------------------------------------

if 0 or milestones.get("debug_always_make_milestones_snapshot"):
    tct.make_snapshot_of_milestones(params["milestonesfile"], sys.argv[1])


# ==================================================
# Helper functions
# --------------------------------------------------

deepget = tct.deepget


def lookup(D, *keys, **kwdargs):
    result = deepget(D, *keys, **kwdargs)
    loglist.append((keys, result))
    return result


# ==================================================
# define
# --------------------------------------------------

# Set to true to generate an email with all textblocks for the purpose of reviewing
debugkeepAllBlocks = 0

HKV = html_key_values = {}
htmlmail_template_file = None
milestone_abc = None
talk = milestones.get("talk", 1)
TheProjectLogHtmlmail = ""
TheProjectLogHtmlmailMessageHtml = ""
TheProjectResultBuildinfoMessage = ""
TheProjectResultHtmlmailMessageHtml = ""
TheProjectLogHtmlmailMessageMdTxt = ""
TheProjectLogHtmlmailMessageRstTxt = ""
TheProjectLogHtmlmailMessageTxt = ""


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append("CHECK PARAMS")

    create_buildinfo = lookup(milestones, "create_buildinfo")
    TheProjectLog = lookup(milestones, "TheProjectLog")
    TheProjectResultBuildinfo = lookup(milestones, "TheProjectResultBuildinfo")

    if not (create_buildinfo and TheProjectLog and TheProjectResultBuildinfo):
        exitcode = 22
        reason = "Bad params or nothing to do"


if exitcode == CONTINUE:
    TheProjectResultBuildinfoMessage = lookup(
        milestones, "TheProjectResultBuildinfoMessage"
    )
    if not TheProjectResultBuildinfoMessage:
        TheProjectResultBuildinfoMessage = os.path.join(
            TheProjectResultBuildinfo, "DearProjectOwner"
        )
    TheProjectResultHtmlmailMessageHtml = TheProjectResultBuildinfoMessage + ".html"

    toolfolderabspath = lookup(params, "toolfolderabspath")
    if not toolfolderabspath:
        exitcode = 22
        reason = "Bad params or nothing to do"


if exitcode == CONTINUE:
    loglist.append("PARAMS are ok")
else:
    loglist.append("Bad PARAMS or nothing to do")


# ==================================================
# work
# --------------------------------------------------

# DocumentationGeneratedZipFile


if exitcode == CONTINUE:
    TheProjectLogHtmlmail = lookup(milestones, "TheProjectLogHtmlmail")
    if not TheProjectLogHtmlmail:
        TheProjectLogHtmlmail = os.path.join(TheProjectLog, "htmlmail")
    if not os.path.exists(TheProjectLogHtmlmail):
        os.mkdir(TheProjectLogHtmlmail)

if exitcode == CONTINUE:
    htmlmail_template_file = os.path.join(toolfolderabspath, "templates", "t3docs.html")
    if not os.path.isfile(htmlmail_template_file):
        loglist.append(
            ("fatal: htmlmail_template_file not found", htmlmail_template_file)
        )
        exitcode = 22
        reason = "Fatal: htmlmail_template not found"

if exitcode == CONTINUE:
    # use individual variables for nice code completion in PyCharm
    absurl_buildinfo_dir = lookup(milestones, "absurl_buildinfo_dir")
    absurl_html_dir = lookup(milestones, "absurl_html_dir")
    absurl_package_dir = lookup(milestones, "absurl_package_dir")
    absurl_package_file = lookup(milestones, "absurl_package_file")
    absurl_parent_dir = lookup(milestones, "absurl_parent_dir")
    absurl_project_parent_dir = lookup(milestones, "absurl_project_parent_dir")
    absurl_pdf_dir = lookup(milestones, "absurl_pdf_dir")
    absurl_pdf_file = lookup(milestones, "absurl_pdf_file")
    absurl_settings_cfg_file = lookup(milestones, "absurl_settings_cfg_file")
    absurl_singlehtml_dir = lookup(milestones, "absurl_singlehtml_dir")
    absurl_warnings_txt_file = lookup(milestones, "absurl_warnings_txt_file")
    documentation_zip_file = lookup(
        milestones, "DocumentationGeneratedZipFile", default=""
    )
    email_notify_about_new_build = lookup(
        milestones, "email_notify_about_new_build", default=[]
    )
    email_user_notify_is_turned_off = lookup(
        milestones, "email_user_notify_is_turned_off", default=0
    )
    emails_user_from_project = lookup(milestones, "emails_user_from_project")

    if documentation_zip_file:
        absurl_documentation_zip_file = "%s/%s" % (
            absurl_buildinfo_dir.rstrip("/"),
            documentation_zip_file,
        )
    else:
        absurl_documentation_zip_file = ""


# ==================================================
# work
# --------------------------------------------------


def do_the_work():

    global email_notify_about_new_build
    global emails_user_from_project

    from bs4 import BeautifulSoup
    import codecs
    import sys

    with codecs.open(htmlmail_template_file, "r", "utf-8") as f1:
        html_doc = f1.read()

    soup = BeautifulSoup(html_doc, "html.parser")

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

    a = soup.a
    h1 = soup.h1
    h2 = soup.h2
    h3 = soup.h3
    h4 = soup.h4
    p = soup.p

    a_attrs = a.attrs.copy() if a else {}
    h1_attrs = h1.attrs.copy() if h1 else {}
    h2_attrs = h2.attrs.copy() if h2 else {}
    h3_attrs = h3.attrs.copy() if h3 else {}
    h4_attrs = h4.attrs.copy() if h4 else {}
    p_attrs = p.attrs.copy() if p else {}

    idDivYourProject = soup.find(id="idDivYourProject")
    idCalloutSettingsFile = soup.find(id="idCalloutSettingsFile")
    idDocumentationFromOpenOffice = soup.find(id="idDocumentationFromOpenOffice")
    idCalloutCongratulations = soup.find(id="idCalloutCongratulations")
    idCalloutThereAreWarnings = soup.find(id="idCalloutThereAreWarnings")
    idDivAboutThisMail = soup.find(id="idDivAboutThisMail")
    idDivGeneralInformation = soup.find(id="idDivGeneralInformation")
    idDivMoreOnYourProject = soup.find(id="idDivMoreOnYourProject")
    idSpanISendToReceivers = soup.find(id="idSpanISendToReceivers")
    idSpanISawANo = soup.find(id="idSpanISawANo")
    idFoundSettingAboutEmailing = soup.find(id="idFoundSettingAboutEmailing")
    idFoundNoSettingAboutEmailing = soup.find(id="idFoundNoSettingAboutEmailing")
    idSendToProjectEmails = soup.find(id="idSendToProjectEmails")
    idABUILDINFO = soup.find(id="idABUILDINFO")
    idAHTML = soup.find(id="idAHTML")
    idASINGLEHTML = soup.find(id="idASINGLEHTML")
    idAPDF = soup.find(id="idAPDF")
    idAPACKAGE = soup.find(id="idAPACKAGE")

    # # there is this 'clone' functionality
    # # https://stackoverflow.com/questions/23057631/clone-element-with-beautifulsoup
    #
    # idCalloutDocumentationFromOpenOffice = copy.copy(idCalloutSettingsFile)
    # if idCalloutDocumentationFromOpenOffice:
    #     idCalloutDocumentationFromOpenOffice.attrs['id'] = 'idCalloutDocumentationFromOpenOffice'
    #     idCalloutSettingsFile.insert_after(idCalloutDocumentationFromOpenOffice)
    #
    #     for elm in idCalloutDocumentationFromOpenOffice.find_all('p'):
    #         elm.decompose()
    #
    #     ptag = soup.new_tag('p', **p_attrs)
    #     ptag.string = 'Important!'
    #     idCalloutDocumentationFromOpenOffice.h2.insert_after(ptag)

    # Add info about localization

    localization_has_localization = lookup(milestones, "localization_has_localization")
    localization = tct.deepget(milestones, "buildsettings", "localization")
    if localization_has_localization:
        h3tag = soup.new_tag("h3", **h3_attrs)
        h3tag.string = "Localization"
        idDivMoreOnYourProject.append(h3tag)
        ptag = soup.new_tag("p", **p_attrs)
        ptag.append(
            u"Yes, I have seen that your project contains one or more localizations.\n"
        )
        if localization in ["", "default"]:
            ptag.append(u"In this run I have rendered the default language.\n")
        else:
            ptag.append(
                u"In this run I have rendered the '%s' version.\n" % localization
            )
        ptag.append(u"Each localization is done in an extra run.\n")
        idDivMoreOnYourProject.append(ptag)

    # What succeeded? What failed?

    successparts = []
    failparts = []

    build_html = lookup(milestones, "build_html")
    if build_html and absurl_html_dir:
        attrs = a.attrs.copy()
        attrs["href"] = absurl_html_dir
        atag = soup.new_tag("a", **attrs)
        atag.string = "html"
        successparts.append(six.text_type(atag))
    else:
        failparts.append("html")

    build_singlehtml = lookup(milestones, "build_singlehtml")
    if build_singlehtml and absurl_singlehtml_dir:
        attrs = a.attrs.copy()
        attrs["href"] = absurl_singlehtml_dir
        atag = soup.new_tag("a", **attrs)
        atag.string = "singlehtml"
        successparts.append(six.text_type(atag))
    else:
        failparts.append("singlehtml")

    if absurl_pdf_file:
        attrs = a.attrs.copy()
        attrs["href"] = absurl_pdf_file
        atag = soup.new_tag("a", **attrs)
        atag.string = "pdf"
        successparts.append(six.text_type(atag))
    else:
        failparts.append("pdf")

    if absurl_package_file:
        attrs = a.attrs.copy()
        attrs["href"] = absurl_package_file
        atag = soup.new_tag("a", **attrs)
        atag.string = "package"
        successparts.append(six.text_type(atag))
    else:
        failparts.append("package")

    if absurl_buildinfo_dir:
        attrs = a.attrs.copy()
        attrs["href"] = absurl_buildinfo_dir
        atag = soup.new_tag("a", **attrs)
        atag.string = "buildinfo"
        successparts.append(six.text_type(atag))
    else:
        failparts.append("buildinfo")

    successparts = successparts if successparts else ["nothing"]
    failparts = failparts if failparts else ["nothing"]

    # Example of suitable values for the html template:

    HKV["project_name"] = "Projectname"
    HKV["project_version"] = "1.2.3"
    HKV["build_time"] = "2017-02-02 16:41:13"
    HKV["this_was_made"] = "html, pdf."
    HKV["this_failed"] = "singlehtml, package."
    HKV["absurl_buildinfo"] = "#absurl_buildinfo"
    HKV["absurl_warnings_txt"] = "#absurl_warnings_txt"
    HKV["absurl_settings_cfg"] = "#absurl_settings_cfg"
    HKV[
        "receivers_from_settings_cfg"
    ] = '<a href="mailto:one@mail.com>one@mail.com</a>, <a href="mailto:two@mail.com>two@mail.com</a>'
    HKV["receivers_from_project"] = '<a href="mailto:three@mail.com>three@mail.com</a>'

    build_time = milestones.get("time_finished_at")
    if build_time:
        build_time = " ".join(build_time.split(" ")[:2])

    # email_user_receivers_exlude_list

    project_name = tct.deepget(
        milestones, "settings_cfg", "general", "project", default="PROJECT?"
    )
    project_version = tct.deepget(
        milestones, "settings_cfg", "general", "version", default="VERSION?"
    )
    build_time = build_time if build_time else "BUILDTIME?"

    # The values are filled into the HTML code directly.
    # So we have to escape them.
    HKV["project_name"] = htmlesc(project_name)
    HKV["project_version"] = htmlesc(project_version)
    HKV["build_time"] = htmlesc(build_time)
    HKV["this_was_made"] = u", ".join(successparts) + "."
    HKV["this_failed"] = u", ".join(failparts) + "."
    HKV["absurl_buildinfo"] = htmlesc(absurl_buildinfo_dir)
    HKV["absurl_publish_dir"] = htmlesc(absurl_html_dir)
    HKV["absurl_warnings_txt"] = htmlesc(absurl_warnings_txt_file)
    HKV["absurl_settings_cfg"] = htmlesc(absurl_settings_cfg_file)
    HKV["absurl_documentation_zip"] = htmlesc(absurl_documentation_zip_file)

    HKV[
        "receivers_from_settings_cfg"
    ] = '<a href="mailto:one@mail.com>one@mail.com</a>, <a href="mailto:two@mail.com>two@mail.com</a>'
    HKV[
        "receivers_from_project"
    ] = '<a href="mailto:three@mail.com>three@mail.com</a>, <a href="mailto:four@mail.com>four@mail.com</a>'

    v = "None"
    if email_notify_about_new_build:
        temp = []
        for email in email_notify_about_new_build:
            attrs = a.attrs.copy()
            attrs["href"] = "mailto:" + email
            atag = soup.new_tag("a", **attrs)
            atag.string = email
            temp.append(six.text_type(atag))
        v = u", ".join(temp)
    HKV["receivers_from_settings_cfg"] = v

    v = "None"
    if emails_user_from_project:
        temp = []
        for email in emails_user_from_project:
            attrs = a.attrs.copy()
            attrs["href"] = "mailto:" + email
            atag = soup.new_tag("a", **attrs)
            atag.string = email
            temp.append(six.text_type(atag))
        v = u", ".join(temp)
    HKV["receivers_from_project"] = v

    # text block logic
    # we remove textblocks that shall not appear

    has_settingscfg_generated = lookup(milestones, "has_settingscfg_generated")
    if has_settingscfg_generated:
        # We have created a Settings.cfg from a Yaml file
        pass
    else:
        if not debugkeepAllBlocks:
            idCalloutSettingsFile = decompose_these(idCalloutSettingsFile)

    # Documentation generated from OpenOffice?
    if documentation_zip_file:
        # yes
        pass
    else:
        # no
        if not debugkeepAllBlocks:
            idDocumentationFromOpenOffice = decompose_these(
                idDocumentationFromOpenOffice
            )

    warnings_file_size = lookup(milestones, "warnings_file_size")
    if warnings_file_size == 0:
        # Congratulations!
        if not debugkeepAllBlocks:
            idCalloutThereAreWarnings = decompose_these(idCalloutThereAreWarnings)
    else:
        # Sphinx shows errors
        if not debugkeepAllBlocks:
            idCalloutCongratulations = decompose_these(idCalloutCongratulations)

    # explicitly turn off by config or commandline
    email_user_do_not_send = lookup(milestones, "email_user_do_not_send", default=0)
    # explicitly turn off by 'no' as email
    email_user_notify_is_turned_off = lookup(
        milestones, "email_user_notify_is_turned_off"
    )

    # list of emails. May be empty.
    email_notify_about_new_build = lookup(milestones, "email_notify_about_new_build")

    if not email_user_notify_is_turned_off:  # and email_notify_about_new_build: # ?
        # We really send to receivers we found in settings
        if not debugkeepAllBlocks:
            idSpanISawANo = decompose_these(idSpanISawANo)
    else:
        # We really found a 'no' in the settings
        if not debugkeepAllBlocks:
            idSpanISendToReceivers = decompose_these(idSpanISendToReceivers)

    email_user_notify_setting_exists = lookup(
        milestones, "email_user_notify_setting_exists"
    )
    if email_user_notify_setting_exists:
        # We found an entry about emailing in the settings
        if not debugkeepAllBlocks:
            idFoundNoSettingAboutEmailing, idSendToProjectEmails = decompose_these(
                idFoundNoSettingAboutEmailing, idSendToProjectEmails
            )
    else:
        # We did not find an entry about emailing in the settings
        if not debugkeepAllBlocks:
            decompose_these(idFoundSettingAboutEmailing)

    emails_user_from_project = lookup(milestones, "emails_user_from_project")
    if (
        idSendToProjectEmails
        and not email_user_do_not_send
        and not email_notify_about_new_build
        and emails_user_from_project
    ):
        pass
    else:
        if not debugkeepAllBlocks:
            idSendToProjectEmails = decompose_these(idSendToProjectEmails)

    # handle links in the General Info section

    if absurl_buildinfo_dir:
        # if we have BUILDINFO '#buildinfo
        idABUILDINFO.attrs["href"] = absurl_buildinfo_dir
    else:
        # if we have no BUILDINFO
        new_strong_tag = soup.new_tag("strong")
        new_strong_tag.string = idABUILDINFO.string
        idABUILDINFO.replace_with(new_strong_tag)

    if absurl_html_dir:
        # if we have HTML '#html'
        idAHTML.attrs["href"] = absurl_html_dir
    else:
        # if we have no HTML
        new_strong_tag = soup.new_tag("strong")
        new_strong_tag.string = idAHTML.string
        idAHTML.replace_with(new_strong_tag)

    if absurl_singlehtml_dir:
        # if we have SINGLEHTML '#singlehtml'
        idASINGLEHTML.attrs["href"] = absurl_singlehtml_dir
    else:
        # if we have no SINGLEHTML
        new_strong_tag = soup.new_tag("strong")
        new_strong_tag.string = idASINGLEHTML.string
        idASINGLEHTML.replace_with(new_strong_tag)

    if absurl_pdf_file:
        # if we have a PDF '#pdf'
        idAPDF.attrs["href"] = absurl_pdf_file
    else:
        # if we have no PDF
        new_strong_tag = soup.new_tag("strong")
        new_strong_tag.string = idAPDF.string
        idAPDF.replace_with(new_strong_tag)

    if absurl_package_file:
        # if we have no PACKAGE '#package'
        idAPACKAGE.attrs["href"] = absurl_package_file
    else:
        # if we have no PACKAGE
        new_strong_tag = soup.new_tag("strong")
        new_strong_tag.string = idAPACKAGE.string
        idAPACKAGE.replace_with(new_strong_tag)

    # lstrip the <pre> blocks

    for pre in soup.find_all("pre"):
        pre.string.replace_with(
            u"\n".join([part.lstrip() for part in pre.string.split("\n")])
        )

    # create outfile
    # replace variables

    with codecs.open("DearProjectOwner-prettified.html", "w", "utf-8") as f2:
        prettified = soup.prettify()
        prettified = prettified.replace("%", "%%").replace("%%(", "%(") % HKV
        f2.write(prettified)

    with codecs.open("DearProjectOwner.html", "w", "utf-8") as f2:
        prettified = six.text_type(soup)
        prettified = prettified.replace("%", "%%").replace("%%(", "%(") % HKV
        f2.write(prettified)


if exitcode == CONTINUE:
    do_the_work()


if 0:
    # atm there may be a DearProjectOwner.txt as well. Rename that file
    # so it is flagged as disabled
    TheProjectResultBuildinfoMessage = lookup(
        milestones, "TheProjectResultBuildinfoMessage"
    )
    if TheProjectResultBuildinfoMessage:
        fpath, fname = os.path.split(TheProjectResultBuildinfoMessage)
        obsolete = os.path.join(fpath, "zzz-OBSOLETE-" + fname)
        shutil.move(TheProjectResultBuildinfoMessage, obsolete)
    TheProjectResultBuildinfoMessage = ""

if exitcode == CONTINUE:
    src = "DearProjectOwner-prettified.html"
    TheProjectLogHtmlmailMessageHtml = TheProjectLogHtmlmail + "/DearProjectOwner.html"
    shutil.copy(src, TheProjectLogHtmlmailMessageHtml)

if exitcode == CONTINUE:
    src = "DearProjectOwner-prettified.html"
    TheProjectResultBuildinfoMessage = os.path.join(
        TheProjectResultBuildinfo, "DearProjectOwner"
    )
    TheProjectResultBuildinfoMessageHtml = TheProjectResultBuildinfoMessage + ".html"
    shutil.copy(TheProjectLogHtmlmailMessageHtml, TheProjectResultBuildinfoMessageHtml)

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if "always!":
    result["MILESTONES"].append(
        {
            "TheProjectResultBuildinfoMessage": TheProjectResultBuildinfoMessage,
            "TheProjectResultHtmlmailMessageHtml": TheProjectResultHtmlmailMessageHtml,
        }
    )

if html_key_values:
    result["MILESTONES"].append({"html_key_values": html_key_values})

if TheProjectLogHtmlmail:
    result["MILESTONES"].append({"TheProjectLogHtmlmail": TheProjectLogHtmlmail})

if TheProjectLogHtmlmailMessageHtml:
    result["MILESTONES"].append(
        {"TheProjectLogHtmlmailMessageHtml": TheProjectLogHtmlmailMessageHtml}
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
