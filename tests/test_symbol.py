import os
import unittest

from tipy.symbol import SymbolTable
from tipy.parser import parse_file, parse
from tipy.util import SymbolError

from .util import TipyTest


class TestSymbol(TipyTest):
    file_lists = os.listdir("tip_examples")

    def test_simple(self):
        prog = """main(a) {
            var a;
            a = 1;
            return a;
        } 
        """
        ast = parse(prog)
        st = SymbolTable.build(ast)
        self.assertEqual(len(st.symbols), 3)

    errors = ['err_notdecl.tip', 'err_decl_use.tip',
            'parsing.tip', 'err_notlocal.tip']

    def test_all_file(self):
        print('symbol test: all')
        for file in self.file_lists:
            if file.endswith(".tip"):
                ast = parse_file("tip_examples/" + file)
                if file not in self.errors:
                    SymbolTable.build(ast)
                else:
                    self.assertException(SymbolTable.build, SymbolError, ast)


if __name__ == '__main__':
    unittest.main()
