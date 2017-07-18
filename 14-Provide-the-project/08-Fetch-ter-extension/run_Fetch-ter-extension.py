#!/usr/bin/env python

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
import tct
import sys

params = tct.readjson(sys.argv[1])
binabspath = sys.argv[2]
facts = tct.readjson(params['factsfile'])
milestones = tct.readjson(params['milestonesfile'])
resultfile = params['resultfile']
result = tct.readjson(resultfile)
loglist = result['loglist'] = result.get('loglist', [])
toolname = params["toolname"]
toolname_pure = params['toolname_pure']
toolchain_name = facts['toolchain_name']
workdir = params['workdir']
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

buildsettings = {}
extension_file = ''
extension_file_abspath = ''
extensions_rootfolder = None
gitbranch = ''
gitdir = ''
gitdir_unpacked = ''
giturl = ''
ter_extkey = ''
ter_extversion = ''
xeq_name_cnt = 0


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    configset = lookup(milestones, 'configset')
    # required milestones
    requirements = ['configset']

    # just test
    for requirement in requirements:
        v = lookup(milestones, requirement)
        if not v:
            loglist.append("'%s' not found" % requirement)
            exitcode = 22

    # fetch
    buildsettings = lookup(milestones, 'buildsettings')
    if not buildsettings:
        exitcode = 22

if exitcode == CONTINUE:

    # fetch #1
    gitbranch = lookup(milestones, 'buildsettings', 'gitbranch')
    gitdir = lookup(milestones, 'buildsettings', 'gitdir')
    giturl = lookup(milestones, 'buildsettings', 'giturl')
    ter_extkey = lookup(milestones, 'buildsettings', 'ter_extkey')
    ter_extversion = lookup(milestones, 'buildsettings', 'ter_extversion')

    # fetch #2
    extensions_rootfolder = lookup(facts, 'tctconfig', configset, 'extensions_rootfolder')

    # test
    if not (ter_extkey and ter_extversion):
        loglist.append('For a TER extension we need the key and the version.')
        CONTINUE = -2

if exitcode == CONTINUE:
    if not gitdir and not extensions_rootfolder:
        CONTINUE = -2

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

import codecs
import os
import shutil
import subprocess

if exitcode == CONTINUE:

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
        exitcode, cmd, out, err = cmdline(cmd, cwd=workdir)
        loglist.append({'exitcode': exitcode, 'cmd': cmd, 'out': out, 'err': err})
        xeq_name_cnt += 1
        filename_cmd = 'xeq-%s-%d-%s.txt' % (toolname_pure, xeq_name_cnt, 'cmd')
        filename_err = 'xeq-%s-%d-%s.txt' % (toolname_pure, xeq_name_cnt, 'err')
        filename_out = 'xeq-%s-%d-%s.txt' % (toolname_pure, xeq_name_cnt, 'out')

        with codecs.open(os.path.join(workdir, filename_cmd), 'w', 'utf-8') as f2:
            f2.write(cmd_multiline.decode('utf-8', 'replace'))

        with codecs.open(os.path.join(workdir, filename_out), 'w', 'utf-8') as f2:
            f2.write(out.decode('utf-8', 'replace'))

        with codecs.open(os.path.join(workdir, filename_err), 'w', 'utf-8') as f2:
            f2.write(err.decode('utf-8', 'replace'))

        return exitcode, cmd, out, err


if exitcode == CONTINUE:
    foldername = ter_extkey + '_' + ter_extversion
    foldername = foldername.replace('*', '').replace('?', '')
    if not foldername:
        loglist.append('illegal extension specification')
        exitcode = 22

if exitcode == CONTINUE:
    gitdir = os.path.join(extensions_rootfolder, foldername)
    if os.path.exists(gitdir):
        shutil.rmtree(gitdir)
    gitdir_unpacked = os.path.join(gitdir, 'unpacked')
    os.makedirs(gitdir_unpacked)

if exitcode == CONTINUE:
    exitcode, cmd, out, err = execute_cmdlist([
        't3xutils.phar', 'fetch', '--use-curl', ter_extkey, ter_extversion, gitdir])

if exitcode == CONTINUE:
    extension_file = ''
    for name in os.listdir(gitdir):
        if name.startswith(ter_extkey):
            extension_file = name
            break

    if extension_file:
        extension_file_abspath = os.path.join(gitdir, extension_file)

    if not extension_file_abspath:
        exit = 2

if exitcode == CONTINUE:
    exitcode, cmd, out, err = execute_cmdlist([
        't3xutils.phar', 'extract', extension_file_abspath, gitdir_unpacked])

if exitcode == CONTINUE:
    buildsettings['gitdir'] = gitdir_unpacked

# ==================================================
# Set MILESTONE
# --------------------------------------------------


D = {}

if extension_file:
    D['extension_file'] = extension_file

if extension_file_abspath:
    D['extension_file_abspath'] = extension_file_abspath

if buildsettings:
    D['buildsettings'] = buildsettings

if D:
    result['MILESTONES'].append(D)


# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------


sys.exit(exitcode)
