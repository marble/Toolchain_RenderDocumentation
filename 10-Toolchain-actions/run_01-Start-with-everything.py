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

def findRunParameter(key, default=None, D=None):
    result = firstNotNone(
        deepget(milestones, key, default=None),
        deepget(facts, 'run_command', key, default=None),
        deepget(facts, 'tctconfig', configset, key, default=None),
        default,
        None)
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
configset = ATNM['active_section']
ATNM['configset'] = configset
time_started_at_unixtime = time.time()
ATNM['time_started_at_unixtime'] = time_started_at_unixtime
time_started_at = tct.logstamp_finegrained(unixtime=time_started_at_unixtime, fmt='%Y-%m-%d %H:%M:%S %f')
ATNM['time_started_at'] = time_started_at


# ==================================================
# Set initial values (2)
# --------------------------------------------------

debug_always_make_milestones_snapshot = findRunParameter('debug_always_make_milestones_snapshot', 1, ATNM)
force_rebuild_needed = findRunParameter('force_rebuild_needed', 1, ATNM)
make_html = findRunParameter('make_html', 1, ATNM)
make_latex = findRunParameter('make_latex', 1, ATNM)
make_pdf = findRunParameter('make_pdf', 1, ATNM)
make_singlehtml = findRunParameter('make_singlehtml', 1, ATNM)
makedir = findRunParameter('makedir', None, ATNM)
rebuild_needed = findRunParameter('rebuild_needed', 1, ATNM)
replace_static_in_html = findRunParameter('replace_static_in_html', 0, ATNM)
smtp_host = findRunParameter('smtp_host', 'None', ATNM)
talk = findRunParameter('talk', 0, ATNM)


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
    loglist.append('PROBLEM with params')

if CONTINUE != 0:
    loglist.append({'CONTINUE': CONTINUE})
    loglist.append('NOTHING to do')


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    talk_builtin = 1
    talk_run_command = tct.deepget(facts, 'run_command', 'talk')
    talk_tctconfig = tct.deepget(facts, 'tctconfig', configset, 'talk')
    talk = int(talk_run_command or talk_tctconfig or talk_builtin)

if talk > 1:
    print('# --------', toolchain_name, time_started_at)


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if 'always':
    result['MILESTONES'].append(ATNM)


# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)


# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
