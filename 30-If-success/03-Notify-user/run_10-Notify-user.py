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

cmdline_reportlines = milestones.get('cmdline_reportlines', [])
talk = milestones.get('talk', 1)
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
    publish_dir_buildinfo = milestones_get('publish_dir_buildinfo')
    TheProjectResultBuildinfo = milestones_get('TheProjectResultBuildinfo')
    TheProjectResultBuildinfoMessage = milestones_get('TheProjectResultBuildinfoMessage')
    toolchain_name = params_get('toolchain_name')

    # test
    if not (create_buildinfo and publish_dir_buildinfo and
            TheProjectResultBuildinfo and TheProjectResultBuildinfoMessage
            and toolchain_name):
        CONTINUE = -1

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
    email_user_do_not_send = milestones_get('email_user_do_not_send', 0) # config, commandline
    loglist.append('emails are turned of in the config or on the commandline')
    if email_user_do_not_send:
        CONTINUE = -1

    email_user_notify_is_turned_off = milestones_get('email_user_notify_is_turned_off')
    loglist.append('author has turned notification about new build off')
    if email_user_do_not_send:
        CONTINUE = -1

if exitcode == CONTINUE:
    assembled = milestones_get('assembled', [])
    email_admin = milestones_get('email_admin')
    email_user_bcc = milestones_get('email_user_bcc')
    email_user_cc = milestones_get('email_user_cc')
    email_user_receivers_exlude_list = milestones_get('email_user_receivers_exlude_list')
    email_admin_send_extra_mail = milestones_get('email_admin_send_extra_mail')
    email_user_to = milestones_get('email_user_to')
    emails_user = milestones_get('emails_user')
    email_notify_about_new_build = milestones_get('email_notify_about_new_build')
    subject = milestones_get('email_user_subject')
    temp_home = tct.deepget(facts, 'tctconfig', 'general', 'temp_home')
    toochains_home = facts_get('toolchains_home')
    publish_dir_buildinfo_message = (publish_dir_buildinfo +
                                     TheProjectResultBuildinfoMessage[len(TheProjectResultBuildinfo):])

    loglist.append(('temp_home', temp_home))

if exitcode == CONTINUE:
    import codecs
    from email.Header import Header
    import smtplib
    from email.mime.text import MIMEText

    if not os.path.exists(publish_dir_buildinfo_message):
        loglist.append('file not found: publish_dir_buildinfo_message')
        exitcode = 2

if exitcode == CONTINUE:

    # body
    with codecs.open(publish_dir_buildinfo_message, 'r', 'utf-8', 'replace') as f1:
        msgbody = f1.read()

    # from
    sender = 'RenderDocumentation@typo3.org'

    # subject
    if not subject:
        subject = os.path.split(publish_dir_buildinfo_message)[1]

    if assembled:
        subject = '[' + ','.join(sorted(assembled)) + '] '+ subject

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
        if talk:
            if subject:
                cmdline_reportlines.append('subject: %s' % subject)
                if talk > 2:
                    print(subject)
            slist = []
            if msg_to_value:
                slist.append('to     : %s' % msg_to_value)
            if msg_cc_value:
                slist.append('cc: %s' % msg_cc_value)
            if msg_bcc_value:
                slist.append('bcc: %s' % msg_bcc_value)
            if slist:
                aline = ';  '.join(slist)
                cmdline_reportlines.append(aline)
                if talk > 2:
                    print(aline)
        s = smtplib.SMTP(host)
        # sendmail_result = 'simulated'
        sendmail_result = s.sendmail(sender, receivers, msg.as_string())

        loglist.append(('sendmail_result:', sendmail_result))

        quit_result = s.quit()
        loglist.append(('quit_result:', quit_result))


    def as_list(v):
        if not v:
            result = []
        elif type(v) == list:
            result = v
        elif isinstance(v, basestring):
            result = [s for s in v.replace(',', ' ').split(' ') if s]
        else:
            result = []
        return result

    #to
    receivers = []

    A = as_list(email_user_to)
    B = as_list(email_notify_about_new_build)
    C = as_list(emails_user)
    loglist.append(('A=email_user_to', A))
    loglist.append(('B=email_notify_about_new_build', B))
    loglist.append(('C=emails_user', C))

    for candidates in [A, B, C]:
        if not receivers and candidates:
            for candidate in candidates:
                if candidate not in email_user_receivers_exlude_list:
                    receivers.append(candidate)

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
    if email_admin_send_extra_mail and email_admin:
        if type(email_admin) == type([]):
            receivers = email_admin
        else:
            receivers = [email_admin]
        send_the_mail()


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
