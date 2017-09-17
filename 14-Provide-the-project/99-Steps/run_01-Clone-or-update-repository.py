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
toolname_pure = params['toolname_pure']
workdir = params['workdir']
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

gitbranch = ''
gitdir = ''
giturl = ''
do_clone_or_pull = ''
gitdir_must_start_with = ''
xeq_name_cnt = 0


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    gitdir = lookup(milestones, 'buildsettings', 'gitdir')
    if not gitdir :
        exitcode = 22

if exitcode == CONTINUE:
    gitdir_is_ready_for_use = lookup(milestones, 'buildsettings', 'gitdir_is_ready_for_use')
    if gitdir_is_ready_for_use:
        CONTINUE = -2

if exitcode == CONTINUE:
    giturl = lookup(milestones, 'buildsettings', 'giturl')
    gitbranch = lookup(milestones, 'buildsettings', 'gitbranch')
    if not (giturl and gitbranch):
        CONTINUE = -2

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('Bad PARAMS or nothing to do')


# =========================================================
# work Example of how to start a subprocess with perfect logging
# ---------------------------------------------------------

if exitcode == CONTINUE:

    import codecs
    import os
    import subprocess

    def cmdline(cmd, cwd=None):
        if cwd is None:
            cwd = os.getcwd()
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=cwd)
        out, err = process.communicate()
        exitcode = process.returncode
        return exitcode, cmd, out, err

    def execute_cmdlist(cmdlist):
        global xeq_name_cnt
        cmd = ' '.join(cmdlist)
        cmd_multiline = ' \\\n   '.join(cmdlist) + '\n'

        xeq_name_cnt += 1
        filename_cmd = 'xeq-%s-%d-%s.txt' % (toolname_pure, xeq_name_cnt, 'cmd')
        filename_err = 'xeq-%s-%d-%s.txt' % (toolname_pure, xeq_name_cnt, 'err')
        filename_out = 'xeq-%s-%d-%s.txt' % (toolname_pure, xeq_name_cnt, 'out')

        with codecs.open(os.path.join(workdir, filename_cmd), 'w', 'utf-8') as f2:
            f2.write(cmd_multiline.decode('utf-8', 'replace'))

        exitcode, cmd, out, err = cmdline(cmd, cwd=workdir)
        loglist.append({'exitcode': exitcode, 'cmd': cmd, 'out': out, 'err': err})

        with codecs.open(os.path.join(workdir, filename_out), 'w', 'utf-8') as f2:
            f2.write(out.decode('utf-8', 'replace'))

        with codecs.open(os.path.join(workdir, filename_err), 'w', 'utf-8') as f2:
            f2.write(err.decode('utf-8', 'replace'))

        return exitcode, cmd, out, err


if 0:
    builder = 'dummy'
    warnings_file = 'dummy.txt'
    sourcedir = 'dummy'
    outdir = 'dummy'
    cmdlist = [
        'sphinx-build-dummy',
        '-a',                  # write all files; default is to only write new and changed files
        '-b ' + builder,       # builder to use; default is html
        '-E',                  # don't use a saved environment, always read all files
        '-w ' + warnings_file, # write warnings (and errors) to given file
        sourcedir,
        outdir
    ]

    exitcode, cmd, out, err = execute_cmdlist(cmdlist)

# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    if os.path.exists(gitdir):
        do_clone_or_pull = 'pull'
    else:
        do_clone_or_pull = 'clone'
        gitdir_must_start_with = lookup(milestones, 'gitdir_must_start_with')
        if not gitdir_must_start_with:
            exitcode = 22

if exitcode == CONTINUE:
    if do_clone_or_pull == 'clone':
        for item in gitdir_must_start_with.split(':'):
            if gitdir.startswith(item):
                break
        else:
            CONTINUE = -1
            loglist.append(('need to clone, but gitdir does not start with one of gitdir_must_start_with',
                            gitdir))

# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:

    import codecs
    import os
    import subprocess


    if do_clone_or_pull == 'clone':
        parent_dir = os.path.split(gitdir)[0]
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir, mode=0775)

        exitcode, cmd, out, err = cmdline('git clone %s %s' % (giturl, gitdir))

        if exitcode == CONTINUE:
            exitcode, cmd, out, err = cmdline('git checkout ' + gitbranch, cwd=gitdir)

    if exitcode == CONTINUE:
        if do_clone_or_pull == 'pull':

            if exitcode == CONTINUE:
                exitcode, cmd, out, err = cmdline('git fetch', cwd=gitdir)

            if exitcode == CONTINUE:
                exitcode, cmd, out, err = cmdline('git reset --hard', cwd=gitdir)

            if exitcode == CONTINUE:
                exitcode, cmd, out, err = cmdline('git checkout ' + gitbranch, cwd=gitdir)

            if exitcode == CONTINUE:
                exitcode, cmd, out, err = cmdline('git pull', cwd=gitdir)


# ==================================================
# Set MILESTONE
# --------------------------------------------------

D = {}

if do_clone_or_pull == 'clone':
    D['git_clone_done'] = 1

if do_clone_or_pull == 'pull':
    D['git_pull_done'] = 1

result['MILESTONES'].append(D)


# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
