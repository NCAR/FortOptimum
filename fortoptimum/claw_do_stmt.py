# coding: utf-8

from __future__ import unicode_literals, print_function

import seqgentools as seq

#from fparser.two.utils import walk_ast
#from fparser.two.parser import ParserFactory
#from fparser.two.utils import FortranSyntaxError
#from fparser.common.readfortran import FortranFileReader, FortranStringReader

from util import (collect_tightly_nested_loops, select_subnode, do_stmts,
        collect_next_sibling_loops, collect_samerange_loops, get_loopcontrol)

class ClawAnnotation(seq.Sequence):

    def __init__(self, node):

        self._node = node

    def annotate(self, item):
        raise NotImplementedError

class ClawLoopInterchange(ClawAnnotation):

    def __init__(self, node, loopvars):

        self._loopvars = loopvars
        self._vars = seq.Permutations(loopvars)

        super(ClawLoopInterchange, self).__init__(node)

    def getitem(self, index):
        return (self, self._vars[index])

    def length(self):
        return self._vars.length()

    def copy(self, memo={}):
        return ClawLoopInterchange(self._node, self._loopvars)

    def annotate(self, item):
        varlist = ", ".join(item) 
        yield "!$claw loop-interchange (%s)"%varlist, self._node.item.span[0]-1

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

    def __init__(self, prefix, headstmt, dostmts):

        self._prefix = prefix
        self._headstmt = headstmt
        self._dostmts = dostmts
        self._stmts = seq.CombinationRange(dostmts, start=1)

        super(ClawLoopFusion, self).__init__(headstmt)

    def getitem(self, index):

        item = self._stmts[index]
        if item:
            return (self, ("%s-%d"%(self._prefix, index), [self._headstmt]+list(item)))
        else:
            return (self, ("%s-%d"%(self._prefix, index), list()))

    def length(self):
        return self._stmts.length()

    def copy(self, memo={}):
        return ClawLoopFusion(self._prefix, self._dostmts)

    def annotate(self, item):
        group, dostmts = item
        for dostmt in dostmts:
            yield "!$claw loop-fusion group(%s)"%group, dostmt.item.span[0]-1

def anno_fusion(dostmt):

    doconst = dostmt.parent
    # find candiate sibiling do stmts
    # find combinations of range of groups
    # find collaps ranges

    # claw interchange accept tightly nested loops only
    next_loops = collect_next_sibling_loops(doconst)

    stmts = []

    for doloop in next_loops:
        stmt = select_subnode(doloop, nodeclass=do_stmts, num_subnode=1)
        stmts.append(stmt)

    lvar, start, stop, step = get_loopcontrol(dostmt)

    filtered = collect_samerange_loops(stmts, str(lvar), start=str(start), stop=str(stop), step=str(step))

    if filtered:

        return ClawLoopFusion("grp%d"%dostmt.item.span[0], dostmt, filtered)

annotators = [
    anno_interchange,
    anno_fusion,
]


def annotations(dostmt):

    annos = []

    for annotator in annotators:
        anno = annotator(dostmt)
        if anno:
            annos.append(anno)

    return seq.Chain(*annos)
