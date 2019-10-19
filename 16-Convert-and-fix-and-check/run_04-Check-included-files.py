#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function
from __future__ import absolute_import

import os
import re
import sys
import tct

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

included_files_check_is_ok = 0
included_files_check_logfile = None
included_files_check_logfile_dumped_to_stdout = None
pendingFiles = {}
visitedBadFiles = {}
visitedFiles = {}
xeq_name_cnt = 0


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    disable_include_files_check = lookup(milestones,
                                         'disable_include_files_check',
                                         default=0)

    if disable_include_files_check:
        CONTINUE = -2

if exitcode == CONTINUE:
    documentation_folder = lookup(milestones, 'documentation_folder')
    masterdoc = lookup(milestones, 'masterdoc')
    OrigProject = lookup(milestones, 'OrigProject')
    OrigProjectDocroot = lookup(milestones, 'OrigProjectDocroot')
    OrigProjectMasterdoc = lookup(milestones, 'OrigProjectMasterdoc')
    TheProject = lookup(milestones, 'TheProject')
    TheProjectLog = lookup(milestones, 'TheProjectLog')
    toolfolderabspath = lookup(params, 'toolfolderabspath')
    workdir = lookup(params, 'workdir')

    if not (1
        and documentation_folder
        and masterdoc
        and OrigProject
        and OrigProjectDocroot
        and OrigProjectMasterdoc
        and TheProject
        and TheProjectLog
        and toolfolderabspath
        and workdir
    ):
        CONTINUE = -2

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('Bad PARAMS or nothing to do')

# ==================================================
# functions
# --------------------------------------------------

def rstFiles(startdir, endstr='.rst'):
    for folder, dirs, files in os.walk(startdir):
        dirs.sort()
        files.sort()
        for fname in files:
            if fname.endswith(endstr):
                yield (folder, fname)

def processRstFile(folder, fname, minimum):
    fpath = folder + "/" + fname
    if not (fpath in visitedFiles):
        error_cnt = 0
        with open(fpath, 'rb') as f1:
            f1bytes = f1.read()
        hits = re.findall('^\s*\.\.\s+(literalinclude|include)::\s*(\S+)\s*$',
                          f1bytes, flags=+re.MULTILINE)
        for hit in hits:
            include_type, incpath = hit
            if not os.path.isabs(incpath):
                incpathabs = os.path.abspath(os.path.join(folder, incpath))
                incpathabs0, incpathabs1 = os.path.split(incpathabs)
                legal = len(incpathabs0) >= minimum
                if legal:
                    if (include_type == 'include'
                        and not incpathabs in visitedFiles
                    ):
                        pendingFiles['incpathabs'] = (incpathabs0, incpathabs1)
                else:
                    error_cnt += 1
                    L = visitedBadFiles.get(fpath, [])
                    L.append(incpathabs)
                    visitedBadFiles[fpath] = L

        visitedFiles[fpath] = error_cnt

# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:

    minimum = len(TheProject)
    for folder, fname in rstFiles(TheProject):
        processRstFile(folder, fname, minimum)

    while pendingFiles:
        for k in pendingFiles:
            incabspath0, incabspath1 = pendingFiles[k]
            processRstFile(incabspath0, incabspath1, minimum)
            del pendingFiles[k]
            break

    included_files_check_is_ok = not visitedBadFiles


    visitedFilesJson = os.path.join(workdir, 'visitedFiles.json')
    temp = {}
    for k, v in visitedFiles.items():
        temp['.' + k[minimum:]] = v
    tct.writejson(temp, visitedFilesJson)

    if visitedBadFiles:

        included_files_check_logfile = os.path.join(workdir, 'visitedBadFiles.json')
        tct.writejson(visitedBadFiles, included_files_check_logfile)
        print('\n Files having bad includes:')
        for k in sorted(visitedBadFiles):
            print()
            print('.' + k[minimum:])
            print(k)
            for objectedFpath in sorted(visitedBadFiles[k]):
                print('   ', objectedFpath)
            print()

        included_files_check_logfile_dumped_to_stdout = 1



# ==================================================
# Set MILESTONE
# --------------------------------------------------

if included_files_check_is_ok:
    result['MILESTONES'].append({'included_files_check_is_ok':
                                 included_files_check_is_ok})
if included_files_check_logfile:
    result['MILESTONES'].append({'included_files_check_logfile':
                                 included_files_check_logfile})
if included_files_check_logfile_dumped_to_stdout:
    result['MILESTONES'].append({
        'included_files_check_logfile_dumped_to_stdout':
        included_files_check_logfile_dumped_to_stdout})

# ==================================================
# save result
# --------------------------------------------------

tct.save_the_result(result, resultfile, params, facts, milestones, exitcode, CONTINUE)


# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
