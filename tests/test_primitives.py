
import sys
import os
import unittest
import fortoptimum

here = os.path.dirname(__file__)

class PrimitiveOptTests(unittest.TestCase):

    def setUp(self):

        self.srcdir = os.path.join(here, "src")
        self.target = "%s/dg_kernel.F90"%self.srcdir
        pass

    def tearDown(self):
        pass

    def test1(self):

        from fortoptimum import api

        sys.argv = [ self.target,
            "-c", "'rm' -f *.o dgkernel.exe",
            "-b", "gfortran ${COMPOPTS} %s -o dgkernel.exe"%self.target,
            "-e", "./dgkernel.exe",
            "-r", "'cp' -f dg_kernel.F90.org dg_kernel.F90",
            "-d", self.srcdir
            ]
        ret = api.entry()

        self.assertEqual(ret, 0)

test_classes = (PrimitiveOptTests,)

