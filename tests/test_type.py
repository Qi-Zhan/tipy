import unittest

from tipy.parser import parse_file, parse
from tipy.analysis import TypeAnalysis
from tipy.util import TypeError
from tipy.ast import Id
from tipy.type import *

from .util import TipyTest


class TestType(TipyTest):

    def test_simple(self):
        prog = """
        short() {
            var x, y, z;
            x = input;
            y = alloc x;
            *y = x;
            z = *y;
            return z;
        }
        """
        ast = parse(prog)
        result = TypeAnalysis.run(ast)
        for expr in result.map2expr.values():
            if isinstance(expr, Id):
                match expr.value:
                    case 'x':
                        self.assertEqual(result.get_type(expr), IntType())
                    case 'y':
                        self.assertEqual(result.get_type(
                            expr), PointerType(IntType()))
                    case 'z':
                        self.assertEqual(result.get_type(expr), IntType())
                    case 'short':
                        type_ = FunctionType([], IntType())
                        self.assertEqual(result.get_type(expr), type_)

    def test_general(self):
        prog = """
        store(a,b) {
            *b = a;
            return 0;
        }
        """
        prog = parse(prog)
        result = TypeAnalysis.run(prog)
        for expr in result.map2expr.values():
            if isinstance(expr, Id):
                match expr.value:
                    case 'a':
                        a = result.get_type(expr)
                        self.assertIsInstance(
                            result.get_type(expr), TypeVar)
                    case 'b':
                        b = result.get_type(expr)
                        self.assertIsInstance(
                            result.get_type(expr), PointerType)
                    case 'store':
                        s = result.get_type(expr)
        self.assertEqual(s, FunctionType([a, b], IntType()))

    def test_recurive(self):
        prog = """
        main() {
            var p;
            p = alloc null;
            *p = p;
            return 0;
        }
        """
        prog = parse(prog)
        result = TypeAnalysis.run(prog)
        for expr in result.map2expr.values():
            print(expr)

    def test_hard(self):
        prog = """
        foo (p,x) {
            
        }
        """

    symbol_errors = ['err_notdecl.tip', 'err_decl_use.tip',
                     'parsing.tip', 'err_notlocal.tip']

    errors = []

    # def test_all_file(self):
    #     for file in self.file_lists:
    #         if file.endswith(".tip"):
    #             # ignore symbol table error
    #             if file in self.symbol_errors:
    #                 continue
    #             print(file)
    #             ast = parse_file("tip_examples/" + file)
    #             if file not in self.errors:
    #                 pass
    #                 # TypeAnalysis.run(ast)
    #             else:
    #                 self.assertException(TypeAnalysis.run, TypeError, ast)


if __name__ == '__main__':
    unittest.main()
