#!/usr/bin/env python

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
from __future__ import absolute_import

import codecs
import os
import shutil
import subprocess
import sys
import tct

from os.path import exists as ospe, join as ospj
from tct import deepget

params = tct.readjson(sys.argv[1])
facts = tct.readjson(params['factsfile'])
milestones = tct.readjson(params['milestonesfile'])
resultfile = params['resultfile']
result = tct.readjson(resultfile)
toolname = params['toolname']
toolname_pure = params['toolname_pure']
toolchain_name = facts['toolchain_name']
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
    result = deepget(D, *keys, **kwdargs)
    loglist.append((keys, result))
    return result


# ==================================================
# define
# --------------------------------------------------

TheProjectMakedir = None
TheProjectMakedirThemes = None
xeq_name_cnt = 0


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    makedir = lookup(milestones, 'makedir')
    TheProject = lookup(milestones, 'TheProject')

    if not (1
            and makedir
            and TheProject):
        CONTINUE = -2

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('Bad PARAMS or nothing to do')


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    def cmdline(cmd, cwd=None):
        if cwd is None:
            cwd = os.getcwd()
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,
            cwd=cwd)
        bstdout, bstderr = process.communicate()
        exitcode2 = process.returncode
        return exitcode2, cmd, bstdout, bstderr

    def execute_cmdlist(cmdlist, cwd=None):
        global xeq_name_cnt
        exitcode, out, err = 88, None, None

        cmd = ' '.join(cmdlist)
        cmd_multiline = ' \\\n   '.join(cmdlist) + '\n'

        xeq_name_cnt += 1
        filename_cmd = 'xeq-%s-%d-%s.txt' % (toolname_pure, xeq_name_cnt, 'cmd')
        filename_err = 'xeq-%s-%d-%s.txt' % (toolname_pure, xeq_name_cnt, 'err')
        filename_out = 'xeq-%s-%d-%s.txt' % (toolname_pure, xeq_name_cnt, 'out')

        with codecs.open(ospj(workdir, filename_cmd), 'w', 'utf-8') as f2:
            f2.write(cmd_multiline.decode('utf-8', 'replace'))

        if (0
            and milestones.get('activateLocalSphinxDebugging')
            and cmdlist[0] == 'sphinx-build'
            and 1):
                from sphinx.cmd.build import main as sphinx_cmd_build_main
                exitcode = sphinx_cmd_build_main(cmdlist[1:])
        else:
            exitcode, cmd, out, err = cmdline(cmd, cwd=cwd)

        loglist.append({'exitcode': exitcode, 'cmd': cmd, 'out': out,
                        'err': err})

        if out:
            with codecs.open(ospj(workdir, filename_out), 'w', 'utf-8') as f2:
                f2.write(out.decode('utf-8', 'replace'))

        if err:
            with codecs.open(ospj(workdir, filename_err), 'w', 'utf-8') as f2:
                f2.write(err.decode('utf-8', 'replace'))

        return exitcode, cmd, out, err


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    TheProjectMakedir = TheProject + 'Makedir'
    cmdlist = [
        # run rsync
        'rsync',
        # in archive mode, that is equivalent to -rlptgoD
        '-a',
        # but we want to resolve symlinks
        # -L, --copy-links When symlinks are encountered, the item that they
        # point to (the referent) is copied, rather than the symlink.
        '-L',
        # Exclude SYMLINK_THE_PROJECT and similar that may exist
        '--exclude', '"SYMLINK_*"',
        # srcdir - slash at the end!
        makedir.rstrip('/') + '/',
        # destdir - slash at the end!
        TheProjectMakedir + '/'
    ]

    exitcode, cmd, out, err = execute_cmdlist(cmdlist, cwd=workdir)

if exitcode == CONTINUE:
    srcthemes = '/THEMES'
    if not ospe(srcthemes):
        loglist.append((srcthemes, 'does not exist. No themes to copy.'))
        CONTINUE = -2

if exitcode == CONTINUE:
    destthemes = TheProjectMakedir + '/_themes'
    if ospe(destthemes):
        loglist.append((destthemes, 'exists. I will not copy', srcthemes, 'because that may overwrite existing'))
        CONTINUE = -2

if exitcode == CONTINUE:
    cmdlist = [
        # run rsync
        'rsync',
        # in archive mode, that is equivalent to -rlptgoD
        '-a',
        # but we want to resolve symlinks
        # -L, --copy-links When symlinks are encountered, the item that they
        # point to (the referent) is copied, rather than the symlink.
        '-L',
        # srcdir - slash at the end!
        srcthemes.rstrip('/') + '/',
        # destdir - slash at the end!
        destthemes.rstrip('/') + '/',
    ]

    exitcode, cmd, out, err = execute_cmdlist(cmdlist, cwd=workdir)

if exitcode == CONTINUE:
    TheProjectMakedirThemes = destthemes



# ==================================================
# Set MILESTONE
# --------------------------------------------------

if TheProjectMakedir:
    result['MILESTONES'].append({'TheProjectMakedir': TheProjectMakedir})

if TheProjectMakedirThemes:
    result['MILESTONES'].append({'TheProjectMakedirThemes':
                                 TheProjectMakedirThemes})


# ==================================================
# save result
# --------------------------------------------------

tct.save_the_result(result, resultfile, params, facts, milestones, exitcode, CONTINUE)


# ==================================================
# Return with proper exitcode
# --------------------------------------------------
sys.exit(exitcode)
