#!/usr/bin/env python

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
# Get and check required milestone(s)
# --------------------------------------------------
def milestones_get(name, default=None):
    result = milestones.get(name, default)
    loglist.append((name, result))
    return result

if exitcode == CONTINUE:
    requirements = [
    ]

    for requirement in requirements:
        v = milestones_get(requirement)
        if not v:
            loglist.append("'%s' not found" % requirement)
            exitcode = 2
            break

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('PROBLEMS with params')

if exitcode == CONTINUE:
    email_admin = milestones_get('email_admin')
    email_user_bcc = milestones_get('email_user_bcc')
    email_user_cc = milestones_get('email_user_cc')
    email_user_do_not_send = milestones_get('email_user_do_not_send')
    email_user_receivers_exlude_list = milestones_get('email_user_receivers_exlude_list')
    email_user_send_extra_mail_to_admin = milestones_get('email_user_send_extra_mail_to_admin')
    email_user_to = milestones_get('email_user_do_not_send')
    emails_found = milestones_get('emails_found')
    emails_user = milestones_get('emails_user')


# ==================================================
# work
# --------------------------------------------------

loglist.append('Now let some logic follow')

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if 0:
    result['MILESTONES'].append({0: 0})

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)

example = {
    "email_admin": "martin.bless@gmail.com",
    "email_user_bcc": "martin.bless@gmail.com",
    "email_user_cc": "martin.bless@typo3.org",
    "email_user_do_not_send": 0,
    "email_user_receivers_exlude_list": [
        "documentation@typo3.org",
        "kasperYYYY@typo3.com",
        "kasperYYYY@typo3.org",
        "info@typo3.org"
    ],
    "email_user_send_extra_mail_to_admin": 0,
    "email_user_to": "martin.bless@gmail.com",
    "emails_found": [
        [
            "Documentation/Index.rst",
            [
                "xavier@causal.ch"
            ]
        ],
        [
            "ext_emconf.php",
            [
                "xavier@causal.ch"
            ]
        ]
    ],
    "emails_user": [
        "xavier@causal.ch"
    ],}
