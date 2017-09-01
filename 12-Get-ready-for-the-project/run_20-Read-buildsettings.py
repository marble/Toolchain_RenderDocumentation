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
toolname = params['toolname']
loglist = result['loglist'] = result.get('loglist', [])
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

# TER_EXTENSION = 0 | 1
# TER_EXTKEY = tt_news
# TER_EXTVERSION = 1.2.3
# LOCALIZATION=
# LOCALIZATION=en_US
# LOCALIZATION=fr_FR

buildsettings = {}
buildsettings_default = {
    "builddir": "",
    "gitbranch": "",
    "gitdir": "",
    "giturl": "",
    "localization": "",
    "logdir": "",
    "masterdoc": "",
    "package_key": "",
    "package_language": "default",
    "package_zip": 0,
    "project": "",
    "t3docdir": "",
    "ter_extension": 0,
    "ter_extkey": "",
    "ter_extversion": "",
    "version": ""
  }
buildsettings_initial = {}
xeq_name_cnt = 0
buildsettings_from_run_command = {}


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    # required milestones
    requirements = []

    # just test
    for requirement in requirements:
        v = lookup(milestones, requirement)
        if not v:
            loglist.append("'%s' not found" % requirement)
            exitcode = 22

    # fetch
    makedir = lookup(milestones, 'makedir')

    # test
    if not makedir:
        exitcode = 22

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('PROBLEM with required params')

if CONTINUE != 0:
    loglist.append({'CONTINUE': CONTINUE})
    loglist.append('NOTHING to do')


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:

    import codecs
    import ConfigParser

    class WithSection:

        def __init__(self, fp, sectionname):
            self.fp = fp
            self.sectionname = sectionname
            self.prepend = True

        def readline(self):
            if self.prepend:
                self.prepend = False
                return '[' + self.sectionname + ']\n'
            else:
                return self.fp.readline()

    # ConfigParser needs a section. Let's invent one.
    section = 'build'
    config = ConfigParser.RawConfigParser()
    f1path = os.path.join(makedir, 'buildsettings.sh')
    if not os.path.exists(f1path):
        loglist.append(('buildsettings.sh not found', f1path))
        f1path = None

if exitcode == CONTINUE:
    if f1path:
        with codecs.open(f1path, 'r', 'utf-8') as f1:
            config.readfp(WithSection(f1, section))

        for option in config.options(section):
            buildsettings_initial[option] = config.get(section, option)

    for k in buildsettings_initial.keys():
        # copy what we have found in the file buildsettings.sh
        buildsettings[k] = buildsettings_initial[k]

    # all keys
    for k in buildsettings_default.keys():
        # set on the commandline?
        if not params.get(k) is None:
            buildsettings[k] = params[k]
        elif buildsettings.get(k) is None:
            buildsettings[k] = buildsettings_default[k]

    # A fix: do some interpolation

    needle = '$GITDIR/'
    gitdir = buildsettings.get('gitdir', '')
    t3docdir = buildsettings.get('t3docdir', '')
    if needle in t3docdir:
        buildsettings['t3docdir'] = t3docdir.replace(needle, gitdir)

    needle = '$VERSION'
    version = buildsettings.get('version', '')
    builddir = buildsettings.get('builddir', '')
    if needle in builddir:
        buildsettings['builddir'] = builddir.replace(needle, version)



    for k in buildsettings.keys():
        v = lookup(facts, 'run_command', k, default=None)
        if v is not None:
            buildsettings[k] = v
            buildsettings_from_run_command[k] = v



# ==================================================
# Set MILESTONE
# --------------------------------------------------

if buildsettings:
    # we modifiy the values of 'buildsettings' in the course of the process
    result['MILESTONES'].append({'buildsettings': buildsettings})

if buildsettings_initial:
    # what we have read
    result['MILESTONES'].append({'buildsettings_initial': buildsettings_initial})

if buildsettings_default:
    # defaults we may have supplemented
    result['MILESTONES'].append({'buildsettings_default': buildsettings_default})

if buildsettings_from_run_command:
    # defaults we may have supplemented
    result['MILESTONES'].append({'buildsettings_from_run_command': buildsettings_from_run_command})


# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
