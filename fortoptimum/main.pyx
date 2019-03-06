
# TODO: combine command inputs with compiler option space

targets@arg = "targets", nargs="+", help="source files"
cleancmd@arg = "-c", "--clean", required=True, help="command to clean"
buildcmd@arg = "-b", "--build", required=True, help="command to build"
executecmd@arg = "-e", "--execute", required=True, help="command to execute"
workdir@arg = "-d", "--workdir", help="working directory"
recovercmd@arg = "-r", "--recover", help="command to recover"

import sys
import os
import tempfile
import shutil
import seqgentools as seq
import space
import execute
import transform
import measure
import platform

macpro = platform.node() == "cisl-blaine.scd.ucar.edu"
cheyenne_login = platform.node().startswith("cheyenne")

[config@macpro]

fparser@text = /Users/youngsun/repos/github/perftasks/fortran/parser/fparser2/fparser2_task.py
optdiscover@text = /Users/youngsun/repos/github/FortOptimum/fortoptimum/discover.py
clawfc@text = /Users/youngsun/opt/claw/1.2.1/bin/clawfc

[config@cheyenne_login]

fparser@text = /gpfs/u/home/youngsun/repos/github/perftasks/fortran/parser/fparser2/fparser2_task.py
optdiscover@text = /gpfs/u/home/youngsun/repos/github/FortOptimum/fortoptimum/discover.py
clawfc@text = /glade/p/cisl/asap/youngsun/opt/claw/02252019/bin/clawfc

[main]

temp = tempfile.mkdtemp()

# backup original target
org = os.path.join(temp, "org")

targets@py = ${targets:arg}

for target in targets:
    if os.path.isfile(target):
        if not os.path.isdir(org):
            os.makedirs(org)
        shutil.copy2(target, org)
    elif os.path.isdir(target):
        print("Directory target is not supported yet: %s"%target)
        sys.exit(-1)
        shutil.copytree(target, org)

# parse source files
astlist = {}
srcprog = {}

for target in targets:
    parsed@pyloco = ${fparser} ${target} -D SET_NX=4,SET_NELEM="6*120*120",SET_NIT=1000
    astlist.update(parsed['astlist'])
    srcprog.update(parsed['srcprog'])

# configure searching
envs = space.EnvVarSpace()
copts = space.CompOptSpace()
lopts = space.LinkOptSpace()
ropts = space.ExeEnvSpace()

# - measure performance
# - verify output
# - searching management

# no RL
# just create a space of all possible source code transformation possible, so it is static space
# find optimal solution and try to understand why it works
# and somehow train machine to capture the knowledge one by one

# discover source xform cases
# get a list of src xform options
xforms = []
for path, ast in astlist.items():
    optdiscovered@pyloco = ${optdiscover}
    xforms.append(optdiscovered['xformspace'])
xformspace = space.XformSpace(*xforms)

searchspace = space.SearchSpace(xformspace, envs, copts, lopts, ropts)

# get reference case
self.parent.send_websocket("dgkernel", "refcase", "REF")
self.parent.send_websocket("dgkernel", "refsrc", srcprog)
refcase@py = execute.execute_case("${cleancmd:arg}", "${buildcmd:arg}", "${executecmd:arg}", "${workdir:arg}", *[[]]*4, recover=${recovercmd:arg})
self.parent.send_websocket("dgkernel", "refout", refcase)
refdata = measure.dgkernel(refcase)
self.parent.send_websocket("dgkernel", "refmeasure", refdata)

# run optimization
try:

    # TODO: update web browser
    finished = False
    while not finished:
        nextcase = next(searchspace)
        self.parent.send_websocket("dgkernel", "case", "CASE")
        modified@py = transform.claw_xform(clawfc, temp, "${workdir:arg}", srcprog, nextcase[0])
        self.parent.send_websocket("dgkernel", "src", modified)
        curcase@py = execute.execute_case("${cleancmd:arg}", "${buildcmd:arg}", "${executecmd:arg}", "${workdir:arg}", *nextcase[1:], recover=${recovercmd:arg})
        self.parent.send_websocket("dgkernel", "out", curcase)
        curdata = measure.dgkernel(curcase)
        self.parent.send_websocket("dgkernel", "measure", curdata)
        transform.recover(temp, srcprog, nextcase[0])
        finished = measure.check_continue(refdata, curdata)

except Exception as err:
    print(err)

for target in targets:
    orgfile = "%s.org"%target
    if os.path.isfile(orgfile):
        os.remove(path)
        shutil.copyfile(orgfile, path)

import pdb; pdb.set_trace()
# report result
