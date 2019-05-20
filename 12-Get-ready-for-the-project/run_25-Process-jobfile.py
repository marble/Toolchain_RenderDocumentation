#!/usr/bin/env python

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
from __future__ import absolute_import
import os
import tct
import sys

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

configset = milestones['configset']


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

def firstNotNone(*args):
    for arg in args:
        if arg is not None:
            return arg
    else:
        return None

def findRunParameterAgain(key, default, D=None, fconv=None, jobfile_data={}):
    # Oops, this function is a quick but ugly hack. But working.
    result = firstNotNone(
        deepget(facts, 'run_command', key, default=None),
        deepget(jobfile_data, 'tctconfig', key, default=None),
        deepget(facts, 'tctconfig', configset, key, default=None),
        default)
    # function convert
    if fconv is not None and result is not None:
        result = fconv(result)
    if result != default:
        if type(D) == type({}):
            D[key] = result
    return result

frpa = findRunParameterAgain
ATNM = all_the_new_milestones = {}

# ==================================================
# define
# --------------------------------------------------

buildsettings_changed = False
initial_working_dir = None
jobfile_abspath = None
jobfile_data = None
xeq_name_cnt = 0


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    buildsettings = lookup(milestones, 'buildsettings')
    if not buildsettings:
        CONTINUE = -2

if exitcode == CONTINUE:
    jobfile_abspath = lookup(milestones, 'jobfile_abspath')
    jobfile = lookup(facts, 'run_command', 'jobfile')
    initial_working_dir = lookup(facts, 'initial_working_dir')
    if not (jobfile_abspath or jobfile):
        CONTINUE = -2

if exitcode == CONTINUE:
    if not jobfile_abspath:
        if os.path.isabs(jobfile):
            jobfile_abspath = jobfile
        elif initial_working_dir:
            jobfile_abspath = os.path.abspath(os.path.join(initial_working_dir, jobfile))
        else:
            CONTINUE = -2

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('Bad PARAMS or nothing to do')

# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:

    TheProjectMakedir = lookup(milestones, 'TheProjectMakedir')
    jobfile_data = tct.readjson(jobfile_abspath)

    # ADD buildsettings we find in jobfile to the existing ones
    if 'buildsettings_sh' in jobfile_data:
        for k, v in jobfile_data.get('buildsettings_sh', {}).items():
            buildsettings[k] = v
            buildsettings_changed = True

    # ADD data we find to the existing in TheProjectMakedir/Overrides.cfg
    if 0 and TheProjectMakedir:
        if 'buildsettings_sh' in jobfile_data:
            for k, v in jobfile_data.get('buildsettings_sh', {}).items():
                buildsettings[k] = v
                buildsettings_changed = True

    if jobfile_data:

        # this is one of the rare cases where we UPDATE already existing milestones

        # we check these settings again, since we now have jobfile available
        force_rebuild_needed = frpa(
            'force_rebuild_needed', milestones.get('force_rebuild_needed'),
            ATNM, int, jobfile_data)
        make_html = frpa('make_html', milestones.get('make_html'), ATNM, int,
                         jobfile_data)
        make_latex = frpa('make_latex', milestones.get('make_latex'), ATNM,
                          int, jobfile_data)
        make_pdf = frpa('make_pdf', milestones.get('make_pdf'), ATNM, int,
                        jobfile_data)
        make_singlehtml = frpa('make_singlehtml',
            milestones.get('make_singlehtml'), ATNM, int, jobfile_data)
        oo_parser = frpa('oo_parser', milestones.get('oo_parser'), ATNM, str,
                         jobfile_data)
        rebuild_needed = frpa('rebuild_needed', milestones.get('rebuild_needed'),
                             ATNM, int, jobfile_data)
        replace_static_in_html = frpa('replace_static_in_html',
                                     milestones.get('replace_static_in_html'),
                                     ATNM, int, jobfile_data)
        talk = frpa('talk', milestones.get('talk'), ATNM, int, jobfile_data)

# ==================================================
# Set MILESTONE
# --------------------------------------------------

if ATNM:
    result['MILESTONES'].append(ATNM)

if buildsettings_changed:
    result['MILESTONES'].append({'buildsettings': buildsettings})

if jobfile_data:
    result['MILESTONES'].append({'jobfile_data': jobfile_data})

if jobfile_abspath is not None:
    result['MILESTONES'].append({'jobfile_abspath': jobfile_abspath})



# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)

# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
