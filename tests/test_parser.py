import unittest
import sys
import io

from tipy.parser import parse_file
from .util import TipyTest


class TestParser(TipyTest):

    def test_parser(self):
        print('parser test: all')
        for file in self.file_lists:
            if file.endswith(".tip"):
                prog = parse_file("tip_examples/" + file)
                buffer = io.StringIO()
                sys.stdout = buffer
                prog.dump()
                _output = buffer.getvalue()
                sys.stdout = sys.__stdout__


if __name__ == '__main__':
    unittest.main()
