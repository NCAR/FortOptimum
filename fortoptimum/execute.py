# coding: utf-8

from __future__ import unicode_literals, print_function

import os

from util import run_shcmd

def execute_case(cleancmd, buildcmd, executecmd, recovercmd, workdir, envs, copts, lopts, ropts):

    # TODO: clean opts and run opts?

    # clean
    #ret, stdout, stderr = run_shcmd(cleancmd, shell=True, env=environ)
    stdout, stderr, retcode = run_shcmd(cleancmd, shell=True, cwd=workdir)

    # build
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

    stdout, stderr, retcode = run_shcmd(buildcmd, shell=True, env=environ, cwd=workdir)


    # run
    #ret, stdout, stderr = run_shcmd(executecmd, shell=True, env=environ)
    stdout, stderr, retcode = run_shcmd(executecmd, shell=True, cwd=workdir)

    # collect result

    # recover
    stdout, stderr, retcode = run_shcmd(recovercmd, shell=True, cwd=workdir)

def check_continue(case):

    return False
