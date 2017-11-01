#!/usr/bin/env python

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
import os
import tct
import sys
#
import normalize_empty_lines
import prepend_sections_with_labels
import tweak_dllisttables

params = tct.readjson(sys.argv[1])
binabspath = sys.argv[2]
facts = tct.readjson(params['factsfile'])
milestones = tct.readjson(params['milestonesfile'])
resultfile = params['resultfile']
result = tct.readjson(resultfile)
loglist = result['loglist'] = result.get('loglist', [])
toolname = params['toolname']
toolname_pure = params['toolname_pure']
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

masterdoc_manual_004_selected = None
masterdoc_manual_005_rst = None
xeq_name_cnt = 0


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')
    masterdoc_manual_004_selected = lookup(milestones, 'masterdoc_manual_html_004_as_rst', 'dl', 'outfile')
    TheProjectBuildOpenOffice2Rest = lookup(milestones, 'TheProjectBuildOpenOffice2Rest')

    if not (masterdoc_manual_004_selected and TheProjectBuildOpenOffice2Rest):
        CONTINUE = -2

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('Bad PARAMS or nothing to do')


# =========================================================
# how to start a subprocess with perfect logging
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

# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    masterdoc_manual_005_rst = os.path.join(TheProjectBuildOpenOffice2Rest, 'manual-005.rst')

    if exitcode == CONTINUE:
        normalize_empty_lines.main(masterdoc_manual_004_selected, masterdoc_manual_005_rst, 2)

    if exitcode == CONTINUE:
        prepend_sections_with_labels.processRstFile(masterdoc_manual_005_rst)

    if exitcode == CONTINUE:
        tweak_dllisttables.processRstFile(masterdoc_manual_005_rst)

    if exitcode == CONTINUE:
        with open(masterdoc_manual_005_rst, 'rb') as f1:
            data = f1.read()
        data = data.replace('.. .. include:: ./FIXME/Includes.txt', '.. include:: ../Includes.txt')
        with open(masterdoc_manual_005_rst, 'wb') as f2:
            f2.write(data)

# ==================================================
# Set MILESTONES
# --------------------------------------------------

if masterdoc_manual_004_selected:
    result['MILESTONES'].append({'masterdoc_manual_004_selected': masterdoc_manual_004_selected})
if masterdoc_manual_005_rst:
    result['MILESTONES'].append({'masterdoc_manual_005_rst': masterdoc_manual_005_rst})



# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)


# ==================================================
# Return with proper exitcode
# --------------------------------------------------


sys.exit(exitcode)
