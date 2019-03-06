# coding: utf-8

from __future__ import unicode_literals, print_function

import os


def dgkernel(refdata):

    valid, stdout, stderr = refdata

    if not valid:
        return stdout, stderr

    minfly = None
    maxfly = None
    start = None
    stop = None

    for line in stdout.split("\n"):

        line = line.strip()

        if line.startswith("MAX(flx)"):
            _, val = line.split("=")
            maxfly = float(val)
        elif line.startswith("MIN(fly)"):
            _, val = line.split("=")
            minfly = float(val)
        elif line.startswith("CLOCK START"):
            _, _, clk, rate = line.split()
            start = float(clk) / float(rate)
        elif line.startswith("CLOCK STOP"):
            _, _, clk, rate = line.split()
            stop = float(clk) / float(rate)

    return (minfly, maxfly), (stop - start, )

def check_continue(refcase, curcase):

    print("REF", refcase)
    print("CUR", curcase)

    return False
