# coding: utf-8

from __future__ import unicode_literals, print_function

import os

from util import run_shcmd

def claw_xform(clawfc, tempdir, srcs, xforms):

    annotations = {}

    # generate source
    for xform in xforms:
        if xform:

            xformer = xform[0]
            xformargs = xform[1]
            stmt = xformer._node
            item = stmt.item
            srcfile = item.reader.id

            if srcfile not in annotations:
                locs = {}
                annotations[srcfile] = locs
            else:
                locs = annotations[srcfile]

            anno, pos = xformer.annotate(xformargs)
            
            if pos <= 0:
                loc = item.span[0]+pos-1
            else:
                loc = item.span[1]+pos-1

            if loc in locs:
                locs[loc].append(anno)
            else:
                locs[loc] = [anno]

    modified = {}

    for path, src in srcs.items():
        if path in annotations:
            lines = []
            for num, line in enumerate(src.split("\n")):
                if num in annotations[path]:
                    lines.extend(annotations[path][num])
                lines.append(line)
            with open(path, 'w') as fw:
                fw.write("\n".join(lines))
        else:
            with open(path, 'w') as fw:
                fw.write(src)

    clawxformdir = os.path.join(tempdir, "clawxforms")
    os.makedirs(clawxformdir)

    import pdb; pdb.set_trace()
    # construct command line arguments
    for idx, path in enumerate(anntations):
        ret, stdout, stderr = run_shcmd("claw....... -o tempdir...")
        if ret != 0:
            pass

    for idx, path in enumerate(anntations):
        os.delfile
        os.mvfile
 

def recover(tempdir, srcs, xforms):

    import pdb; pdb.set_trace()

