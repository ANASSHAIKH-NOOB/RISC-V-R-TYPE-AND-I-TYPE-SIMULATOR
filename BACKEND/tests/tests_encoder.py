import unittest
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from encoder import encode_r, encode_i
import isa_tables


class TestEncoder(unittest.TestCase):
    def test_encode_r_matches_tables(self):
        word = encode_r('ADD', 1, 2, 3)
        self.assertIsInstance(word, int)
        self.assertEqual(word & 0x7F, isa_tables.OPCODES['ADD'])

    def test_encode_i_matches_tables(self):
        word = encode_i('ADDI', 1, 2, 5)
        self.assertIsInstance(word, int)
        self.assertEqual(word & 0x7F, isa_tables.OPCODES['ADDI'])


if __name__ == '__main__':
    unittest.main()

