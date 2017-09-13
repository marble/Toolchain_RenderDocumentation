#!/bin/bash

# Author: https://gist.github.com/davejamesmiller/1967569
# Myfork: https://gist.github.com/marble/870864f5823ef320f9ee8abc539caea4

# This is a script I used when I wanted to create a symlink on a remote web
# server, but that web server had the 'ln' command disabled (using cPanel's
# Jailshell).

# It works by creating a symlink on the local computer, then using rsync to copy
# that symlink to the remote server.

# Example:
# ./remote-symlink.sh myhost ../remote/path remote/target

if [ $# != 3 ]; then
  echo "Usage: $0 <host> <target> <linkname>" >&2
  exit 1
fi

tmpfile=$(tempfile)
ln -sf $2 $tmpfile
rsync -l $tmpfile $1:$3
rm $tmpfile