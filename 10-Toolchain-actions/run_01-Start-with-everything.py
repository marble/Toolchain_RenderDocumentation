#!/usr/bin/env python

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
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

def findRunParameter(key, default=None, D=None, fconv=None):
    result = firstNotNone(
        deepget(milestones, key, default=None),
        deepget(facts, 'run_command', key, default=None),
        # too bad that 'jobfile_data' isn't available at this point
        deepget(milestones, 'jobfile_data', 'tctconfig', key, default=None),
        deepget(facts, 'tctconfig', configset, key, default=None),
        default,
        None)
    # function convert
    if fconv is not None:
        result = fconv(result)
    if type(D) == type({}):
        D[key] = result
    return result

ATNM = all_the_new_milestones = {}


# ==================================================
# Set initial values (1)
# --------------------------------------------------
import time

# configset = deepget(facts, 'run_command', 'configset', default='default')
ATNM['active_section'] = (milestones.get('active_section')
                  or deepget(facts, 'active_section', default='default'))

# too bad we used both names:
configset = ATNM['active_section']
ATNM['configset'] = configset

time_started_at_unixtime = time.time()
ATNM['time_started_at_unixtime'] = time_started_at_unixtime
time_started_at = tct.logstamp_finegrained(unixtime=time_started_at_unixtime, fmt='%Y-%m-%d %H:%M:%S %f')
ATNM['time_started_at'] = time_started_at


# ==================================================
# Set initial values (2)
# --------------------------------------------------

debug_always_make_milestones_snapshot = findRunParameter('debug_always_make_milestones_snapshot', 1, ATNM, int)
force_rebuild_needed = findRunParameter('force_rebuild_needed', 1, ATNM, int)
make_html = findRunParameter('make_html', 1, ATNM, int)
make_latex = findRunParameter('make_latex', 1, ATNM, int)
make_pdf = findRunParameter('make_pdf', 1, ATNM, int)
make_singlehtml = findRunParameter('make_singlehtml', 1, ATNM, int)
makedir = findRunParameter('makedir', None, ATNM)
rebuild_needed = findRunParameter('rebuild_needed', 1, ATNM, int)
replace_static_in_html = findRunParameter('replace_static_in_html', 0, ATNM, int)
smtp_host = findRunParameter('smtp_host', 'None', ATNM)
talk = findRunParameter('talk', 0, ATNM, int)


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')
    if not configset:
        exitcode = 22

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('Bad PARAMS or nothing to do')


# ==================================================
# work
# --------------------------------------------------

if talk > 1:
    print('# --------', toolchain_name, time_started_at)


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if 'ATNM - All The New Milestones':
    result['MILESTONES'].append(ATNM)


# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)


# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
