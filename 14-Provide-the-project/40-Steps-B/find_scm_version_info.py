#!/usr/bin/env python3
# find_scm_version_info.py, mb, 2022-04-21, 2022-04-21

import json
import pprint
import sys
from pathlib import Path

import setuptools_scm
from setuptools_scm import (DEFAULT_LOCAL_SCHEME, DEFAULT_TAG_REGEX,
                            DEFAULT_VERSION_SCHEME, warnings)

# two globals
collected_errors = []
collected_warnings = []

def is_json_encodable(v):
    result = True
    try:
        json.dumps(v)
    except TypeError:
        result = False
    return result

def showwarning(message, category, filename, lineno, file=None, line=None):
    parts = []
    if message:
        parts.append(f"{message=!r}")
    if category:
        parts.append(f"{category=!r}")
    if filename:
        parts.append(f"{filename=!r}")
    if lineno:
        parts.append(f"{lineno=!r}")
    if file:
        parts.append(f"{file=!r}")
    if line:
        parts.append(f"{line=!r}")
    if parts:
        collected_warnings.append(' '.join(parts))

warnings.showwarning = showwarning

def my_get_version(
        root=".",
        dist_name=None,
        fallback_root=".",
        fallback_version=None,
        git_describe_command=None,
        local_scheme=DEFAULT_LOCAL_SCHEME,
        normalize=True,
        parentdir_prefix_version=None,
        parse=None,
        relative_to=None,
        search_parent_directories=False,
        tag_regex=DEFAULT_TAG_REGEX,
        version_cls=None,
        version_scheme=DEFAULT_VERSION_SCHEME,
        write_to=None,
        write_to_template=None,
):
    config = setuptools_scm.Configuration(**locals())

    # We want to find meaning to these three
    error = None
    guessed_version = None
    parsed_scm_version = None

    try:
        parsed_scm_version = setuptools_scm._do_parse(config)
    except LookupError:
        error = 'LookupError'
    except:
        error = 'Unknown error'

    if parsed_scm_version:
        guessed_version = setuptools_scm.format_version(
            parsed_scm_version,
            version_scheme=version_scheme,
            local_scheme=local_scheme,
        )
    return guessed_version, parsed_scm_version, error


def main(root='.', fallback_version='unknown'):
    root = str(Path(root).expanduser())
    result = {}
    scm_version_info = {}
    result['scm_version_info'] = scm_version_info
    collected_errors[:] = []
    collected_warnings[:] = []
    guessed_version, parsed_scm_version, error = my_get_version(
        fallback_root=root,
        fallback_version=fallback_version,
        root=root,
    )
    if error:
        collected_errors.append(error)

    if collected_warnings:
        scm_version_info['warnings'] = collected_warnings[:]

    if collected_errors:
        scm_version_info['errors'] = collected_errors[:]

    if guessed_version:
        scm_version_info['guessed_version'] = guessed_version

    if parsed_scm_version:
        # reveal all attributes of the parsed_scm_version object
        vv_pprint = {}
        vv_json = {}
        vv = vars(parsed_scm_version)
        for k, v in vv.items():
            if is_json_encodable(v):
                vv_pprint[k] = v
                vv_json[k] = v
            else:
                vv_pprint[k] = pprint.pformat(v)
        scm_version_info['pprint'] = vv_pprint
        scm_version_info['json'] = vv_json

    # anything found at all?
    if scm_version_info:
        scm_version_info['00info'] = (
            "Showing what the Python module 'setuptools_scm' "
            "can tell us about the input repository and its version."
        )
        scm_version_info['project'] = root
        # provide handy access to 'is_shallow'
        is_shallow = False
        for line in collected_warnings:
            if "is shallow" in line:
                is_shallow = True
                break
        if is_shallow:
            scm_version_info['is_shallow'] = is_shallow

    return result

def usage():
    print(
        f"\nUsage:"
        f"\n   python3 find_scm_version_info.py  PATH"
        f"\n"
        f"\nPurpose:"
        f"\n   Print version info about derived from a repository in JSON format."
        f"\n   Internally the Python module 'setuptools_scm` is used."
        f"\n"
        f"\nExample:"
        f"\n   python3 find_scm_version_info.py  ."
        f"\n"
    )


if 0 and 'programmatical usage':
    import find_scm_version_info
    result_dict = find_scm_version_info.main(root='path/to/project')

if __name__ == "__main__":
    root = None
    if len(sys.argv) == 2:
        root = sys.argv[1]
    if root:
        scm_version_info = main(root=root)
        print(json.dumps(scm_version_info, indent=4, sort_keys=True))
    else:
        usage()
