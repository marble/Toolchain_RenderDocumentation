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
toolname_pure = params['toolname_pure']
workdir = params['workdir']
loglist = result['loglist'] = result.get('loglist', [])
exitcode = CONTINUE = 0

# ==================================================
# define
# --------------------------------------------------

xeq_name_cnt = 0

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

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')
    giturl = tct.deepget(milestones, 'buildsettings', 'giturl')
    gitdir = tct.deepget(milestones, 'buildsettings', 'gitdir')
    gitbranch = tct.deepget(milestones, 'buildsettings', 'gitbranch')
    loglist.append(('giturl', giturl))
    loglist.append(('gitdir', gitdir))
    loglist.append(('gitbranch', gitbranch))
    if not giturl:
        CONTINUE = -1

# ==================================================
# work
# --------------------------------------------------

import codecs
import os
import subprocess


if exitcode == CONTINUE:

    def cmdline(cmd, cwd=None):
        global xeq_name_cnt
        if cwd is None:
            cwd = os.getcwd()
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=cwd)
        out, err = process.communicate()
        exitcode = process.returncode
        loglist.append({'exitcode': exitcode, 'cmd': cmd, 'out': out, 'err': err})
        xeq_name_cnt += 1
        filename_cmd = 'xeq-%s-%d-%s.txt' % (toolname_pure, xeq_name_cnt, 'cmd')
        filename_err = 'xeq-%s-%d-%s.txt' % (toolname_pure, xeq_name_cnt, 'err')
        filename_out = 'xeq-%s-%d-%s.txt' % (toolname_pure, xeq_name_cnt, 'out')
        with codecs.open(os.path.join(workdir, filename_cmd), 'w', 'utf-8') as f2:
            f2.write(cmd.decode('utf-8', 'replace'))
        with codecs.open(os.path.join(workdir, filename_out), 'w', 'utf-8') as f2:
            f2.write(out.decode('utf-8', 'replace'))
        with codecs.open(os.path.join(workdir, filename_err), 'w', 'utf-8') as f2:
            f2.write(err.decode('utf-8', 'replace'))
        return exitcode, cmd, out, err


    if exitcode == CONTINUE:
        exitcode, cmd, out, err = cmdline('git reset --hard', cwd=gitdir)

    if exitcode == CONTINUE:
        exitcode, cmd, out, err = cmdline('git checkout ' + gitbranch, cwd=gitdir)

    if exitcode == CONTINUE:
        exitcode, cmd, out, err = cmdline('git pull', cwd=gitdir)


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if exitcode == CONTINUE:
    result['MILESTONES'].append({'git_pull_done': 1})

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
