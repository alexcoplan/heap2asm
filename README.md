# heap2asm bootstrap

A script and set of sources for building a native heap2asm executable. heap2asm
is used by (but typically not bundled with) the heap2exec script, which is used
to turn a smlnj heap image into an executable.

## Rationale

The sources for heap2asm are available on the smlnj website, but building a
heap2asm executable from scratch is surprisingly nontrivial. The script (and
modified copy of heap2exec) in this repository solve this problem.

