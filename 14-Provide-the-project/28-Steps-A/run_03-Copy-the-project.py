#!/usr/bin/env python

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
from __future__ import absolute_import
import os
import tct
import sys
from os.path import join as ospj, exists as ospe

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

TheProject = None
xeq_name_cnt = 0

# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')
    workdir_home = lookup(params, 'workdir_home')
    masterdocs_initial = lookup(milestones, 'masterdocs_initial')
    gitdir = lookup(milestones, 'buildsettings', 'gitdir')
    if not (workdir_home and masterdocs_initial and gitdir):
        exitcode = 22

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('PROBLEMS with params')

if CONTINUE != 0:
    loglist.append({'CONTINUE': CONTINUE})
    loglist.append('NOTHING to do')

# ==================================================
# we want to call the shell
# --------------------------------------------------

if exitcode == CONTINUE:
    import codecs
    import subprocess

    def cmdline(cmd, cwd=None):
        if cwd is None:
            cwd = os.getcwd()
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=cwd)
        out, err = process.communicate()
        exitcode = process.returncode
        return exitcode, cmd, out, err

    def execute_cmdlist(cmdlist, cwd=None):
        global xeq_name_cnt
        cmd = ' '.join(cmdlist)
        cmd_multiline = ' \\\n   '.join(cmdlist) + '\n'

        xeq_name_cnt += 1
        filename_cmd = 'xeq-%s-%d-%s.txt' % (toolname_pure, xeq_name_cnt, 'cmd')
        filename_err = 'xeq-%s-%d-%s.txt' % (toolname_pure, xeq_name_cnt, 'err')
        filename_out = 'xeq-%s-%d-%s.txt' % (toolname_pure, xeq_name_cnt, 'out')

        with codecs.open(os.path.join(workdir, filename_cmd), 'w', 'utf-8') as f2:
            f2.write(cmd_multiline.decode('utf-8', 'replace'))

        exitcode, cmd, out, err = cmdline(cmd, cwd=cwd)

        loglist.append({'exitcode': exitcode, 'cmd': cmd, 'out': out, 'err': err})

        with codecs.open(os.path.join(workdir, filename_out), 'w', 'utf-8') as f2:
            f2.write(out.decode('utf-8', 'replace'))

        with codecs.open(os.path.join(workdir, filename_err), 'w', 'utf-8') as f2:
            f2.write(err.decode('utf-8', 'replace'))

        return exitcode, cmd, out, err

# ==================================================
# work
# --------------------------------------------------

from shutil import copytree, copyfile

if exitcode == CONTINUE:
    TheProject = os.path.join(workdir_home, 'TheProject')
    if os.path.exists(TheProject):
        loglist.append("TheProject already exists: %s" % TheProject)
        exitcode = 22

if exitcode == CONTINUE:
    os.mkdir(TheProject)

if exitcode == CONTINUE:

    if 0 and "simple copy, no rsync":
        # This works, but does not copy the timestamps of the file.
        # So we are better switching to rsync.
        # copy files of the top level and ./doc/ and ./Documentation is existing
        for top, dirs, files in os.walk(gitdir):
            for afile in files:
                copyfile(os.path.join(top, afile), os.path.join(TheProject, afile))
            for adir in dirs:
                if adir in ['doc', 'Documentation']:
                    copytree(os.path.join(top, adir), os.path.join(TheProject, adir))
            break

    if 1 and "better use rsync":
        # copy files of the top level and ./doc/ and ./Documentation is existing
        # be safe
        src = gitdir.replace('\\', '/').rstrip('/')
        dest = TheProject.replace('\\', '/').rstrip('/')
        cmdlist=['rsync', '%s/*' % src, '%s/' % dest]
        exitcode, cmd, out, err = execute_cmdlist(cmdlist, cwd=workdir)
        for adir in ['doc', 'Documentation']:
            srcdir = os.path.join(src, adir)
            destdir = os.path.join(dest, adir)
            if os.path.exists(srcdir):
                cmdlist = ['rsync', '-a', '--delete', '%s/' % srcdir, '%s/' % destdir]
                exitcode, cmd, out, err = execute_cmdlist(cmdlist, cwd=workdir)


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if exitcode == CONTINUE:
    result['MILESTONES'].append({'TheProject': TheProject})

# ==================================================
# save result
# --------------------------------------------------

tct.save_the_result(result, resultfile, params, facts, exitcode=exitcode, CONTINUE=CONTINUE)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
