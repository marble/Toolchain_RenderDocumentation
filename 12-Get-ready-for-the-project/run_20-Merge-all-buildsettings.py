#!/usr/bin/env python

from __future__ import print_function
from __future__ import absolute_import

import codecs
import os
import six.moves.configparser
import sys
import tct

from tct import deepget

params = tct.readjson(sys.argv[1])
facts = tct.readjson(params['factsfile'])
milestones = tct.readjson(params['milestonesfile'])
reason = ''
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
# Helper functions (1)
# --------------------------------------------------

def firstNotNone(*args):
    for arg in args:
        if arg is not None:
            return arg
    else:
        return None

def lookup(D, *keys, **kwdargs):
    result = deepget(D, *keys, **kwdargs)
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
buildsettings_from_run_command = {}
buildsettings_from_jobfile = {}
buildsettings_initial = {}
xeq_name_cnt = 0


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    makedir = lookup(milestones, 'makedir')
    if not makedir:
        CONTINUE = -2

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('Bad PARAMS or nothing to do')


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    buildsettings_from_jobfile = lookup(milestones, 'jobfile_data',
                                        'buildsettings_sh', default={})

if exitcode == CONTINUE:
    # read Makedir/buildsettings.sh

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
    config = six.moves.configparser.RawConfigParser()
    f1path = os.path.join(makedir, 'buildsettings.sh')
    if not os.path.exists(f1path):
        f1path = None
    if f1path:
        with codecs.open(f1path, 'r', 'utf-8') as f1:
            config.readfp(WithSection(f1, section))

        for option in config.options(section):
            buildsettings_initial[option] = config.get(section, option)

if exitcode == CONTINUE:

    allkeys = set()
    allkeys = allkeys.union(set(buildsettings_default.keys()))
    allkeys = allkeys.union(set(buildsettings_from_jobfile.keys()))
    allkeys = allkeys.union(set(buildsettings_from_run_command.keys()))
    allkeys = allkeys.union(set(buildsettings_initial.keys()))

    for k in allkeys:
        # if we have already agreed on something
        a = lookup(milestones, 'buildsettings', k, default=None)
        # if given on the commandline - preferred method
        b = lookup(facts, 'run_command', k, default=None)
        # if given on the commandline - deprecated method
        c = params.get(k, None)
        # jobfile_data
        d = lookup(milestones, 'jobfile_data', 'buildsettings_sh', k,
                   default=None)
        # from Makedir/buildsettings.sh
        e = buildsettings_initial.get(k)
        # defaults defined above
        f = buildsettings_default.get(k)
        # desperation default
        g = None

        buildsettings[k] = firstNotNone(a, b, c, d, e, f, g)

if exitcode == CONTINUE:

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


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if buildsettings:
    # this is the final merge of all buildsettings
    result['MILESTONES'].append({'buildsettings': buildsettings})

if buildsettings_from_run_command:
    # from the commandline
    result['MILESTONES'].append({'buildsettings_from_run_command':
                                 buildsettings_from_run_command})

if buildsettings_from_jobfile:
    # from milestones/jobfile_data/buildsettings_sh
    pass

if buildsettings_initial:
    # from $MAKEDIR/buildsettings.sh
    result['MILESTONES'].append({'buildsettings_initial': buildsettings_initial})

if buildsettings_default:
    # hardcoded above
    result['MILESTONES'].append({'buildsettings_default':
                                 buildsettings_default})


# ==================================================
# save result
# --------------------------------------------------

tct.save_the_result(result, resultfile, params, facts, milestones, exitcode, CONTINUE, reason)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
