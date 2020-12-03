import unittest

from circuits import Circuit
from isomorphism import find_isomorphism

class TestCircuits(unittest.TestCase):
    def test_parsing(self):
        C = Circuit("netlists/cmos_nand_1.txt")

        self.assertEqual(len(C.netlist), 4)
        self.assertEqual(C.G.number_of_nodes(), 10)

class TestIsomorphism(unittest.TestCase):
    def test_nand_nor(self):
        C1 = Circuit("netlists/cmos_nand_1.txt")
        C2 = Circuit("netlists/cmos_nand_2.txt")

        results = find_isomorphism(C1.G, C2.G)
        self.assertNotEqual(results, None)

class TestNoIsomorphism(unittest.TestCase):
    def test_nand_nor(self):
        C_nand = Circuit("netlists/cmos_nand_1.txt")
        C_nor = Circuit("netlists/cmos_nand_error.txt")

        results = find_isomorphism(C_nand.G, C_nor.G)
        self.assertEqual(results, None)
