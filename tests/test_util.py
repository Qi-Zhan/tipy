import unittest

from tipy.util import typecheck, TypeError

from .util import TipyTest


class TestTypecheck(TipyTest):

    def test_simpl(self):
        @typecheck
        def foo(a: int, b: int):
            return a + b

        self.assertEqual(foo(1, 2), 3)
        self.assertException(foo, TypeError, 1, 2.0)

    def test_single(self):
        @typecheck
        def foo(a, b: int):
            return a

        self.assertEqual(foo('a', 1), 'a')
        self.assertException(foo, TypeError, 'a', 'b')

    def test_keyword(self):
        @typecheck
        def foo(a, b: int):
            return a

        self.assertEqual(foo('a', b=1), 'a')
        self.assertException(foo, TypeError, 'a', b='b')


if __name__ == '__main__':
    unittest.main()
