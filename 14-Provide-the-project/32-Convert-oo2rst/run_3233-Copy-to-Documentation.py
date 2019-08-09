#!/usr/bin/env python

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
from __future__ import absolute_import
import os
import tct
import sys
#
import normalize_empty_lines
import prepend_sections_with_labels
import tweak_dllisttables
import shutil

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

TheProjectDocumentation = None
TheProjectDocumentationManualFile = None
TheProjectDocumentationSaved = None
xeq_name_cnt = 0
masterdoc_manual_rst_selected = None

dummy = {"masterdoc_manual_html_005_as_rst":
     {
        "dl": {
            "outfile":
            "/home/marble/Repositories/mbnas/mbgit/Rundir/00-TEMPROOT_NOT_VERSIONED/RenderDocumentation/2017-11-15_15-01-29_607017/TheProjectBuild/OpenOffice2Rest/manual-005.dl.rst"
        },
        "t3flt": {
            "outfile":
            "/home/marble/Repositories/mbnas/mbgit/Rundir/00-TEMPROOT_NOT_VERSIONED/RenderDocumentation/2017-11-15_15-01-29_607017/TheProjectBuild/OpenOffice2Rest/manual-005.t3flt.rst"
        }
     }
    }


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')
    masterdoc_manual_html_005_as_rst = lookup(milestones, 'masterdoc_manual_html_005_as_rst')
    oo_parser = lookup(milestones, 'oo_parser', default='dl')
    TheProject = lookup(milestones, 'TheProject')
    TheProjectBuildOpenOffice2Rest = lookup(milestones, 'TheProjectBuildOpenOffice2Rest')
    if not (masterdoc_manual_html_005_as_rst and oo_parser and TheProject and TheProjectBuildOpenOffice2Rest):
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
    if masterdoc_manual_rst_selected is None:
        masterdoc_manual_rst_selected = lookup(masterdoc_manual_html_005_as_rst, oo_parser, 'outfile', default=None)
    if not masterdoc_manual_rst_selected:
        CONTINUE = -2

if exitcode == CONTINUE:
    TheProjectDocumentation = os.path.join(TheProject, 'Documentation')
    if os.path.exists(TheProjectDocumentation):
        TheProjectDocumentationSaved = os.path.join(TheProject, 'Documentation-Saved')
        shutil.move(TheProjectDocumentation, TheProjectDocumentationSaved)

    src = os.path.join(params['toolfolderabspath'], 'Documentation_default_files', 'Documentation')
    shutil.copytree(src, TheProjectDocumentation)

    TheProjectDocumentationManualFolder = os.path.join(TheProjectDocumentation, 'Manual')
    TheProjectDocumentationManualFile = os.path.join(TheProjectDocumentation, 'Manual', 'Index.rst')

    shutil.copyfile(masterdoc_manual_rst_selected, TheProjectDocumentationManualFile)

    for fname in os.listdir(TheProjectBuildOpenOffice2Rest):
        if os.path.splitext(fname)[1].lower() in ['.gif', '.png', '.jpg', '.jpeg']:
            src = os.path.join(TheProjectBuildOpenOffice2Rest, fname)
            dest = os.path.join(TheProjectDocumentationManualFolder, fname)
            shutil.copyfile(src, dest)

# ==================================================
# Set MILESTONES
# --------------------------------------------------

if TheProjectDocumentation:
    result['MILESTONES'].append({'TheProjectDocumentation': TheProjectDocumentation})

if TheProjectDocumentationManualFile:
    result['MILESTONES'].append({'TheProjectDocumentationManualFile': TheProjectDocumentationManualFile})

if TheProjectDocumentationSaved:
    result['MILESTONES'].append({'TheProjectDocumentationSaved': TheProjectDocumentationSaved})

if masterdoc_manual_rst_selected:
    result['MILESTONES'].append({'masterdoc_manual_rst_selected': masterdoc_manual_rst_selected})



# ==================================================
# save result
# --------------------------------------------------

tct.save_the_result(result, resultfile, params, facts, exitcode=exitcode, CONTINUE=CONTINUE)


# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
