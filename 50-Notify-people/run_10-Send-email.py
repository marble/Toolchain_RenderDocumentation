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
toolchain_name = facts['toolchain_name']
workdir = params['workdir']
exitcode = CONTINUE = 0


# ==================================================
# Make a copy of milestones for later inspection?
# --------------------------------------------------

if 0 or milestones.get('debug_always_make_milestones_snapshot'):
    tct.make_snapshot_of_milestones(params['milestonesfile'], sys.argv[1])


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

smtp_host = None
sender = 'RenderDocumentation@typo3.org'
receivers = ''
subject = lookup(milestones, 'email_user_subject', default='Your project: Documentation rendered')
textfile = None
htmlfile = None
cmdline_reportlines = milestones.get('cmdline_reportlines', [])
talk = milestones.get('talk', 1)
xeq_name_cnt = 0


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    # required milestones
    requirements = [
        'configset',
        'smtp_host'
    ]

    # just test
    for requirement in requirements:
        v = lookup(milestones, requirement, default=None)
        if v is None:
            loglist.append("'%s' not found" % requirement)
            exitcode = 22

if exitcode == CONTINUE:
    configset = lookup(milestones, 'configset')
    TheProjectLogHtmlmailMessageHtml = lookup(milestones, 'TheProjectLogHtmlmailMessageHtml')
    TheProjectLogHtmlmailMessageMdTxt = lookup(milestones, 'TheProjectLogHtmlmailMessageMdTxt')
    TheProjectLogHtmlmailMessageRstTxt = lookup(milestones, 'TheProjectLogHtmlmailMessageRstTxt')
    TheProjectLogHtmlmailMessageTxt = lookup(milestones, 'TheProjectLogHtmlmailMessageTxt')

    textfile = TheProjectLogHtmlmailMessageTxt or TheProjectLogHtmlmailMessageRstTxt or TheProjectLogHtmlmailMessageMdTxt
    htmlfile = TheProjectLogHtmlmailMessageHtml
    if not (textfile or htmlfile):
        loglist.append('No textfile and no htmlfile specified')
        CONTINUE = -1

    smtp_host = lookup(milestones, 'smtp_host')
    if not smtp_host:
        loglist.append("'Won't send mails. No smtp_host specified.")
        CONTINUE = -2

if exitcode == CONTINUE:
    email_admin = lookup(milestones, 'email_admin')
    email_admin_send_extra_mail = lookup(milestones, 'email_admin_send_extra_mail')
    email_notify_about_new_build = lookup(milestones, 'email_notify_about_new_build')
    email_user_bcc = lookup(milestones, 'email_user_bcc')
    email_user_cc = lookup(milestones, 'email_user_cc')
    email_user_do_not_send = lookup(milestones, 'email_user_do_not_send') # at the commandline
    email_user_notify_is_turned_off = lookup(milestones, 'email_user_notify_is_turned_off')
    email_user_to_instead = lookup(milestones, 'email_user_to_instead')
    emails_user_from_project = lookup(milestones, 'emails_user_from_project')

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('PROBLEMS with params')

if exitcode == 22:
    loglist.append('I cannot send mails.')

if CONTINUE != 0:
    loglist.append({'CONTINUE': CONTINUE})
    loglist.append('NOTHING to do')

# ==================================================
# functions
# --------------------------------------------------

if exitcode == CONTINUE:
    import codecs
    import smtplib
    from email.header import Header
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

def as_list(v):
    if not v:
        result = []
    elif type(v) == list:
        result = v
    elif isinstance(v, basestring):
        result = [s.strip() for s in v.replace(',', ' ').split(' ') if s.strip()]
    else:
        result = []
    return result

def send_the_mail(sender, receivers, subject='',
                  ccreceivers=None, bccreceivers=None, smtp_host='localhost',
                  textfile=None, htmlfile=None):

    sendmail_result = None

    # todo: bugfix!
    # see http://mg.pov.lt/blog/unicode-emails-in-python.html

    msg_to_value = ', '.join(as_list(receivers))
    msg_cc_value = ', '.join(as_list(ccreceivers))
    msg_bcc_value = ', '.join(as_list(bccreceivers))

    msg = None
    txtcontent = None
    if textfile:
        with codecs.open(textfile, 'rb', 'utf-8', errors='replace') as f1:
            txtcontent = f1.read()

    htmlcontent = None
    if htmlfile:
        with codecs.open(htmlfile, 'rb', 'utf-8', errors='replace') as f1:
            htmlcontent = f1.read()

    if txtcontent and htmlcontent:
        cmdline_reportlines.append('EMAIL alternative text/plain, text/html')
        msg = MIMEMultipart('alternative')
        part1 = MIMEText(txtcontent, 'plain')
        part2 = MIMEText(htmlcontent, 'html')
        msg.attach(part1)
        msg.attach(part2)
    elif txtcontent:
        cmdline_reportlines.append('EMAIL text/plain')
        msg = MIMEText(txtcontent.encode('utf-8'), 'plain', 'utf-8')
    elif htmlcontent:
        cmdline_reportlines.append('EMAIL text/html')
        msg = MIMEText(txtcontent.encode('utf-8'), 'html', 'utf-8')

    if msg:
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = sender
        msg['To'] = msg_to_value
        if msg_cc_value:
            msg['Cc'] = msg_cc_value
        if msg_bcc_value:
            msg['Bcc'] = msg_bcc_value

        cmdline_reportlines.append(u'Subject: ' + subject)
        cmdline_reportlines.append(u'From   : ' + sender)
        cmdline_reportlines.append(u'To     : ' + msg_to_value)
        cmdline_reportlines.append(u'Cc     : ' + msg_cc_value)
        cmdline_reportlines.append(u'Bcc    : ' + msg_bcc_value)

        s = smtplib.SMTP(smtp_host)
        sendmail_result = s.sendmail(sender, msg_to_value, msg.as_string())
        s.quit()
        cmdline_reportlines.append(u'result : ' + repr(sendmail_result))

    return sendmail_result

# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:

    receivers = ''

    if not email_user_do_not_send and not email_user_notify_is_turned_off:
        receivers = email_notify_about_new_build or emails_user_from_project

    if not email_user_do_not_send and email_user_to_instead:
        receivers = email_user_to_instead

    if receivers:
        send_the_mail(sender, receivers, subject=subject,
                      ccreceivers = email_user_cc,
                      bccreceivers = email_user_bcc,
                      textfile = textfile,
                      htmlfile = htmlfile,
                      smtp_host=smtp_host)

    if email_admin and email_admin_send_extra_mail:
        send_the_mail(sender, email_admin, subject=subject,
                      ccreceivers = None,
                      bccreceivers = None,
                      textfile = textfile,
                      htmlfile = htmlfile,
                      smtp_host=smtp_host)


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if 1:
    result['MILESTONES'].append({'cmdline_reportlines': cmdline_reportlines})

if exitcode == CONTINUE:
    result['MILESTONES'].append({'email_to_user_send': True})


# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)


# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
