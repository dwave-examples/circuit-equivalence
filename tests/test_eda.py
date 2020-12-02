import unittest

from circuits import Circuit

class TestCircuits(unittest.TestCase):
    def test_parsing(self):
        C = Circuit("netlists/cmos_nand_1.txt")

        self.assertEqual(len(C.netlist), 4)
        self.assertEqual(C.G.number_of_nodes(), 10)
