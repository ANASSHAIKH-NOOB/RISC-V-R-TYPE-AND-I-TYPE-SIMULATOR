import unittest
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from assembler import assemble


class TestAssembler(unittest.TestCase):
    def test_basic_r_type_encoding(self):
        instrs = assemble('add x1, x2, x3')
        self.assertEqual(len(instrs), 1)
        self.assertIn('binary', instrs[0])

    def test_basic_i_type_encoding(self):
        instrs = assemble('addi x1, x2, 5')
        self.assertEqual(len(instrs), 1)
        self.assertIn('binary', instrs[0])


if __name__ == '__main__':
    unittest.main()

