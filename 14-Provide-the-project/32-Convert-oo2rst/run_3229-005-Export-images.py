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
import base64
import hashlib
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

masterdoc_manual_005_rst_saved_images = {}
xeq_name_cnt = 0

x = {"masterdoc_manual_html_005_as_rst":
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

    # masterdoc_manual_005_rst = lookup(milestones, 'masterdoc_manual_005_rst')
    masterdoc_manual_html_005_as_rst = lookup(milestones, 'masterdoc_manual_html_005_as_rst')
    TheProjectBuildOpenOffice2Rest = lookup(milestones, 'TheProjectBuildOpenOffice2Rest')

    if not (masterdoc_manual_html_005_as_rst and TheProjectBuildOpenOffice2Rest):
        CONTINUE = -2

if exitcode == CONTINUE:
    loglist.append('PARAMS are ok')
else:
    loglist.append('Bad PARAMS or nothing to do')


# ==================================================
# work
# --------------------------------------------------

def save_image(fname, ext, coding, data, destfolder, tabletype):
    fpath_image = None
    do_more = 1
    if do_more:
        fname = fname.strip('|')
    if not (fname and ext and coding and data):
        do_more = 0
    if do_more and coding == 'base64':
        try:
            decoded = base64.b64decode(data)
        except TypeError:
            decoded = None
            do_more = 0

    if do_more:
        fpath_image = '%s.%s' % (fname, ext)
        fpath = os.path.join(destfolder, fpath_image)
        fpath_sha1 = fpath + '.sha1.txt'

        sha1 = hashlib.sha1()
        sha1.update(decoded)
        sha1_hexdigest = sha1.hexdigest()

    if do_more:
        if os.path.exists(fpath_sha1):
            with open(fpath_sha1) as f1:
                sha1_hexdigest_old = f1.read()
        else:
            sha1_hexdigest_old = None

        if os.path.exists(fpath):
            if sha1_hexdigest == sha1_hexdigest_old:
                do_more = False

    if do_more:
        cnt = -1
        while True:
            cnt += 1
            if not os.path.exists(fpath) and not os.path.exists(fpath_sha1):
                break
            # make name unique
            tabletype_fname = '%s-%s' % (tabletype, fname)
            if cnt:
                tabletype_fname += '-%s' % cnt
            fpath_image = '%s.%s' % (tabletype_fname, ext)
            fpath = os.path.join(destfolder, fpath_image)
            fpath_sha1 = fpath + '.sha1.txt'

    if do_more:
        with open(fpath, 'wb') as f2:
            f2.write(decoded)
        with open(fpath_sha1, 'wb') as f2:
            f2.write(sha1_hexdigest)

    return fpath_image


def process_file(rstfile, tabletype):
    # x = """.. |img-1|      image:: data:image/png;base64,iVBORw0KGgoAAAANSUhE...kSuQmCC"""
    # x.split
    # ['..', '|img-1|', 'image::', 'data:image/png;base64,iVBORw0KGgoAAAANSUhE...kSuQmCC']
    tmpfile = rstfile + '.temp.rst'
    destfolder = os.path.split(tmpfile)[0]
    savedimages = []

    with open(rstfile, 'rb') as f1, \
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
                            fpath_image = save_image(parts[1], ext, coding, data, destfolder, tabletype)
                            if fpath_image:
                                line = ' '.join(parts[0:3] + [fpath_image]) + '\n'
                                savedimages.append(fpath_image)
            f2.write(line)

    if savedimages:
        os.remove(rstfile)
        shutil.move(tmpfile, rstfile)
        masterdoc_manual_html_005_as_rst[tabletype] = savedimages

    if os.path.exists(tmpfile):
        os.remove(tmpfile)

    return


if exitcode == CONTINUE:
    for i, tabletype in enumerate(masterdoc_manual_html_005_as_rst.keys()):
        rstfile = masterdoc_manual_html_005_as_rst[tabletype]['outfile']
        process_file(rstfile, tabletype)

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
