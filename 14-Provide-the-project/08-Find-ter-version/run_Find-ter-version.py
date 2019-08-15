#!/usr/bin/env python

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
from __future__ import absolute_import
import tct
import sys
#
import codecs
import os
import subprocess


params = tct.readjson(sys.argv[1])
binabspath = sys.argv[2]
facts = tct.readjson(params['factsfile'])
milestones = tct.readjson(params['milestonesfile'])
resultfile = params['resultfile']
result = tct.readjson(resultfile)
loglist = result['loglist'] = result.get('loglist', [])
toolname = params['toolname']
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

buildsettings_changed = False
ter_extversion_highest = None
xeq_name_cnt = 0


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    configset = lookup(milestones, 'configset')
    buildsettings = lookup(milestones, 'buildsettings')
    ter_extkey = lookup(milestones, 'buildsettings', 'ter_extkey')
    if not (configset and buildsettings and ter_extkey):
        CONTINUE = -2

if exitcode == CONTINUE:
    ter_extversion = lookup(milestones, 'buildsettings', 'ter_extversion')
    if ter_extversion:
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


if exitcode == CONTINUE:
    exitcode, cmd, out, err = execute_cmdlist([
        't3xutils.phar', 'info', ter_extkey])

if exitcode == CONTINUE:
    example = """
Available versions:
 0.1.0    uploaded: 19.04.2013 16:05:26
 0.2.0    uploaded: 27.04.2013 11:42:13
 0.3.0    uploaded: 10.05.2013 13:45:01
 0.4.0    uploaded: 28.05.2013 11:51:38
 0.5.0    uploaded: 04.06.2013 16:39:00
 0.6.0    uploaded: 18.06.2013 09:10:45
 1.0.0    uploaded: 05.07.2013 10:33:43
 1.1.0    uploaded: 09.08.2013 19:43:04
 1.1.1    uploaded: 24.08.2013 15:47:11
 1.2.0    uploaded: 22.09.2013 18:54:58
 1.2.1    uploaded: 23.09.2013 14:22:14
 1.2.2    uploaded: 15.10.2013 23:23:41
 1.3.0    uploaded: 05.01.2014 19:25:18
 1.3.1    uploaded: 16.01.2014 22:16:20
 1.3.2    uploaded: 16.03.2014 17:25:00
 2.0.0    uploaded: 07.04.2014 17:41:53
 2.0.1    uploaded: 20.04.2014 10:07:55
 2.1.0    uploaded: 05.06.2014 11:36:53
 2.2.0    uploaded: 04.12.2014 17:01:28
 2.2.1    uploaded: 03.03.2015 17:25:23
 2.2.2    uploaded: 17.03.2015 16:04:30
 2.2.3    uploaded: 11.04.2015 11:39:46
 2.3.0    uploaded: 18.08.2015 15:38:46
 2.3.1    uploaded: 10.11.2015 13:43:53
 2.4.0    uploaded: 03.10.2016 08:52:54
 2.5.0    uploaded: 08.01.2017 11:16:36
 2.5.1    uploaded: 05.05.2017 12:12:21
"""
    for line in out.split('\n'):
        parts = line.split()
        # ['0.1.0', 'uploaded:', '19.04.2013', '16:05:26']
        if len(parts) != 4:
            continue
        if parts[1] != 'uploaded:':
            continue
        version = parts[0].split('.')
        if len(version) != 3:
            continue
        try:
            version = [int(item) for item in version]
        except ValueError:
            continue
        if ter_extversion_highest is None:
            ter_extversion_highest = version
        else:
            ter_extversion_highest = max(ter_extversion_highest, version)

    if ter_extversion_highest:
        buildsettings['ter_extversion'] = '.'.join([str(item) for item in ter_extversion_highest])
        if buildsettings['version'] in ['', '0.0.0']:
            buildsettings['version'] = buildsettings['ter_extversion']
        parts = buildsettings['builddir'].split('/')
        if parts:
            if parts[-1] in ['', '0.0.0']:
                parts[-1] = buildsettings['ter_extversion']
            buildsettings['builddir'] = '/'.join(parts)
        buildsettings_changed = True

# ==================================================
# Set MILESTONE
# --------------------------------------------------


D = {}

if buildsettings_changed:
    D['buildsettings'] = buildsettings

if ter_extversion_highest:
    D['ter_extversion_highest'] = ter_extversion_highest

if D:
    result['MILESTONES'].append(D)


# ==================================================
# save result
# --------------------------------------------------

tct.save_the_result(result, resultfile, params, facts, milestones, exitcode, CONTINUE)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------


sys.exit(exitcode)
