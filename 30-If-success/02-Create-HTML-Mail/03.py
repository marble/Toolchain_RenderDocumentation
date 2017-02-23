#! /usr/bin/env python
# coding: utf-8

from __future__ import print_function

from bs4 import BeautifulSoup
import codecs
import sys

f1path = 'outfile-prettified.html'
f1path = '/home/marble/Repositories/github.com/TYPO3-Documentation/t3SphinxThemeRtdEmail/dist/t3docs.html'

with codecs.open(f1path, 'r', 'utf-8') as f1:
    html_doc = f1.read()

soup = BeautifulSoup(html_doc, 'html.parser')

def first_or_none(resultset):
    result = None
    if len(resultset):
        result = resultset[0]
    return result

def decompose_these(*args):
    result = []
    for i, arg in enumerate(args):
        if arg:
            arg.decompose()
            result.append(None)
        else:
            result.append(arg)
    return result

# gather information

h1 = soup.h1
h2 = soup.h2
h3 = soup.h3
h4 = soup.h4
p = soup.p
a = soup.a

idDivYourProject = first_or_none(soup.find_all(id="idDivYourProject"))
idCalloutSettingsFile = first_or_none(soup.find_all(id="idCalloutSettingsFile"))
idCalloutCongratulations = first_or_none(soup.find_all(id="idCalloutCongratulations"))
idCalloutThereAreWarnings = first_or_none(soup.find_all(id="idCalloutThereAreWarnings"))
idDivAboutThisMail = first_or_none(soup.find_all(id="idDivAboutThisMail"))
idDivGeneralInformation = first_or_none(soup.find_all(id="idDivGeneralInformation"))

idSpanISendToReceivers = first_or_none(soup.find_all(id="idSpanISendToReceivers"))
idSpanISawANo = first_or_none(soup.find_all(id="idSpanISawANo"))
idFoundSettingAboutEmailing = first_or_none(soup.find_all(id="idFoundSettingAboutEmailing"))
idFoundNoSettingAboutEmailing = first_or_none(soup.find_all(id="idFoundNoSettingAboutEmailing"))
idSendToProjectEmails = first_or_none(soup.find_all(id="idSendToProjectEmails"))

idABUILDINFO = first_or_none(soup.find_all(id="idABUILDINFO"))
idAHTML= first_or_none(soup.find_all(id="idAHTML"))
idASINGLEHTML= first_or_none(soup.find_all(id="idASINGLEHTML"))
idAPDF = first_or_none(soup.find_all(id="idAPDF"))
idAPACKAGE= first_or_none(soup.find_all(id="idAPACKAGE"))


# fill dummy

D = {}
D['project_name'] = 'Projectname'
D['project_version'] = '1.2.3'
D['build_time'] = '2017-02-02 16:41:13'
D['this_was_made'] = '#dummy, dummy.'
D['this_failed'] = 'dummy, dummy.'
D['absurl_buildinfo'] = '#absurl_buildinfo'
D['absurl_warnings_txt'] = '#absurl_warnings_txt'
D['absurl_settings_cfg'] = '#absurl_settings_cfg'
D['receivers_from_settings_cfg'] = '<a href="mailto:one@mail.com>one@mail.com</a>, <a href="mailto:two@mail.com>two@mail.com</a>'
D['receivers_from_project'] = '<a href="mailto:three@mail.com>three@mail.com</a>'

# What succeeded? What failed?

successparts = []
failparts = []

if 0:
    attrs = a.attrs.copy()
    attrs['href'] = '#html'
    atag = soup.new_tag('a', **attrs)
    atag.string = 'html'
    successparts.append(unicode(atag))
else:
    failparts.append('html')

if 0:
    attrs = a.attrs.copy()
    attrs['href'] = '#singlehtml'
    atag = soup.new_tag('a', **attrs)
    atag.string = 'singlehtml'
    successparts.append(unicode(atag))
else:
    failparts.append('singlehtml')

if 0:
    attrs = a.attrs.copy()
    attrs['href'] = '#pdf'
    atag = soup.new_tag('a', **attrs)
    atag.string = 'pdf'
    successparts.append(unicode(atag))
else:
    failparts.append('pdf')

if 0:
    attrs = a.attrs.copy()
    attrs['href'] = '#package'
    atag = soup.new_tag('a', **attrs)
    atag.string = 'package'
    successparts.append(unicode(atag))
else:
    failparts.append('package')

if 0:
    attrs = a.attrs.copy()
    attrs['href'] = '#buildinfo'
    atag = soup.new_tag('a', **attrs)
    atag.string = 'buildinfo'
    successparts.append(unicode(atag))
else:
    failparts.append('buildinfo')

