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

if exitcode == CONTINUE:
    create_buildinfo = milestones_get('create_buildinfo')
    TheProjectResultBuildinfo = milestones_get('TheProjectResultBuildinfo')
    TheProjectResultBuildinfoMessage = milestones_get('TheProjectResultBuildinfoMessage')
    toolchain_name = tct.deepget(params, 'toolchain_name')
    loglist.append(('toolchain_name', toolchain_name))

if not (create_buildinfo and TheProjectResultBuildinfo and TheProjectResultBuildinfoMessage
        and toolchain_name):
    CONTINUE = -1

if exitcode == CONTINUE:
    subject = milestones_get('email_user_subject')
    emails_user = milestones_get('emails_user')
    email_admin = tct.deepget(facts, 'tctconfig', toolchain_name, 'email_admin')
    email_user_forced = tct.deepget(facts, 'tctconfig', toolchain_name, 'email_user_forced')
    email_user_cc = tct.deepget(facts, 'tctconfig', toolchain_name, 'email_user_cc')
    email_user_bcc = tct.deepget(facts, 'tctconfig', toolchain_name, 'email_user_bcc')
    temp_home = tct.deepget(facts, 'tctconfig', 'general', 'temp_home')
    toochains_home = tct.deepget(facts, 'tctconfig', 'general', 'toolchains_home')

# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    import codecs
    import smtplib
    from email.mime.text import MIMEText

    if not os.path.exists(TheProjectResultBuildinfoMessage):
        exitcode = 2

if exitcode == CONTINUE:

    # body
    with codecs.open(TheProjectResultBuildinfoMessage, 'r', 'utf-8', 'replace') as f1:
        msgbody = f1.read()

    # from
    sender = 'Toolchain_RenderDocumentation@typo3.org'

    # subject
    if not subject:
        subject = os.path.split(TheProjectResultBuildinfoMessage)[1]

    # cc
    cclist = []
    if email_user_cc:
        for item in email_user_cc.replace(',', ' ').split(' '):
            if item and item not in cclist:
                cclist.append(item)

    # bcc
    bcclist = []
    if email_user_bcc:
        for item in email_user_bcc.replace(',', ' ').split(' '):
            if item and item not in bcclist:
                bcclist.append(item)

    def send_the_mail():
        msg = MIMEText(msgbody)

        msg['From'] = sender
        loglist.append(('sender:', sender))

        msg['To'] = ', '.join(receivers)
        loglist.append(('receivers:', receivers))

        msg['Subject'] = subject
        loglist.append(('subject:', subject))

        if cclist:
            msg['Cc'] = ', '.join(cclist)
            loglist.append(('cc:', cclist))

        if bcclist:
            msg['Bcc'] = ', '.join(bcclist)
            loglist.append(('bcc:', bcclist))

        s = smtplib.SMTP('localhost')
        sendmail_result = s.sendmail(sender, receivers, msg.as_string())
        loglist.append(('sendmail_result:', sendmail_result))

        quit_result = s.quit()
        loglist.append(('quit_result:', quit_result))

    #to
    receivers = []
    if email_user_forced:
        for item in email_user_forced.replace(',', ' ').split(' '):
            if item and item not in receivers:
                receivers.append(item)
    else:
        receivers = emails_user

    loglist.append('Now send an email!')
    send_the_mail()



# ==================================================
# Set MILESTONE
# --------------------------------------------------

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
