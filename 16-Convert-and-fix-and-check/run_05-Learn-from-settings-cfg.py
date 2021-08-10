#!/usr/bin/env python

from __future__ import print_function
from __future__ import absolute_import
import tct
import sys

params = tct.readjson(sys.argv[1])
binabspath = sys.argv[2]
facts = tct.readjson(params["factsfile"])
milestones = tct.readjson(params["milestonesfile"])
reason = ""
resultfile = params["resultfile"]
result = tct.readjson(resultfile)
loglist = result["loglist"] = result.get("loglist", [])
toolname = params["toolname"]
toolname_pure = params["toolname_pure"]
workdir = params["workdir"]
exitcode = CONTINUE = 0


# ==================================================
# Make a copy of milestones for later inspection?
# --------------------------------------------------

if 0 or milestones.get("debug_always_make_milestones_snapshot"):
    tct.make_snapshot_of_milestones(params["milestonesfile"], sys.argv[1])


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

email_notify_about_new_build = []

# in config, on commandline
email_user_do_not_send = milestones_get("email_user_do_not_send")

email_user_notify_is_turned_off = 0
email_user_notify_setting_exists = 0
settings_cfg_data = {}
xeq_name_cnt = 0


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append("CHECK PARAMS")
    settingscfg_file = milestones.get("settingscfg_file", "")
    email_user_do_not_send = milestones.get("email_user_do_not_send", 0)
    if not (settingscfg_file):
        CONTINUE = -2
        reason = "Bad PARAMS or nothing to do"


if exitcode == CONTINUE:
    loglist.append("PARAMS are ok")
else:
    loglist.append("Bad PARAMS or nothing to do")


# ==================================================
# work
# --------------------------------------------------

import codecs
import six.moves.configparser

if exitcode == CONTINUE:
    config = six.moves.configparser.RawConfigParser()
    try:
        config.readfp(codecs.open(settingscfg_file, "r", "utf-8"))
    except six.moves.configparser.ParsingError as e:
        loglist.append(("ConfigParser.ParsingError", (settingscfg_file, repr(e))))
        exitcode = 5

if exitcode == CONTINUE:
    for s in config.sections():
        settings_cfg_data[s] = settings_cfg_data.get(s, {})
        for o in config.options(s):
            settings_cfg_data[s][o] = config.get(s, o)

if exitcode == CONTINUE:
    v = tct.deepget(settings_cfg_data, "notify", "about_new_build")
    if v:
        email_user_notify_setting_exists = 1
        for email in v.split(","):
            email = email.strip()
            if email and email not in email_notify_about_new_build:
                if email == "no":
                    email_user_notify_is_turned_off = 1
                else:
                    email_notify_about_new_build.append(email)
        email_notify_about_new_build.sort()


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if settings_cfg_data:
    result["MILESTONES"].append(
        {
            "settings_cfg": settings_cfg_data,
        }
    )

if "always":
    result["MILESTONES"].append(
        {
            "email_notify_about_new_build": email_notify_about_new_build,
            "email_user_notify_is_turned_off": email_user_notify_is_turned_off,
            "email_user_notify_setting_exists": email_user_notify_setting_exists,
        }
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
