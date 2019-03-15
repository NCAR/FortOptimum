# coding: utf-8

from __future__ import unicode_literals, print_function

import seqgentools as seq

#from fparser.two.utils import walk_ast
#from fparser.two.parser import ParserFactory
#from fparser.two.utils import FortranSyntaxError
#from fparser.common.readfortran import FortranFileReader, FortranStringReader

from util import (collect_tightly_nested_loops, select_subnode, do_stmts,
        collect_next_sibling_loops)

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
            stmt = select_subnode(doloop, nodeclass=do_stmts, num_subnode=1)
            loopctrl = stmt.items[1]
            name = loopctrl.items[1][0].string
            varnames.append(name)

        # generate permutations
        return ClawLoopInterchange(dostmt, varnames)

class ClawLoopFusion(ClawAnnotation):

    def __init__(self, prefix, dostmts):

        self._prefix = prefix
        self._dostmts = dostmts
        self._stmts = seq.CombinatioinRange(dostmts)

    def getitem(self, index):
        return (self, ("%s-%d"%(self._prefix, index), self._stmts[index]))

    def length(self):
        return self._vars.length()

    def copy(self, memo={}):
        return ClawLoopFusion(self._prefix, self._dostmts)

    def annotate(self, item):
        group, stmt = item
        return "!$claw loop-fusion (%s)"%group, 0

def anno_fusion(dostmt):

    doconst = dostmt.parent

    # claw interchange accept tightly nested loops only
    next_loops = collect_next_sibling_loops(doconst)

    if next_loops:

        do_stmts = []

        for doloop in next_loops:
            stmt = select_subnode(doloop, nodeclass=do_stmts, num_subnode=1)
            do_stmts.append(stmt)

        return ClawLoopFusion(prefix, do_stmts)

annotators = [
    anno_interchange,
]

    #anno_fusion,

def annotations(dostmt):

    annos = []

    for annotator in annotators:
        anno = annotator(dostmt)
        if anno:
            annos.append(anno)

    return seq.Chain(*annos)
