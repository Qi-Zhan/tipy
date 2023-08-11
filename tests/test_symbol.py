import unittest

from tipy.symbol import SymbolTable
from tipy.parser import parse_file, parse
from tipy.util import SymbolError, get_output

from .util import TipyTest


class TestSymbol(TipyTest):

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
        output = get_output(st.show)
        for line in output.split('\n'):
            if line == '':
                continue
            (name, _, _, point_line) = line.split()
            if name == 'a':
                self.assertEqual(point_line, 'line2')
            else:
                self.assertEqual(point_line, 'line1')

    errors = ['err_notdecl.tip', 'err_decl_use.tip',
              'parsing.tip', 'err_notlocal.tip']

    def test_all_file(self):
        for file in self.file_lists:
            if file.endswith(".tip"):
                ast = parse_file("tip_examples/" + file)
                if file not in self.errors:
                    SymbolTable.build(ast)
                else:
                    self.assertException(SymbolTable.build, SymbolError, ast)


if __name__ == '__main__':
    unittest.main()
