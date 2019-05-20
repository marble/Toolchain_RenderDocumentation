#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""Integrate two files known as 'packages.xml'.

Usage:
    python combine_packages_xml.py FPATH_1 FPATH_2 >result.xml

Description:
    The script reads FPATH_1 and updates the data with FPATH_2.
    Entries are sorted by 'version+language'. The file timestamp
    is set to 'now'. The result is printed to stdout.
"""

from __future__ import print_function
from __future__ import absolute_import
import codecs
import datetime
import re
import sys
import time

if not __name__ == "__main__":
    print('Please run as main.')
    sys.exit(1)

def usage(exitcode=0):
    print(__doc__)
    sys.exit(exitcode)

def usage1(exitcode=1):
    lines = __doc__.split('\n')
    print('\n'.join(lines[2:4] + ['    Try --help']))
    sys.exit(exitcode)

if len(sys.argv) == 1 or '--help' in sys.argv:
    usage()

if len(sys.argv) != 3:
    usage1()

fpath1 = sys.argv[1]
fpath2 = sys.argv[2]

unixtime = int(time.time())
dt = datetime.datetime.fromtimestamp(unixtime)
datetimestr = dt.strftime('%Y-%m-%d %H:%M:%S')

example_data = """
<?xml version="1.0" standalone="yes" ?>
<documentationPackIndex>
	<meta>
		<timestamp>1493982096</timestamp>
		<date>2017-05-05 13:01:36</date>
	</meta>
	<languagePackIndex>
		<languagepack version="0.4.0" language="default">
			<md5>7c5890efa98d8184f2004a5d219bb57b</md5>
		</languagepack>
		<languagepack version="0.5.0" language="default">
			<md5>cad89b3359498d070e75247b9e974eb2</md5>
		</languagepack>
		<languagepack version="0.6.0" language="default">
			<md5>fd8f805fef1bdf748de32e430ccd08d6</md5>
		</languagepack>
		<languagepack version="1.0.0" language="default">
			<md5>c98885a6a82329c48d35ba1be06c62c2</md5>
		</languagepack>
		<languagepack version="1.1.0" language="default">
			<md5>8a20f8337c2dd3cadeeab46544826177</md5>
		</languagepack>
		<languagepack version="1.1.0" language="fr_FR">
			<md5>2725397412083343c57bad8a706257cf</md5>
		</languagepack>
		<languagepack version="1.1.1" language="default">
			<md5>567f4fa8883766acf58ad529bd28f165</md5>
		</languagepack>
		<languagepack version="1.1.1" language="fr_FR">
			<md5>20fd95af62d5bee7bab4b20e20752923</md5>
		</languagepack>
		<languagepack version="1.2.0" language="default">
			<md5>d82077b4e25ebd4d3ff2d6568006310c</md5>
		</languagepack>
		<languagepack version="1.2.0" language="fr_FR">
			<md5>a2fecd2e4a43e7103dca6a7800990519</md5>
		</languagepack>
		<languagepack version="1.2.1" language="default">
			<md5>9c0d59e8ca0224417f4cc50d1137b989</md5>
		</languagepack>
		<languagepack version="1.2.1" language="fr_FR">
			<md5>7b64db2f3632f15639c5c1b0b6853962</md5>
		</languagepack>
		<languagepack version="1.2.2" language="default">
			<md5>5b269fc51aab30596267e40f65494ab3</md5>
		</languagepack>
		<languagepack version="1.2.2" language="fr_FR">
			<md5>12cc312274ccc74836218a4a1c4fe367</md5>
		</languagepack>
		<languagepack version="1.3.0" language="default">
			<md5>1b9ff0511b50f89220efa4dae402d7f2</md5>
		</languagepack>
		<languagepack version="1.3.0" language="fr_FR">
			<md5>6ce32d8a414aaeabfa706483e7799b46</md5>
		</languagepack>
		<languagepack version="1.3.1" language="default">
			<md5>13079fb01792655184bf71650938b308</md5>
		</languagepack>
		<languagepack version="1.3.1" language="fr_FR">
			<md5>4edf4b024b394135152bd204bfaff2f5</md5>
		</languagepack>
		<languagepack version="1.3.2" language="default">
			<md5>c6338fb4fc2e5178184cf6ad65eefcfe</md5>
		</languagepack>
		<languagepack version="1.3.2" language="fr_FR">
			<md5>6a8ed5d22a808487a8217844f5b0c500</md5>
		</languagepack>
		<languagepack version="2.0.0" language="default">
			<md5>1d079e747c8b2f4c0b589712c13427be</md5>
		</languagepack>
		<languagepack version="2.0.0" language="fr_FR">
			<md5>c3cf49cfdc8a0e29d10832a4344e91e7</md5>
		</languagepack>
		<languagepack version="2.0.1" language="default">
			<md5>76abdd02fa068e8074815b36d8e460d3</md5>
		</languagepack>
		<languagepack version="2.0.1" language="fr_FR">
			<md5>4bf4dcda2a6e74d34479503543137ad5</md5>
		</languagepack>
		<languagepack version="2.1.0" language="default">
			<md5>f08a233da48eacb10c47922805afd249</md5>
		</languagepack>
		<languagepack version="2.1.0" language="fr_FR">
			<md5>6584398fcc9e7f5a546722da5a103d26</md5>
		</languagepack>
		<languagepack version="2.2.0" language="default">
			<md5>b982d16982626a60d0afd175a42b8938</md5>
		</languagepack>
		<languagepack version="2.2.0" language="fr_FR">
			<md5>7333f623ee0452401d653818c1e5a8de</md5>
		</languagepack>
		<languagepack version="2.2.1" language="default">
			<md5>15c025915b4106418dabdb19ef67d24b</md5>
		</languagepack>
		<languagepack version="2.2.1" language="fr_FR">
			<md5>d4160de05bde35f2217558b57adba429</md5>
		</languagepack>
		<languagepack version="2.2.2" language="default">
			<md5>9af5abd5ebf7278bcc456ccc1cc23b63</md5>
		</languagepack>
		<languagepack version="2.2.2" language="fr_FR">
			<md5>3609e8f2052ff03d27eabfd52991b9f8</md5>
		</languagepack>
		<languagepack version="2.2.3" language="default">
			<md5>fe6d78a9e3deed8ff43f9424dd3272f7</md5>
		</languagepack>
		<languagepack version="2.2.3" language="fr_FR">
			<md5>f39b898bf9efedfbbf8b670e7ce7bb88</md5>
		</languagepack>
		<languagepack version="2.3.0" language="default">
			<md5>d4f85ecaf4f6a0c83cfcf5e68dcd7a0f</md5>
		</languagepack>
		<languagepack version="2.3.0" language="fr_FR">
			<md5>37428948f560597acf8ed45fdfb3da98</md5>
		</languagepack>
		<languagepack version="2.3.1" language="default">
			<md5>152b3e2f0645fd2e8c9c08fcc2e8862b</md5>
		</languagepack>
		<languagepack version="2.3.1" language="fr_FR">
			<md5>c36846d36aea5225e54260892eccc24b</md5>
		</languagepack>
		<languagepack version="2.4.0" language="default">
			<md5>e7db74af568ddc646ee6e7388dbbe110</md5>
		</languagepack>
		<languagepack version="2.4.0" language="fr_FR">
			<md5>55dab560775a957acb32f3edb23d439a</md5>
		</languagepack>
		<languagepack version="2.5.0" language="default">
			<md5>2d8aedc81bca14a3077a474299b64af6</md5>
		</languagepack>
		<languagepack version="2.5.0" language="fr_FR">
			<md5>ebdcb836634fb3c0cb57d8b4d1c745da</md5>
		</languagepack>
		<languagepack version="2.5.1" language="default">
			<md5>26ae6128e32b5e5567b4fb52f8b5a2d2</md5>
		</languagepack>
		<languagepack version="2.5.1" language="fr_FR">
			<md5>c371f7323107d00de9c9172e5a51f05a</md5>
		</languagepack>
	</languagePackIndex>
