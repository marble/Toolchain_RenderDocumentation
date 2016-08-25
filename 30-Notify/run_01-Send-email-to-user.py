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
# define
# --------------------------------------------------

email_user_send_extra_mail_to_admin = False

# ==================================================
# Check required milestone(s)
# --------------------------------------------------

def milestones_get(name, default=None):
    result = milestones.get(name, default)
    loglist.append((name, result))
    return result

def params_get(name, default=None):
    result = params.get(name, default)
    loglist.append((name, result))
    return result

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')
    create_buildinfo = milestones_get('create_buildinfo')
    TheProjectResultBuildinfo = milestones_get('TheProjectResultBuildinfo')
    TheProjectResultBuildinfoMessage = milestones_get('TheProjectResultBuildinfoMessage')
    publish_dir_buildinfo = milestones_get('publish_dir_buildinfo')
    toolchain_name = params_get('toolchain_name')

if exitcode == CONTINUE:
    if not (create_buildinfo and TheProjectResultBuildinfo and TheProjectResultBuildinfoMessage
            and publish_dir_buildinfo and toolchain_name):
        exitcode = 2

if exitcode == CONTINUE:
    subject = milestones_get('email_user_subject')
    emails_user = milestones_get('emails_user')
    email_admin = (tct.deepget(facts, 'run_command', 'email_admin') or
                     tct.deepget(facts, 'tctconfig', toolchain_name, 'email_admin'))
    email_user_to = (tct.deepget(facts, 'run_command', 'email_user_to') or
                     tct.deepget(facts, 'tctconfig', toolchain_name, 'email_user_to'))
    email_user_cc = (tct.deepget(facts, 'run_command', 'email_user_cc') or
                     tct.deepget(facts, 'tctconfig', toolchain_name, 'email_user_cc'))
    email_user_bcc = (tct.deepget(facts, 'run_command', 'email_user_bcc') or
                      tct.deepget(facts, 'tctconfig', toolchain_name, 'email_user_bcc'))
    email_user_send_extra_mail_to_admin = (tct.deepget(facts, 'run_command', 'email_user_send_extra_mail_to_admin') or
                      tct.deepget(facts, 'tctconfig', toolchain_name, 'email_user_send_extra_mail_to_admin'))
    temp_home = tct.deepget(facts, 'tctconfig', 'general', 'temp_home')
    toochains_home = tct.deepget(facts, 'tctconfig', 'general', 'toolchains_home')

    publish_dir_buildinfo_message = (publish_dir_buildinfo +
                                     TheProjectResultBuildinfoMessage[len(TheProjectResultBuildinfo):])

# ==================================================
# work
# --------------------------------------------------


if exitcode == CONTINUE:
    import codecs
    from email.Header import Header
    import smtplib
    from email.mime.text import MIMEText


    if not os.path.exists(publish_dir_buildinfo_message):
        exitcode = 2

if exitcode == CONTINUE:

    # body
    with codecs.open(publish_dir_buildinfo_message, 'r', 'utf-8', 'replace') as f1:
        msgbody = f1.read()

    # from
    sender = 'Toolchain_RenderDocumentation@typo3.org'

    # subject
    if not subject:
        subject = os.path.split(publish_dir_buildinfo_message)[1]

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

    # host
    host = 'localhost'

    def send_the_mail():

        # todo: bugfix!
        # see http://mg.pov.lt/blog/unicode-emails-in-python.html

        msg_to_value = ', '.join(receivers) if receivers else ''
        msg_cc_value = ', '.join(cclist) if cclist else ''
        msg_bcc_value = ', '.join(bcclist) if bcclist else ''
        loglist.append(('actual mailparams', {
            'from': sender,
            'host': host,
            'msg_bcc_value': msg_bcc_value,
            'msg_cc_value': msg_cc_value,
            'msg_to_value': msg_to_value,
            'subject': subject,
        }))

        msg = MIMEText(msgbody.encode('utf-8'), 'plain', 'utf-8')
        msg['From'] = sender
        msg['To'] = msg_to_value
        msg['Subject'] = Header(subject, 'utf-8')
        if msg_cc_value:
            msg['Cc'] = msg_cc_value
        if msg_bcc_value:
            msg['Bcc'] = msg_bcc_value
        s = smtplib.SMTP(host)
        sendmail_result = s.sendmail(sender, receivers, msg.as_string())
        loglist.append(('sendmail_result:', sendmail_result))

        quit_result = s.quit()
        loglist.append(('quit_result:', quit_result))

    #to
    receivers = []
    email_user_receivers_exlude_list = ['documentation@typo3.org']
    if email_user_to:
        for item in email_user_to.replace(',', ' ').split(' '):
            if item not in email_user_receivers_exlude_list:
                if item and item not in receivers:
                    receivers.append(item)
    else:
        receivers = emails_user

    if receivers:
        loglist.append('Now send an email!')
        send_the_mail()
    else:
        loglist.append('There is no primary receiver we could notify by mail')
        if cclist:
            loglist.append('Send to cclist')
            receivers = cclist
            send_the_mail()
        elif bcclist:
            loglist.append('Send to bcclist')
            receivers = bcclist
            send_the_mail()
    if email_user_send_extra_mail_to_admin and email_admin:
        if type(email_admin) == type([]):
            receivers = email_admin
        else:
            receivers = [email_admin]
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
