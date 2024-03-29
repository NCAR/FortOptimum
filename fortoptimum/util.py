# coding: utf-8

from __future__ import unicode_literals, print_function

import subprocess

from collections import OrderedDict as odict

#from fparser.two.utils import walk_ast, FortranSyntaxError
from fparser.two.Fortran2003 import (Label_Do_Stmt, Nonlabel_Do_Stmt,
    Block_Label_Do_Construct, Block_Nonlabel_Do_Construct, Action_Term_Do_Construct,
    Outer_Shared_Do_Construct, Loop_Control)

do_stmts = (Label_Do_Stmt, Nonlabel_Do_Stmt)
do_constructs = (Block_Label_Do_Construct, Block_Nonlabel_Do_Construct,
    Action_Term_Do_Construct, Outer_Shared_Do_Construct)

# to stop further traversal, return not None from func 
# The return code will be forwarded to initial caller
# func will collect anything in bag during processing
def DFS(node, func, bag, subnode='items', prerun=True, depth=0):

    ret = None

    if prerun and func is not None:
        ret = func(node, bag, depth)
        if ret is not None: return ret

    if node and hasattr(node, subnode):
        for child in getattr(node, subnode, []):
            ret = DFS(child, func, bag, subnode=subnode, prerun=prerun, depth=depth+1)

    if not prerun and func is not None:
        ret = func(node, bag, depth)
        if ret is not None: return ret

    return ret

def BFS(node, func, bag, subnode='items', prerun=True, depth=0):

    ret = None
    queue = [node]

    while queue:

        parent = queue.pop(0)
        ret = func(node, bag, depth)
        if ret is not None: return ret

        children = getattr(parent, subnode, [])
        queue.extend(children)

    return ret

def collect_tightly_nested_loops(doconst, bag=None):

    bag = [] if bag is None else bag

    num_nested = 0

    for child in doconst.content:
        if isinstance(child, do_constructs):
            if num_nested > 0:
                return []
            else:
                bag.append(child)
                num_nested += 1
                collect_tightly_nested_loops(child, bag=bag)
    return bag


def collect_next_sibling_loops(doconst):

    upper_node = doconst.parent

    bag = []

    located = False

    for child in upper_node.content:
        if located:
            if isinstance(child, do_constructs):
                bag.append(child)
        elif child is doconst:
            located = True

    return bag

def get_loopcontrol(dostmt):

    lvar, start, stop, step = [None]*4

    loop_control = select_subnode(dostmt, nodeclass=Loop_Control, num_subnode=1, subnode_attr="items")

    if loop_control:
        lvar  = loop_control.items[1][0]
        start = loop_control.items[1][1][0]
        stop  = loop_control.items[1][1][1]
        step  = loop_control.items[1][1][2] if len(loop_control.items[1][1])==3 else None

    return lvar, start, stop, step

def collect_samerange_loops(dostmts, lvar, start="None", stop="None", step="None"):

    bag = []

    for dostmt in dostmts:
        loop_control = select_subnode(dostmt, nodeclass=Loop_Control, num_subnode=1, subnode_attr="items")
        _lvar, _start, _stop, _step = get_loopcontrol(dostmt)
        if lvar==str(_lvar) and start== str(_start) and stop==str(_stop) and step==str(_step):
            bag.append(dostmt)

    return bag

def select_subnode(node, num_subnode=None, nodeclass=None, selector=None, subnode_attr="content"):

    subnodes = getattr(node, subnode_attr, [])
    
    selected = []

    if subnodes:

        for subnode in subnodes:

            if selector:
                if not selector(subnode):
                    continue            

            if nodeclass:
                if not isinstance(subnode, nodeclass):
                    continue            

            selected.append(subnode)

    if selected:
        return selected[0] if num_subnode == 1 else selected
    else:
        return None if num_subnode == 1 else []

def run_shcmd(cmd, input=None, **kwargs):

    show_error_msg = None
    if 'show_error_msg' in kwargs:
        show_error_msg = kwargs['show_error_msg']
        del kwargs['show_error_msg']

    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, \
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)
    out, err = proc.communicate(input=input)

    if proc.returncode != 0 and show_error_msg:
        print('>> %s' % cmd)
        print('returned non-zero code from shell('+str(ret_code)+')\n OUTPUT: '+str(out)+'\n ERROR: '+str(err)+'\n')

    if type(out) != type(u"A"):
        out = out.decode("utf-8")

    if type(err) != type(u"A"):
        err = err.decode("utf-8")

    return out, err, proc.returncode
