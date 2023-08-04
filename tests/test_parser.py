import unittest
import os
import sys
import io
from tipy.parser import parse_file

class TestParser(unittest.TestCase):
    file_lists = os.listdir("tip_examples")
    def test_parser(self):
        for file in self.file_lists:
            if file.endswith(".tip"):
                print("Parsing " + file)
                prog = parse_file("tip_examples/" + file)
                buffer = io.StringIO()
                sys.stdout = buffer
                prog.dump()
                _output = buffer.getvalue()
                sys.stdout = sys.__stdout__
        

if __name__ == '__main__':
    unittest.main()