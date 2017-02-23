#! /usr/bin/env python
# coding: utf-8

# pip install --upgrade bs4

import codecs

from bs4 import BeautifulSoup
with codecs.open('001-t3docs.html', 'r', 'utf-8') as f1:
    html_doc = f1.read()

soup = BeautifulSoup(html_doc, 'html.parser')

if 1:
    with codecs.open('002-t3docs-prettified.html', 'w', 'utf-8') as f2:
        prettified = soup.prettify()
        # print(prettified)
        f2.write(prettified)

if 0:
    with codecs.open('outfile-str.html', 'w', 'utf-8') as f2:
        # print(soup)
        f2.write(unicode(soup))
