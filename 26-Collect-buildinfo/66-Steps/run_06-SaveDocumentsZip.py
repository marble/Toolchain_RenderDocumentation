#!/usr/bin/env python
# coding: utf-8

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
import os
import tct
import sys

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

deepget = tct.deepget

def lookup(D, *keys, **kwdargs):
    result = deepget(D, *keys, **kwdargs)
    loglist.append((keys, result))
    return result


# ==================================================
# define
# --------------------------------------------------

TheProjectResultBuildinfoDocumentationGenerated = None
DocumentationGeneratedZipFile = None
xeq_name_cnt = 0


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    TheProject = lookup(milestones, 'TheProject')
    TheProjectDocumentation = lookup(milestones, 'TheProjectDocumentation')
    TheProjectBuildOpenOffice2Rest = lookup(milestones, 'TheProjectBuildOpenOffice2Rest')
    TheProjectResultBuildinfo = lookup(milestones, 'TheProjectResultBuildinfo')
    zip_systemtool = (lookup(milestones, 'known_systemtools', 'zip') or '').strip()

    if not (TheProject and TheProjectResultBuildinfo and
            TheProjectBuildOpenOffice2Rest and TheProjectDocumentation
            and zip_systemtool):
        CONTINUE = -2

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('Nothing to do for these params')


# =========================================================
# how to start a subprocess with perfect logging
# ---------------------------------------------------------

### ATTENTION: Is specific here

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

if exitcode == CONTINUE:
    DocumentationGeneratedZipFile = 'Documentation.zip.GENERATED.zip'
    TheProjectResultBuildinfoDocumentationGenerated = os.path.join(TheProjectResultBuildinfo, DocumentationGeneratedZipFile)

    exitcode_, cmd, out, err = execute_cmdlist(
        [
            zip_systemtool, '-r',
            TheProjectResultBuildinfoDocumentationGenerated,
            TheProjectDocumentation[len(TheProject):].lstrip('/')
        ],
        cwd = TheProject)

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if TheProjectResultBuildinfoDocumentationGenerated:
    result['MILESTONES'].append({
        'TheProjectResultBuildinfoDocumentationGenerated':
        TheProjectDocumentation})

if DocumentationGeneratedZipFile:
    result['MILESTONES'].append({'DocumentationGeneratedZipFile':DocumentationGeneratedZipFile})



# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)


# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
