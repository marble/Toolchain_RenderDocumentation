#!/usr/bin/env python

# ==================================================
# open
# --------------------------------------------------

from __future__ import print_function
import os
import tct
import sys
#
import base64
import re
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

masterdoc_manual_005_rst_saved_images = []
xeq_name_cnt = 0


# ==================================================
# Check params
# --------------------------------------------------

if exitcode == CONTINUE:
    loglist.append('CHECK PARAMS')

    masterdoc_manual_005_rst = lookup(milestones, 'masterdoc_manual_005_rst')
    TheProjectBuildOpenOffice2Rest = lookup(milestones, 'TheProjectBuildOpenOffice2Rest')

    if not (masterdoc_manual_005_rst and TheProjectBuildOpenOffice2Rest):
        CONTINUE = -2

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('Bad PARAMS or nothing to do')


# ==================================================
# work
# --------------------------------------------------

def save_image(fname, ext, coding, data, destfolder):
    fpath_image = None
    proceed = 1
    if proceed:
        fname = fname.strip('|')
    if not (fname and ext and coding and data):
        proceed = 0
    if proceed and coding == 'base64':
        try:
            decoded = base64.b64decode(data)
        except TypeError:
            decoded = None
            proceed = 0
    if proceed:
        fpath_image = '%s.%s' % (fname, ext)
        with file(os.path.join(destfolder, fpath_image), 'wb') as f2:
            f2.write(decoded)
    return fpath_image


if exitcode == CONTINUE:
    # x = """.. |img-1|      image:: data:image/png;base64,iVBORw0KGgoAAAANSUhE...kSuQmCC"""
    # x.split
    # ['..', '|img-1|', 'image::', 'data:image/png;base64,iVBORw0KGgoAAAANSUhE...kSuQmCC']

    tmpfile = masterdoc_manual_005_rst + '.temp.rst'
    destfolder = os.path.split(tmpfile)[0]

    with open(masterdoc_manual_005_rst, 'rb') as f1, \
        open(tmpfile, 'wb') as f2:
        for line in f1:
            if line.startswith('.. |'):
                parts = line.split()
                if len(parts) == 4:
                    if parts[1].endswith('|') and parts[2] == 'image::':
                        m = re.match('^data:image/(?P<ext>[a-z]+);(?P<coding>\w+),(?P<data>.+)$', parts[3])
                        if m:
                            ext = m.groupdict()['ext']
                            coding = m.groupdict()['coding']
                            data = m.groupdict()['data']
                            fpath_image = save_image(parts[1], ext, coding, data, destfolder)
                            if fpath_image:
                                line = ' '.join(parts[0:3] + [fpath_image]) + '\n'
                                masterdoc_manual_005_rst_saved_images.append(fpath_image)
            f2.write(line)

    if masterdoc_manual_005_rst_saved_images:
        os.remove(masterdoc_manual_005_rst)
        shutil.move(tmpfile, masterdoc_manual_005_rst)

    if os.path.exists(tmpfile):
        os.remove(tmpfile)

# ==================================================
# Set MILESTONES
# --------------------------------------------------

if masterdoc_manual_005_rst_saved_images:
    result['MILESTONES'].append(
        {'masterdoc_manual_005_rst_saved_images':
         masterdoc_manual_005_rst_saved_images})

# ==================================================
# save result
# --------------------------------------------------

tct.writejson(result, resultfile)


# ==================================================
# Return with proper exitcode
# --------------------------------------------------


sys.exit(exitcode)
