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
    buildsettings = milestones.get('buildsettings')
    loglist.append({'makedir': makedir})
    loglist.append({'buildsettings': buildsettings})
    if not buildsettings:
        errormsg = "Error: milestone 'buildsettings' not found."
        loglist.append(errormsg)
        exitcode = 2

# ==================================================
# work
# --------------------------------------------------

import os
import subprocess

giturl = buildsettings['giturl']
gitdir = buildsettings['gitdir']
gitbranch = buildsettings['gitbranch']

if exitcode == CONTINUE:

    if not giturl:
        loglist.append('Ok, giturl is not given. Assuming gitdir is ready for use.')

if exitcode == CONTINUE:
    if giturl:
        if not os.path.isdir(gitdir):
            errormsg = "Error: Cannot find gitdir ('%s')" % gitdir
            loglist.append(errormsg)
            exitcode = 2

        if exitcode == CONTINUE:
            if not os.path.isdir(os.path.join(gitdir, '.git')):
                errormsg = 'Error: No GIT repository. gitdir/.git not found.'
                loglist.append(errormsg)
                exitcode = 2

        if exitcode == CONTINUE:
            def cmdline(cmd, cwd=gitdir):
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=cwd)
                out, err = process.communicate()
                exitcode = process.returncode
                loglist.append([exitcode, cmd, out, err])
                return exitcode

        if exitcode == CONTINUE:
            exitcode = cmdline('git reset --hard')

        if exitcode == CONTINUE:
            exitcode = cmdline('git checkout ' + gitbranch)

        if exitcode == CONTINUE:
            exitcode = cmdline('git pull')



# ==================================================
# save result
# --------------------------------------------------


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if exitcode == CONTINUE:
    result['MILESTONES'].append({'gitdir_ready': 1})

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
