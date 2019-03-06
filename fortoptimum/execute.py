# coding: utf-8

from __future__ import unicode_literals, print_function

import os

from util import run_shcmd

def execute_case(cleancmd, buildcmd, executecmd, workdir, envs, copts, lopts, ropts, recover=None):

    # TODO: clean opts and run opts?

    # clean
    stdout, stderr, retcode = run_shcmd(cleancmd, shell=True, cwd=workdir)
    if retcode != 0:
        return False, stdout, stderr

    # construct build options
    opts = []

    for copt in copts:
        import pdb; pdb.set_trace()

    for lopt in lopts:
        import pdb; pdb.set_trace()

    for ropt in ropts:
        import pdb; pdb.set_trace()

    environ = dict(os.environ)
    environ["COMPOPTS"] = " ".join(opts)

    for env in envs:
        import pdb; pdb.set_trace()

    # build
    stdout, stderr, retcode = run_shcmd(buildcmd, shell=True, env=environ, cwd=workdir)
    if retcode != 0:
        return False, stdout, stderr

    # run
    #ret, stdout, stderr = run_shcmd(executecmd, shell=True, env=environ)
    runout, runerr, retcode = run_shcmd(executecmd, shell=True, cwd=workdir)
    if retcode != 0:
        return False, stdout, stderr

    # recover
    if recover:
        stdout, stderr, retcode = run_shcmd(recover, shell=True, cwd=workdir)
        if retcode != 0:
            return False, stdout, stderr

    return True, runout, runerr