</documentationPackIndex>
"""
prolog_template = """\
<?xml version="1.0" standalone="yes" ?>
<documentationPackIndex>
	<meta>
		<timestamp>%(unixtime)s</timestamp>
		<date>%(datetimestr)s</date>
	</meta>
	<languagePackIndex>"""

languagepack = """\
		<languagepack version="%(version)s" language="%(language)s">
			<md5>%(md5)s</md5>
		</languagepack>"""

epilog = """\
	</languagePackIndex>
</documentationPackIndex>"""

re_obj = re.compile('''
   <languagepack
   \\s+
   version="(?P<version>\d+\.\d+\.\d+)"
   \\s+
   language="(?P<language>[a-zA-Z-_]*)"\\s*.
   \\s*<md5>(?P<md5>[a-f0-9]*)</md5>
''', re.VERBOSE + re.DOTALL)


def version_tuple(v):
    return tuple([int(part) for part in v.split('.') if part.isdigit()])

def version_cmp(a, b):
    return cmp(version_tuple(a), version_tuple(b))

def getversions(fpath):
    result = {}
    with codecs.open(fpath, 'r', 'utf-8') as f1:
        data = f1.read()
    for m in re_obj.finditer(data):
        k = '%s,%s' % (m.group('version'), m.group('language'))
        result[k] = {
            'version': m.group('version'),
            'language': m.group('language'),
            'md5': m.group('md5')
        }
    return result

def version_cmp(a, b):
    result = cmp(version_tuple(a[1]['version']), version_tuple(b[1]['version']))
    if result == 0:
        result = cmp(a[1]['language'], b[1]['language'])
    return result


versions1 = getversions(fpath1)
versions2 = getversions(fpath2)
versions3 = versions1.copy()
versions3.update(versions2)

print(prolog_template % {'unixtime': unixtime, 'datetimestr': datetimestr})
for k, v in sorted(list(versions3.items()), cmp=version_cmp):
    print(languagepack % v)
print(epilog)
