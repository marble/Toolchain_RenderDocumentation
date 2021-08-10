#!/usr/bin/env python
# coding: utf-8


from __future__ import absolute_import
from __future__ import print_function

teststring = """
old: href="../../_static/css/t3more.css"
new: href="/t3SphinxThemeRtd/3.6.0/css/t3more.css"

old: src="../../_static/jquery.js"
new: src="/t3SphinxThemeRtd/3.6.0/jquery.js"
"""


import re

regexpattern = re.compile(
    """
        (?P<intro>
        (?:href|src)           # non capturing href or src
        \s*                    # optional whitespace
        =
        \s*                    # optional whitespace
        )
        (?P<quote>"|')         # group "quote" is either ' or "
        \s*                    # unlikely whitespace
        (?P<relpart>[\./]*_static/)   # the relative part we want to replace
        (?P<payload>[\S]*)     # the payload
        \s*                    # unlikely whitespace
        (?P=quote)             # the quote again
    """,
    re.VERBOSE,
)

version = "3.6.0"
replacement = (
    r"\g<intro>\g<quote>/t3SphinxThemeRtd/" + version + "/" + "\g<payload>\g<quote>"
)

print(regexpattern.sub(replacement, teststring))
