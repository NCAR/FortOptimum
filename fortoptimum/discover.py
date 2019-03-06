# coding: utf-8

from __future__ import unicode_literals, print_function

#import sys
#import os
import pyloco
#import subprocess
import seqgentools as seq

from fparser.two.utils import walk_ast, Base
#from fparser.two.parser import ParserFactory
#from fparser.two.utils import FortranSyntaxError
#from fparser.common.readfortran import FortranFileReader, FortranStringReader

import claw_do_stmt

class OptDiscoverTask(pyloco.PylocoTask):

    def __init__(self, parent):
        pass


    def perform(self, targs):

        # expect "path" and "ast" in self.env
        path = self.env['path']

        for node in walk_ast(self.env['ast'].content):

            # create parent attributes
            for x in getattr(node, "content", []):
                if isinstance(x, Base):
                    x.parent = node
            for x in getattr(node, "items", []):
                if isinstance(x, Base):
                    x.parent = node

        xforms = []

        for node in walk_ast(self.env['ast'].content):

            cname = node.__class__.__name__

            if cname.endswith("_Stmt") and not cname.startswith("End"):
                xformer = getattr(self, "xform_%s"%cname)
                xform = xformer(node)
                if xform:
                    xforms.append(xform)

        xformspace = seq.Chain(*xforms)

        return 0, {"xformspace": xformspace}

    def xform_Program_Stmt(self, node):
        pass

    def xform_Use_Stmt(self, node):
        pass

    def xform_Implicit_Stmt(self, node):
        pass

    def xform_Type_Declaration_Stmt(self, node):
        pass

    def xform_Assignment_Stmt(self, node):
        # TODO: may have lots of xformations
        #       for now, we focus on loops
        pass

    def xform_Nonlabel_Do_Stmt(self, node):

        return claw_do_stmt.annotations(node)

    def xform_Write_Stmt(self, node):
        pass

    def xform_Call_Stmt(self, node):
        # TODO: for testing only
        pass

