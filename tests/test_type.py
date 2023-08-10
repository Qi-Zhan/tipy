import unittest

from tipy.parser import parse
from tipy.analysis import TypeAnalysis
from tipy.ast import Id
from tipy.type import *
from tipy.util import TypeError

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

    def test_error(self):
        prog = """
        main() {
            var x, y;
            x = input;
            y = alloc x;
            x = x + y;
            return 0;
        }
        """
        prog = parse(prog)
        self.assertException(TypeAnalysis.run, TypeError, prog)

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
        # success if no max recursion depth exceeded
        TypeAnalysis.run(prog)

    def test_hard(self):
        prog = """
        foo (p,x) {
            var f, q;
            if (*q == 0) {
                f = 1;
            } else {
                q  = alloc 0;
                *q = (*p) - 1;
                f = (*p)*(x(q, x));
            }
            return f;
        }

        main() {
            var n;
            n = input;
            return foo(&n, foo);
        }
        """
        prog = parse(prog)
        result = TypeAnalysis.run(prog)
        for expr in result.map2expr.values():
            if isinstance(expr, Id):
                match expr.value:
                    case 'p' | 'q':
                        self.assertEqual(
                            result.get_type(expr), PointerType(IntType()))
                    case 'x':
                        x = result.get_type(expr)
                        self.assertIsInstance(x, RecursionType)
                        self.assertIsInstance(x.type_, FunctionType)
                    case 'foo':
                        foo = result.get_type(expr)
        self.assertEqual(foo, x)


if __name__ == '__main__':
    unittest.main()
