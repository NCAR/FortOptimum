
import sys
import unittest
import fortoptimum

class PrimitiveOptTests(unittest.TestCase):

    def setUp(self):

        self.srcdir = "/Users/youngsun/repos/github/FortOptimum/tests/src"
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

