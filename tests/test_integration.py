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

import subprocess
import unittest
import os
import sys

from dwave.cloud.utils import retried

project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# These are integration tests used to validate example run successfully with other integrated systems
# It is designed to run from any other directory than current directory

class IntegrationTests(unittest.TestCase):

    @retried(retries=3)
    def test_equivalence(self):
        example_file = os.path.join(project_dir, 'equivalence.py')
        output = subprocess.check_output([sys.executable, example_file])
        output = output.decode('utf-8').upper() # Bytes to str
        if os.getenv('DEBUG_OUTPUT'):
            print("Example output \n" + output)

        with self.subTest(msg="Verify if output contains 'CIRCUITS ARE EQUIVALENT' \n"):
            self.assertIn("circuits are equivalent".upper(), output)

if __name__ == '__main__':
    unittest.main()