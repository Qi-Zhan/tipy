import unittest


class TipyTest(unittest.TestCase):
    def assertException(self, func, exception, *args):
        try:
            func(*args)
        except exception:
            pass
        else:
            raise Exception(f"Should raise {exception.__name__}")
