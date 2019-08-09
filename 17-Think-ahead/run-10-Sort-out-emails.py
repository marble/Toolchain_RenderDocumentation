#!/usr/bin/env python

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
from __future__ import absolute_import
import tct
import sys

params = tct.readjson(sys.argv[1])
binabspath = sys.argv[2]
facts = tct.readjson(params['factsfile'])
milestones = tct.readjson(params['milestonesfile'])
resultfile = params['resultfile']
result = tct.readjson(resultfile)
loglist = result['loglist'] = result.get('loglist', [])
toolname = params['toolname']
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

pass

# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    requirements = [
    ]

    for requirement in requirements:
        v = milestones_get(requirement)
        if not v:
            loglist.append("'%s' not found" % requirement)
            exitcode = 22
            break

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('PROBLEMS with params')


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    email_admin = milestones_get('email_admin')
    email_admin_send_extra_mail = milestones_get('email_admin_send_extra_mail')
    email_user_bcc = milestones_get('email_user_bcc')
    email_user_cc = milestones_get('email_user_cc')
    email_user_do_not_send = milestones_get('email_user_do_not_send', 0) # config, commandline
    email_user_notify_is_turned_off = milestones_get('email_user_notify_is_turned_off', 0)
    email_user_receivers_exlude_list = milestones_get('email_user_receivers_exlude_list')
    email_user_to_instead = milestones_get('email_user_to_instead')
    emails_found_in_projects = milestones_get('emails_found_in_projects')
    emails_user_from_project = milestones_get('emails_user_from_project')

loglist.append('Now we should have some logic following')


# ==================================================
# Set MILESTONE
# --------------------------------------------------

pass

# ==================================================
# save result
# --------------------------------------------------

tct.save_the_result(result, resultfile, params, facts, exitcode, CONTINUE)


# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
