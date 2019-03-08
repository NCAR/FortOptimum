# coding: utf-8

from __future__ import unicode_literals, print_function

import os

from util import run_shcmd

def _flatten(opts, bag):
    if isinstance(opts, (list, tuple)):
        for opt in opts:
            _flatten(opt, bag)
    else:
        bag.append(opts)

def execute_case(self, cleancmd, buildcmd, executecmd, workdir, envs, copts, lopts, ropts, recover=None):

    # TODO: clean opts and run opts?

    # clean
    stdout, stderr, retcode = run_shcmd(cleancmd, shell=True, cwd=workdir)
    if retcode != 0:
        return False, stdout, stderr

    # construct build options
    opts = []

    for copt in copts:
        bag = []
        _flatten(copt, bag)
        opts.extend(bag)

    for lopt in lopts:
        bag = []
        _flatten(lopt, bag)
        opts.extend(bag)

    cfgs = []

    for ropt in ropts:
        bag = []
        _flatten(ropt, bag)
        cfgs.extend(bag)

    environ = dict(os.environ)
    #environ["COMPOPTS"] = " ".join(opts)

    for env in envs:
        import pdb; pdb.set_trace()

    # build
    bcmd = buildcmd + " " + " ".join(opts)
    self.parent.send_websocket("dgkernel", "buildopts", bcmd)
    stdout, stderr, retcode = run_shcmd(bcmd, shell=True, env=environ, cwd=workdir)
    if retcode != 0:
        return False, stdout, stderr

    # run
    rcfg = executecmd + " " + " ".join(cfgs)
    self.parent.send_websocket("dgkernel", "runcfgs", rcfg)
    runout, runerr, retcode = run_shcmd(executecmd, shell=True, cwd=workdir)
    if retcode != 0:
        return False, stdout, stderr

    # recover
    if recover:
        stdout, stderr, retcode = run_shcmd(recover, shell=True, cwd=workdir)
        if retcode != 0:
            return False, stdout, stderr

    return True, runout, runerr
