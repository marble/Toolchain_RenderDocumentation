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
errormsg = ''
helpmsg = ''

# ==================================================
# Check required milestone(s)
# --------------------------------------------------

if exitcode == CONTINUE:
    makedir = milestones.get('makedir')
    loglist.append({'makedir': makedir})
    if not makedir:
        errormsg = "Error: milestone 'makedir' not found."
        loglist.append(errormsg)
        exitcode = 2

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
        errormsg = "Error: file not found ('%s')" % f1path
        loglist.append(errormsg)
        exitcode = 1

if exitcode == CONTINUE:
    with codecs.open(f1path, 'r', 'utf-8') as f1:
        config.readfp(WithSection(f1, section))

    buildsettings = {}
    for option in config.options(section):
        buildsettings[option] = config.get(section, option)

if exitcode == CONTINUE:
    # A fix: do interpolation
    needle = '$GITDIR/'
    gitdir = buildsettings.get('gitdir', '')
    t3docdir = buildsettings.get('t3docdir', '')
    if needle in t3docdir:
        buildsettings['t3docdir'] = t3docdir.replace(needle, gitdir)
        loglist.append(toolname + ': we replaced $GITDIR in t3docdir')

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if exitcode == CONTINUE:
    result['MILESTONES'].append({'buildsettings': buildsettings})

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
