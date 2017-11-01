#!/usr/bin/env python

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
import os
import tct
import sys
#
import ooxhtml2rst

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

masterdoc_manual_html_004_as_rst = {}
xeq_name_cnt = 0


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    masterdoc_manual_html_003_from_tidy = lookup(milestones, 'masterdoc_manual_html_003_from_tidy')
    TheProjectBuildOpenOffice2Rest = lookup(milestones, 'TheProjectBuildOpenOffice2Rest')

    if not (masterdoc_manual_html_003_from_tidy and TheProjectBuildOpenOffice2Rest):
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

    infile = masterdoc_manual_html_003_from_tidy
    outfile = os.path.join(TheProjectBuildOpenOffice2Rest, 'manual-004.rst')

    appendlog = 0
    taginfo = 0
    tabletypes = ['t3flt', 'dl']

    for i, tablesas in enumerate(tabletypes):
        thisFiles = {}
        thisOutfile = outfile[:-3] + tablesas + '.rst'
        thisTreefile = thisOutfile + '.restparser-tree.txt'
        thisLogfile = thisOutfile + '.restparser-log.txt'

        ooxhtml2rst.main(infile, thisOutfile, thisTreefile, thisLogfile,
                         appendlog, taginfo, tablesas)

        if os.path.exists(thisOutfile):
            exitcode = 0
        else:
            exitcode = 1

        if exitcode == 0:
            if thisOutfile and os.path.exists(thisOutfile):
                thisFiles['outfile'] = thisOutfile
            if thisTreefile and os.path.exists(thisTreefile):
                thisFiles['treefile'] = thisTreefile
            if thisLogfile and os.path.exists(thisLogfile):
                thisFiles['logfile'] = thisLogfile

        if thisFiles:
            masterdoc_manual_html_004_as_rst[tablesas] = thisFiles


    if 0:
        pass
        # for each of our newly created *.rst provide a Docutils rendering
        # errorfilename = 'sxw2html-conversion-error.txt'
        # self.t3docutils_stylesheet_path
        # self.usr_bin_python
        # self.t3rst2html_script
        # self.safetempdir

        #for f2path_rst in self.rstfilepaths:
        #    normalize_empty_lines.main(f2path_rst, self.f2path_rst_temp, 2)
        #    os.remove(f2path_rst)
        #    os.rename(self.f2path_rst_temp, f2path_rst)


# ==================================================
# Set MILESTONES
# --------------------------------------------------

if masterdoc_manual_html_004_as_rst:
    result['MILESTONES'].append({'masterdoc_manual_html_004_as_rst': masterdoc_manual_html_004_as_rst})


# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)


# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
