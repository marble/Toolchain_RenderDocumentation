#!/usr/bin/env python

from __future__ import print_function
from __future__ import absolute_import

import os
import shutil
import sys
import tct

from os.path import exists as ospe, join as ospj
from tct import deepget

params = tct.readjson(sys.argv[1])
binabspath = sys.argv[2]
facts = tct.readjson(params['factsfile'])
milestones = tct.readjson(params['milestonesfile'])
reason = ''
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
    result = deepget(D, *keys, **kwdargs)
    loglist.append((keys, result))
    return result


# ==================================================
# define
# --------------------------------------------------

publish_package = None
publish_dir_package = None
xeq_name_cnt = 0


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    build_package = lookup(milestones, 'build_package')
    package_file = lookup(milestones, 'package_file')
    package_name = lookup(milestones, 'package_name')
    resultdir = lookup(milestones, 'resultdir')

    if not(1
            and build_package
            and package_file
            and package_name
            and resultdir
    ):
        CONTINUE = -2
        reason = 'Bad PARAMS or nothing to do'

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('Bad PARAMS or nothing to do')


# ==================================================
# work
# --------------------------------------------------

if exitcode == CONTINUE:
    publish_dir_package = ospj(resultdir, 'Result', 'package')
    if not ospe(publish_dir_package):
        os.makedirs(publish_dir_package)
    publish_package = ospj(publish_dir_package, package_name)
    shutil.copy2(package_file, publish_package)


# ==================================================
# Set MILESTONE
# --------------------------------------------------

if publish_package:
    result['MILESTONES'].append({'publish_package': publish_package})

if publish_dir_package:
    result['MILESTONES'].append({'publish_dir_package': publish_dir_package})



# ==================================================
# save result
# --------------------------------------------------

tct.save_the_result(result, resultfile, params, facts, milestones, exitcode, CONTINUE, reason)


# ==================================================
# Return with proper exitcode
# --------------------------------------------------

sys.exit(exitcode)
