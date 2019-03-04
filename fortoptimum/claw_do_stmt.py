# coding: utf-8

from __future__ import unicode_literals, print_function

import seqgentools as seq

#from fparser.two.utils import walk_ast
#from fparser.two.parser import ParserFactory
#from fparser.two.utils import FortranSyntaxError
#from fparser.common.readfortran import FortranFileReader, FortranStringReader

from util import collect_tightly_nested_loops, select_subnode, do_stmts

class ClawAnnotation(seq.Sequence):

    def annotate(self, item):
        raise NotImplementedError

class ClawLoopInterchange(ClawAnnotation):

    def __init__(self, node, loopvars):

        self._node = node
        self._loopvars = loopvars
        self._vars = seq.Permutations(loopvars)

    def getitem(self, index):
        return (self, self._vars[index])

    def length(self):
        return self._vars.length()

    def copy(self, memo={}):
        return ClawLoopInterchange(self._node, self._loopvars)

    def annotate(self, item):
        varlist = ", ".join(item) 
        return "!$claw loop-interchange (%s)"%varlist, 0

def anno_interchange(dostmt):

    doconst = dostmt.parent

    # claw interchange accept tightly nested loops only
    nested_loops = collect_tightly_nested_loops(doconst)

    if nested_loops:

        # claw interchange limit up to 3 level nested loops
        doloops = [doconst] + nested_loops[:2]

        varnames = []
        # get loop variables
        for doloop in doloops:
            dostmt = select_subnode(doloop, nodeclass=do_stmts, num_subnode=1)
            loopctrl = dostmt.items[1]
            name = loopctrl.items[1][0].string
            varnames.append(name)

        # generate permutations
        return ClawLoopInterchange(dostmt, varnames)

annotators = [
    anno_interchange
]

def annotations(dostmt):

    annos = []

    for annotator in annotators:
        anno = annotator(dostmt)
        if anno:
            annos.append(anno)

    return seq.Chain(*annos)
