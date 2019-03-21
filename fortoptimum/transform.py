# coding: utf-8

from __future__ import unicode_literals, print_function

import os
import shutil

from util import run_shcmd

def claw_xform(clawfc, tempdir, workdir, srcs, xforms):

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

            for anno, loc in xformer.annotate(xformargs):

                if loc in locs:
                    locs[loc].append(anno)
                else:
                    locs[loc] = [anno]

    clawtemp = os.path.join(tempdir, "clawxform")
    if os.path.isdir(clawtemp):
        shutil.rmtree(clawtemp)
    os.makedirs(clawtemp)

    modified = {}
    idx = 0

    for path, src in srcs.items():

        if path in annotations:

            lines = []
            for num, line in enumerate(src.split("\n")):
                if num in annotations[path]:
                    lines.extend(annotations[path][num])
                lines.append(line)

            orgfile = "%s.org"%path
            if not os.path.isfile(orgfile):
                shutil.copyfile(path, orgfile)

            tempfile = os.path.join(clawtemp, "c%d.f90"%idx)
            with open(tempfile, 'w') as fw:
                fw.write("\n".join(lines))

            clawcmd = "%s -o %s -d=claw -t=cpu %s"%(clawfc, path, tempfile)
            stdout, stderr, retcode = run_shcmd(clawcmd, shell=True, cwd=workdir)

            modified[path] = "\n".join(lines)
            idx += 1

    return modified

def recover(tempdir, srcs, xforms):

    for path, src in srcs.items():
        orgfile = "%s.org"%path
        if os.path.isfile(orgfile):
            os.remove(path)
            shutil.copyfile(orgfile, path)

