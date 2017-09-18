#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""Deliver a completely rendered project to docs.typo3.org

Usage:

    python deliver.py  path/to/publish-params.json

"""

from __future__ import print_function
import codecs
import json
import os
import re
import shutil
import subprocess
import sys

def usage(exitcode=0):
    print(__doc__)
    sys.exit(exitcode)

def readjson(fpath):
    with codecs.open(fpath, 'r', 'utf-8', errors='replace') as f1:
        result = json.load(f1)
    return result

def version_tuple(v):
    return tuple([int(part) for part in v.split('.') if part.isdigit()])

def version_cmp(a, b):
    return cmp(version_tuple(a), version_tuple(b))

if 0:
    publish_data_example = [{
        "publish_dir": "typo3cms/extensions/blog/8.7.0",
        "publish_dir_buildinfo": "typo3cms/extensions/blog/8.7.0/_buildinfo",
        "publish_language_dir": "typo3cms/extensions/blog",
        "publish_package_file": "typo3cms/extensions/blog/packages/blog-8.7.0-default.zip",
        "publish_packages_xml_file": "typo3cms/extensions/blog/packages/packages.xml",
        "publish_project_dir": "typo3cms/extensions/blog",
        "publish_project_parent_dir": "typo3cms/extensions",
        "todo_update_stable_symlink": 1
    }]

def update_xml_file(stock, incoming, result):
    for line in file(stock):
        print(line)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        usage(0)

    hosts = {
        # naming like in ~/.ssh/config
        'srv189': {
            'HostName': 'srv189.typo3.org',
            'User': 'docsdev',
            'webroot':'/home/docsdev/www',
            'project_htaccess_file': '',
    },
        'srv123': {
            'HostName': 'srv123.typo3.org',
            'User': 'mbless',
            'webroot': '/home/mbless/public_html',
            'project_htaccess_file': '/home/mbless/scripts/config/_htaccess-2016-08.txt',
        },
    }

    host = hosts['srv123']
    user_at_domain = host['User'] + '@' + host['HostName']
    fpath = os.path.normpath(os.path.abspath(sys.argv[1]))
    srcabspart, fname = os.path.split(fpath)
    destabspart = host['webroot']

    publish_data_list = readjson(fpath)
    for publish_data in publish_data_list:
        if 0:
            for k in publish_data.keys():
                print(os.path.join(srcabspart, str(publish_data[k])))

        srcdir  = os.path.join(srcabspart , publish_data['publish_dir']).rstrip('/')
        destdir = os.path.join(destabspart, publish_data['publish_dir']).rstrip('/')

        print('#! /bin/bash')
        print('#')
        print('# ##################################################')
        print('#')
        print('# Ensure destination dir.')
        print('ssh "%s"\\\n    "mkdir -p %s"\n' % (user_at_domain, destdir))

        print('# Upload the new documentation.')
        print('rsync -av --delete\\\n    "%s/"\\\n    "%s:%s/"\n' % (srcdir, user_at_domain, destdir))


        publish_package_file = publish_data.get('publish_package_file', '')
        publish_packages_xml_file = publish_data.get('publish_packages_xml_file', '')

        print('# Do we have a new package?')
        print('# publish_package_file:', publish_package_file)
        print('# publish_packages_xml_file:', publish_packages_xml_file)

        CONTINUE = 1
        if not publish_package_file:
            CONTINUE = 0

        if CONTINUE:
            publish_package_dir, fname = os.path.split(publish_package_file)
            print('# Ensure destination package dir.')
            destdir = os.path.join(destabspart, publish_package_dir)
            print('ssh "%s"\\\n    "mkdir -p %s"\n' % (user_at_domain, destdir))

            print('# upload package.zip')
            srcfile  = os.path.join(srcabspart , publish_package_file)
            destfile = os.path.join(destabspart, publish_package_file)
            print('scp "%s"\\\n    "%s:%s"\n' % (srcfile, user_at_domain, destfile))

            print('# try to fetch existing xml file from destination')
            srcfile = os.path.join(destabspart, publish_packages_xml_file)
            destfile1  = os.path.join(srcabspart , 'packages-1.xml')
            if os.path.exists(destfile1):
                os.remove(destfile1)
            cmd = 'scp "%s:%s" "%s"' % (user_at_domain, srcfile, destfile1)
            result = subprocess.call(cmd, shell=True)
            if result:
                print("# Not successful.")
            else:
                print("# Done. Saved as 'packages-1.xml'.")

            print("# Copy new xml file alongside as 'packages-2.xml'")
            srcfile = os.path.join(srcabspart, publish_packages_xml_file)
            destfile2  = os.path.join(srcabspart , 'packages-2.xml')
            #  = 'cp  "%s"\\\n    "%s"\n' % (srcfile, destfile2))
            shutil.copy(srcfile, destfile2)

            destfile3 = os.path.join(srcabspart, 'packages-3.xml')
            if os.path.exists(destfile1):
                print('# combine')
                pyscript = "/home/marble/Repositories/mbnas/mbgit/Toolchains/RenderDocumentation/60-Publish/combine_packages_xml.py"
                # print('python \\\n    %s\\\n    %s\\\n    %s\\\n    >%s\n' % (pyscript, destfile1, destfile2, destfile3))
                cmd = '%s "%s" "%s" >"%s"' % (pyscript, destfile1, destfile2, destfile3)
                print('#', cmd)
                subprocess.call(cmd, shell=True)
            else:
                print('# No previous xml was found. Use our new one directly.')
                shutil.copy(destfile2, destfile3)

            print('# Upload the updated or new xml file.')
            destfile = os.path.join(destabspart, publish_packages_xml_file)
            print('scp "%s"\\\n    "%s:%s"\n' % (destfile3, user_at_domain, destfile))
            print()

        # .htaccess
        print('# Provide .htaccess file. We are doing this always.')
        dest_htaccess = os.path.join(destabspart, publish_data['publish_project_dir'], '.htaccess')
        print('ssh', '\\\n   ', user_at_domain, '\\\n   ', 'ln -fs', host['project_htaccess_file'],  '\\\n   ', dest_htaccess, '\n')

        # stable
        dest_project = os.path.join(destabspart, publish_data['publish_project_dir'])
        todo_update_stable_symlink = publish_data['todo_update_stable_symlink']
        print("# todo_update_stable_symlink:", todo_update_stable_symlink)

        if todo_update_stable_symlink:
            CONTINUE = 1
            print("# care about symlink 'stable'")
            dest_stable = os.path.join(destabspart, publish_data['publish_project_dir'], 'stable')
            print('#', dest_stable)


            # read existing 'stable' link
            cmd = ' '.join(['ssh', user_at_domain, 'readlink', dest_stable])
            print('#', cmd)
            try:
                existing_stable_target = subprocess.check_output(cmd, shell=True)
            except:
                existing_stable_target = ''

            existing_stable_target = existing_stable_target.strip()
            print('# existing_stable_target:', existing_stable_target)

            # find already published versions
            cmdlist = ['ssh', user_at_domain, "find", dest_project, "-maxdepth 1 -type d"]
            cmd = ' '.join(cmdlist)
            try:
                output = subprocess.check_output(cmd, shell=True)
            except subprocess.CalledProcessError:
                output = ''
            lines = [line[len(dest_project)+1:] for line in output.split('\n')]
            lines = [line for line in lines if re.match('\d+\.\d+(\.\d+)*', line)]
            lines.sort(cmp=version_cmp, reverse=True)
            highest_existing_version = lines[0] if lines else '0'
            print('# highest existing version:', highest_existing_version)

            if CONTINUE:
                if existing_stable_target and not re.match('\d+\.\d+(\.\d+)*', existing_stable_target):
                    print("# Current 'stable' does not point to numeric version.")
                    print("# Will not change that.")
                    CONTINUE = 0

            if CONTINUE:
                our_new_version = os.path.split(publish_data['publish_dir'])[1]
                print('# our new version:', our_new_version)
                if not re.match('\d+\.\d+(\.\d+)*', our_new_version):
                    print('# Is not numeric. Will not link that.')
                    CONTINUE = 0

            if CONTINUE:
                print('# our_new_version', our_new_version)
                print('# highest_existing_version', highest_existing_version)
                candidate = sorted([highest_existing_version, our_new_version], cmp=version_cmp, reverse=True)[0]
                if candidate != our_new_version:
                    print('# Existing version is higher than our new one. Nothing to do.')
                    CONTINUE = 0

            if CONTINUE:
                if candidate == existing_stable_target:
                    print('# Existing symlink is already up to date.Nothing to do.')
                    CONTINUE = 0

            if CONTINUE:
                cmdlist = ['ssh "', user_at_domain, '" "rm ', dest_stable, '" >/dev/null']
                print(''.join(cmdlist))
                cmdlist = ['ssh "', user_at_domain, '" "ln -fs ', candidate, ' ', dest_stable, '"']
                cmd = ''.join(cmdlist)
                print(cmd)
                CONTINUE = 0

            print()


        print()
        print('# ### further steps:')
        print('# ### - log to database')
