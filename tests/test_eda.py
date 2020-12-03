import unittest

from circuits import Circuit
from isomorphism import find_isomorphism, find_equivalence

class TestCircuits(unittest.TestCase):
    def test_parsing(self):
        C = Circuit("netlists/cmos_nand_1.txt")

        self.assertEqual(len(C.netlist), 4)
        self.assertEqual(C.G.number_of_nodes(), 10)

class TestIsomorphism(unittest.TestCase):
    def test_isomorphs(self):
        C1 = Circuit("netlists/cmos_nand_1.txt")
        C2 = Circuit("netlists/cmos_nand_2.txt")

        results = find_isomorphism(C1.G, C2.G)
        self.assertNotEqual(results, None)

    def test_non_isomorph(self):
        C_nand = Circuit("netlists/cmos_nand_1.txt")
        C_nor = Circuit("netlists/cmos_nand_error.txt")

        results = find_isomorphism(C_nand.G, C_nor.G)
        self.assertEqual(results, None)

class TestEquivalence(unittest.TestCase):
    def test_equivalent(self):
        C1 = Circuit("netlists/cmos_nand_1.txt")
        C2 = Circuit("netlists/cmos_nand_2.txt")

        results = find_equivalence(C1, C2)
        self.assertNotEqual(results, None)

    def test_not_equivalent(self):
        C_nand = Circuit("netlists/cmos_nand_1.txt")
        C_nor = Circuit("netlists/cmos_nand_error.txt")

        results = find_equivalence(C_nand, C_nor)
        self.assertEqual(results, None)
