
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

#macpro = platform.node() == "cisl-blaine.scd.ucar.edu"
#macpro = platform.node() == "cisl-blaine.wlclient.ucar.edu"
macpro = platform.node().startswith("cisl-blaine")
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

# environment variable space
envs = space.EnvVarSpace()

gfrotran_flags_demo = ["-fgcse-after-reload", "-ftree-partial-pre"]
gfrotran_flags_O3 = [ "-fgcse-after-reload ",
"-finline-functions ",
"-fipa-cp-clone",
"-floop-interchange ",
"-floop-unroll-and-jam ",
"-fpeel-loops ",
"-fpredictive-commoning ",
"-fsplit-paths ",
"-ftree-loop-distribute-patterns ",
"-ftree-loop-distribution ",
"-ftree-loop-vectorize ",
"-ftree-partial-pre ",
"-ftree-slp-vectorize ",
"-funswitch-loops ",
"-fvect-cost-model ",
"-fversion-loops-for-strides"]
gfortran_flags_Ofast = [ "-ffast-math",
"-fstack-arrays",
"-fno-protect-parens"]

# compiler option space
#optflags = seq.CombinationRange(["-fgcse-after-reload", "-ftree-partial-pre"])
optflags = seq.CombinationRange(gfortran_flags_Ofast)

copts = space.CompOptSpace(["-O3"], optflags)

# linker option space
lopts = space.LinkOptSpace()

# run configuration space
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
ss_size = [searchspace.length()] + [ss.length() for ss in searchspace.subspaces]
self.parent.send_websocket("dgkernel", "searchspace", tuple(ss_size))

# get reference case
self.parent.send_websocket("dgkernel", "refsrc", srcprog)
refcase@py = execute.execute_case(self, "${cleancmd:arg}", "${buildcmd:arg}", "${executecmd:arg}", "${workdir:arg}", [], ["-O3"], [], [], recover=${recovercmd:arg})
self.parent.send_websocket("dgkernel", "refout", refcase)
refdata = measure.dgkernel(refcase)
self.parent.send_websocket("dgkernel", "refmeasure", refdata)

# run optimization
try:

    visited = 0
    finished = False
    while not finished:
        caseindex, newcase = next(searchspace)
        #caseinfo = {"caseindex": caseindex}
        #self.parent.send_websocket("dgkernel", "newcase", caseinfo)
        self.parent.send_websocket("dgkernel", "nextcase", {"algorithm": "sequencial", "params": {"nextindex": caseindex}})
        modified@py = transform.claw_xform(clawfc, temp, "${workdir:arg}", srcprog, newcase[0])
        self.parent.send_websocket("dgkernel", "src", modified)
        curcase@py = execute.execute_case(self, "${cleancmd:arg}", "${buildcmd:arg}", "${executecmd:arg}", "${workdir:arg}", *newcase[1:], recover=${recovercmd:arg})
        self.parent.send_websocket("dgkernel", "out", curcase)
        curdata = measure.dgkernel(curcase)
        self.parent.send_websocket("dgkernel", "measure", curdata)
        transform.recover(temp, srcprog, newcase[0])
        finished = measure.check_continue(refdata, curdata)

        visited += 1

except Exception as err:
    print(err)

for target in targets:
    orgfile = "%s.org"%target
    if os.path.isfile(orgfile):
        os.remove(path)
        shutil.copyfile(orgfile, path)

#import pdb; pdb.set_trace()
# report result
