#!/usr/bin/env python

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
from __future__ import absolute_import
import tct
import os
import sys
#
import codecs
import subprocess

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

deepget = tct.deepget

def lookup(D, *keys, **kwdargs):
    result = deepget(D, *keys, **kwdargs)
    loglist.append((keys, result))
    return result


# ==================================================
# define
# --------------------------------------------------

# Should we verify these do exist?

list_for_which = [
    'bzip2',
    'check_include_files.py',
    'dvips',
    'git',
    'git-restore-mtime',
    'gzip',
    'html2text',
    'latex',
    'latexmk',
    'makeindex',
    'pandoc',
    'pdflatex',
    'pip',
    'pipenv'
    'python',
    'python2',
    'python3',
    'soffice',
    'sphinx-build',
    't3xutils.phar',
    'tidy',
    'zip',
    ]

known_systemtools = {}
known_versions = {}
pip_freeze = None
xeq_name_cnt = 0

# ==================================================
# prepare for shell calls
# --------------------------------------------------

if exitcode == CONTINUE:

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

if exitcode == CONTINUE:
   for k in list_for_which:
       cmdlist = ['which', k]
       xcode, cmd, out, err = execute_cmdlist(cmdlist, cwd=workdir)
       if xcode == 0:
           known_systemtools[k] = out
       else:
           known_systemtools[k] = ''

if exitcode == CONTINUE:
   if 'pip' in known_systemtools:
    cmdlist = ['which freeze']
    xcode, cmd, out, err = execute_cmdlist(cmdlist, cwd=workdir)
    if xcode == 0:
        pip_freeze = v.split('\n')

if exitcode == CONTINUE:
    imported = False
    try:
        import t3SphinxThemeRtd
        imported = True
    except ImportError:
        pass
    if imported:
        # t3SphinxThemeRtd.VERSION # (3, 6, 14)
        # t3SphinxThemeRtd.__version__ # 3.6.14
        known_versions['t3SphinxThemeRtd.VERSION'] = t3SphinxThemeRtd.VERSION
        known_versions['t3SphinxThemeRtd.__version__'] = t3SphinxThemeRtd.__version__

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if known_systemtools:
    result['MILESTONES'].append({'known_systemtools': known_systemtools})

if known_versions:
    result['MILESTONES'].append({'known_versions': known_versions})

if pip_freeze is not None:
    result['MILESTONES'].append({'pip_freeze': pip_freeze})

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
