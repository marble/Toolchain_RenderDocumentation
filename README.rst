.. highlight:: shell

===================
RenderDocumentation
===================


-----------------------------------------
A Toolchain To Render TYPO3 Documentation
-----------------------------------------

:Version:         2.11.0
:Date:            2020-12-10
:Author:          Martin Bless <martin.bless@mbless.de>
:Repository:      https://github.com/marble/Toolchain_RenderDocumentation
:Target Folder:   ~/Toolchains/RenderDocumentation
:Short info:
   This version knows how to handle an OpenOffice file named `./doc/manual.sxw`.
   It processes both the two versions of table handling: `dl`(as definition
   lists) and `t3flt` (TYPO3 field list table). Example: `... -c oo_parser t3flt`.

Release notes
=============

What has changed? See `CHANGES <CHANGES.rst>`_.



Description
===========

This toolchain is for Linux-like systems. It is to be run by
TCT, the Tool-Chain-Tool ((provide link)).

Definition: A tool is an *executable* file in the repository
with these characteristics:

-  name starts with 'run_'
-  must be executable (x bit set)
-  linux must be able to run it
-  any programming language allowed
-  binary files are allowed
-  can be located in any folder at any nesting level in the
   repository

TCT looks for tools (=files) at the top level first and runs
them in alphabetical order. It then processes the subfolders
in alphabetical order in the same way. So we have a recursion
here and proceed in "top-down first" fashion.

Definition: A toolchain is a folder with its files and subfolders.

TCT recreates the folder structure of the toolchain for all the
actual tools it finds in a temporary file space.

((more to be written))


xxx
===

::

   tct
   tct --help
   tct clean --help
   tct run   --help

   cd ~/Repositories/mbnas/mbgit/tct
   tct -v run RenderDocumentation --toolchain-help
   tct -v run RenderDocumentation -T unlock
   tct -v run RenderDocumentation --clean-but 2
   # tct -v run RenderDocumentation -c makedir ../Makedirs/manual_gettingstarted.make -c rebuild_needed 1 -c talk 2
   tct -v run RenderDocumentation \
       -c makedir        ../Makedirs/manual_gettingstarted.make  \
       -c rebuild_needed 1  \
       -c talk           2


Start normally::

   (venv)$  tct

Debugging::

   cd ~/Repositories/mbnas/mbgit/tct
   # edit tct.py "if __name__=='__main__':" ...
   (venv) python tct.py

   # In PyCharm debugging extends to spawned subprocesses automatically!!!