successparts = successparts if successparts else ['nothing']
failparts = failparts if failparts else ['nothing']
D['this_was_made'] = u', '.join(successparts) + '.'
D['this_failed'] = u', '.join(failparts) + '.'


# text block logic

if 1:
    # We have created a Settings.cfg from a Yaml file
    pass
else:
    idCalloutSettingsFile = decompose_these(idCalloutSettingsFile)

if 1:
    # Congratulations!
    idCalloutThereAreWarnings = decompose_these(idCalloutThereAreWarnings)
else:
    # Sphinx shows errors
    idCalloutCongratulations = decompose_these(idCalloutCongratulations)

if 0:
    # We really send to receivers we found in settings
    idSpanISawANo = decompose_these(idSpanISawANo)
else:
    # We really found a 'no' in the settings
    idSpanISendToReceivers = decompose_these(idSpanISendToReceivers)

if 1:
    # We found an entry about emailing in the settings
    idFoundNoSettingAboutEmailing, idSendToProjectEmails = decompose_these(idFoundNoSettingAboutEmailing, idSendToProjectEmails)
else:
    # We did not find an entry about emailing in the settings
    decompose_these(idFoundSettingAboutEmailing)

if idSendToProjectEmails and 'receivers_from_project' and 1:
    pass
else:
    idSendToProjectEmails = decompose_these(idSendToProjectEmails)

# handle links in the General Info section

if 1:
    # if we have no BUILDINFO
    idABUILDINFO.attrs['href'] = '#buildinfo'
else:
    # if we have no BUILDINFO
    new_strong_tag = soup.new_tag("strong")
    new_strong_tag.string = idABUILDINFO.string
    idABUILDINFO.replace_with(new_strong_tag)

if 1:
    # if we have HTML
    idAHTML.attrs['href'] = '#html'
else:
    # if we have no HTML
    new_strong_tag = soup.new_tag("strong")
    new_strong_tag.string = idAHTML.string
    idAHTML.replace_with(new_strong_tag)

if 1:
    # if we have SINGLEHTML
    idASINGLEHTML.attrs['href'] = '#singlehtml'
else:
    # if we have no SINGLEHTML
    new_strong_tag = soup.new_tag("strong")
    new_strong_tag.string = idASINGLEHTML.string
    idASINGLEHTML.replace_with(new_strong_tag)

if 1:
    # if we have a PDF
    idAPDF.attrs['href'] = '#pdf'
else:
    # if we have no PDF
    new_strong_tag = soup.new_tag("strong")
    new_strong_tag.string = idAPDF.string
    idAPDF.replace_with(new_strong_tag)

if 1:
    # if we have no PACKAGE
    idAPACKAGE.attrs['href'] = '#package'
else:
    # if we have no PACKAGE
    new_strong_tag = soup.new_tag("strong")
    new_strong_tag.string = idAPACKAGE.string
    idAPACKAGE.replace_with(new_strong_tag)


# lstrip the <pre> blocks

for pre in soup.find_all('pre'):
    pre.string.replace_with(u'\n'.join([part.lstrip() for part in pre.string.split('\n')]))
    print(pre.string)

# create outfile
# replace variables

with codecs.open('outfile-prettified-2.html', 'w', 'utf-8') as f2:
    prettified = soup.prettify()
    prettified = prettified.replace('%', '%%').replace('%%(', '%(') % D
    f2.write(prettified)

with codecs.open('outfile-str-2.html', 'w', 'utf-8') as f2:
    prettified = unicode(soup)
    prettified = prettified.replace('%', '%%').replace('%%(', '%(') % D
    f2.write(prettified)







"""
<div class="yt-lockup-content">
    <h3 class="yt-lockup-title "><a
            class="yt-uix-sessionlink yt-uix-tile-link  spf-link  yt-ui-ellipsis yt-ui-ellipsis-2"
            dir="ltr"
            title="#110 Complete OTA with a Reed Switch ?"
            aria-describedby="description-id-786762"
            data-sessionlink="ei=H6GTWLTACtCy1gLonpnABA&amp;feature=c4-videos-u&amp;ved=CDgQlx4iEwj0y5eqqvLRAhVQmVUKHWhPBkgomxw"
            href="https://www.youtube.com/watch?v=e409WzuK-pU&amp;t=4s">#110
        Complete OTA with a Reed Switch ?</a><span
            class="accessible-description"
            id="description-id-786762"> - Dauer: 5 Minuten, 46 Sekunden</span>
    </h3>

    <div class="yt-lockup-meta">
        <ul class="yt-lockup-meta-info">
            <li>5.569 Aufrufe</li>
            <li>vor 3 Wochen</li>
        </ul>
    </div>
</div>
"""