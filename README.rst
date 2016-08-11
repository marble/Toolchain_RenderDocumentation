

===================
RenderDocumentation
===================


-----------------------------------------
A Toolchain To Render TYPO3 Documentation
-----------------------------------------

:Author:          Martin Bless <martin@mbless.de>
:Repository:      https://github.com/marble/Toolchain_RenderDocumentation
:Target Folder:   ~/Toolchains/RenderDocumentation


Description
===========

This toolchain is for Linux-like systems. It is to be run by
TCT, the Tool-Chain-Tool ((provide link)).

Definition: A tool is an *executable* file in the repository
with these characteristics:

- name starts with 'run_'
- must be executable (x bit set)
- linux must be able to run it
- any programming language allowed
- binary files are allowed
- can be located in any folder at any nesting level in the
  repository

TCT looks for tools (=files) at the top level first and runs
them in alphabetical order. It then processes the subfolders
in alphabetical order in the same way. So we have a recursion
here and proceed in "top-down first" fashion.

((to be continued))
