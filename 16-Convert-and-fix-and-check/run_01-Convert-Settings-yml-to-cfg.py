#!/usr/bin/env python

from __future__ import print_function
from __future__ import absolute_import
import codecs
import copy
import six.moves.configparser
import sys
import tct
import yaml

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

has_settingscfg = None
has_settingscfg_generated = None
settingscfg_file = None


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append("CHECK PARAMS")

    # fetch
    settingsyml_file = milestones.get("settingsyml_file", "")
    settingscfg_file = milestones.get("settingscfg_file", "")
    if settingscfg_file:
        reason = "Nothing to do. Settings.cfg exists."
        loglist.append(reason)
        CONTINUE = -2

if exitcode == CONTINUE:
    if not settingsyml_file:
        reason = "Settings.yml not found"
        loglist.append(reason)
        CONTINUE = -2

if exitcode == CONTINUE:
    loglist.append("PARAMS are ok")
else:
    loglist.append("Bad PARAMS or nothing to do")


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:

    config = six.moves.configparser.RawConfigParser()

    settingsyml = None
    settingsyml_file = milestones["settingsyml_file"]
    with codecs.open(settingsyml_file, "r", "utf-8") as f1:
        reason = ""
        try:
            settingsyml = yaml.safe_load(f1)
        except yaml.parser.ParserError:
            settingsyml = None
            reason = "yaml.parser.ParserError"
        except yaml.scanner.ScannerError:
            settingsyml = None
            reason = "yaml.scanner.ScannerError"
        except:
            settingsyml = None
            reason = "unexpected exception"
    if settingsyml is None:
        loglist.append(
            (
                "error: cannot parse `settingsyml_file`",
                settingsyml_file,
                "reason:",
                reason,
            )
        )
        exitcode = 22

if exitcode == CONTINUE:
    loglist.append({"settingsyml": copy.deepcopy(settingsyml)})
    confpy = settingsyml["conf.py"]

    section = "general"
    config.add_section(section)
    cnt = 0
    for key, value in sorted(confpy.items()):
        if isinstance(value, (dict, list)):
            pass
        else:
            if key.startswith("latex_"):
                # we saw problems with these
                continue
            cnt += 1
            config.set(section, key, value)
            del confpy[key]

    section = "html_theme_options"
    config.add_section(section)
    config.set(section, "github_branch", "")
    config.set(section, "github_commit_hash", "")
    config.set(section, "github_repository", "")
    config.set(section, "path_to_documentation_dir", "")
    config.set(section, "github_revision_msg", "")
    config.set(section, "github_sphinx_locale", "")
    config.set(section, "project_contact", "")
    config.set(section, "project_discussions", "")
    config.set(section, "project_home", "")
    config.set(section, "project_issues", "")
    config.set(section, "project_repository", "")
    config.set(section, "use_opensearch", "")

    section = "intersphinx_mapping"
    config.add_section(section)
    im = confpy.get("intersphinx_mapping")
    if im:
        for key, value in sorted(im.items()):
            config.set(section, key, value[0])
        del confpy["intersphinx_mapping"]

    section = "extensions"
    extensions = confpy.get("extensions")
    if extensions:
        config.add_section(section)
        for i, extension in enumerate(sorted(extensions)):
            config.set(section, "ext_%02d" % i, extension)
        del confpy["extensions"]

    section = "extlinks"
    extlinks = confpy.get("extlinks")
    if extlinks:
        config.add_section(section)
        for key, value in sorted(extlinks.items()):
            config.set(section, key, "%s | %s" % (value[0], value[1]))
        del confpy["extlinks"]

    # todo: handle 'latex_documents'
    # No, it turns out it's better to leave them out.

    for section in ["latex_elements", "texinfo_documents", "man_pages"]:
        items = confpy.get(section)
        if items:
            config.add_section(section)
            for key, value in sorted(items.items()):
                config.set(section, key, value)
            del confpy[section]

    loglist.append({"UNCONVERTED_REST": copy.deepcopy(settingsyml)})
    settingscfg_file = settingsyml_file[:-4] + ".cfg"
    with codecs.open(settingscfg_file, "w") as configfile:
        config.write(configfile)

        configfile.write(
            """\

# About Settings.cfg

# normal:
# https://github.com/marble/typo3-docs-typo3-org-resources/blob/master/TemplatesForCopying/ExampleFiles/Settings-minimal.cfg

# extensive:
# https://github.com/marble/typo3-docs-typo3-org-resources/blob/master/TemplatesForCopying/ExampleFiles/Settings-extensive.cfg

# Example files:
# https://github.com/marble/typo3-docs-typo3-org-resources/tree/master/TemplatesForCopying/ExampleFiles

# More:
# http://mbless.de/blog/2015/10/24/a-new-task-for-an-old-server.html#ini-files
"""
        )

if exitcode == CONTINUE:
    has_settingscfg = True
    has_settingscfg_generated = True

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if has_settingscfg is not None:
    result["MILESTONES"].append({"has_settingscfg": has_settingscfg})

if has_settingscfg_generated is not None:
    result["MILESTONES"].append(
        {"has_settingscfg_generated": has_settingscfg_generated}
    )

if settingscfg_file is not None:
    result["MILESTONES"].append({"settingscfg_file": settingscfg_file})


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
