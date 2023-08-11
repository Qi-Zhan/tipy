import unittest
import sys
import io

from tipy.parser import parse_file
from tipy.visitor import AstVisitor

from .util import TipyTest


class TestParser(TipyTest):

    def test_parser(self):
        visitor = AstVisitor()
        buffer = io.StringIO()
        sys.stdout = buffer
        for file in self.file_lists:
            if file.endswith(".tip"):
                prog = parse_file("tip_examples/" + file)
                prog.dump()
                visitor.visit_program(prog) # test that it doesn't crash
                _output = buffer.getvalue()
        sys.stdout = sys.__stdout__


if __name__ == '__main__':
    unittest.main()
