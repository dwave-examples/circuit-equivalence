# Copyright 2020 D-Wave Systems Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest

from circuits import Circuit
from equivalence import find_isomorphism, find_equivalence

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
        C1 = Circuit("netlists/cmos_nand_1.txt")
        C2 = Circuit("netlists/cmos_nand_error.txt")

        results = find_isomorphism(C1.G, C2.G)
        self.assertEqual(results, None)

    def test_unequal_node_count(self):
        C1 = Circuit("netlists/cmos_nand_1.txt")
        C2 = Circuit("netlists/cmos_nand_missing.txt")

        results = find_isomorphism(C1.G, C2.G)
        self.assertEqual(results, None)

class TestEquivalence(unittest.TestCase):
    def test_equivalent(self):
        C1 = Circuit("netlists/cmos_nand_1.txt")
        C2 = Circuit("netlists/cmos_nand_2.txt")

        results = find_equivalence(C1, C2)
        self.assertNotEqual(results, None)

    def test_not_equivalent(self):
        C1 = Circuit("netlists/cmos_nand_1.txt")
        C2 = Circuit("netlists/cmos_nand_error.txt")

        results = find_equivalence(C1, C2)
        self.assertEqual(results, None)
