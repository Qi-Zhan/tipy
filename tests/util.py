import unittest
import os


class TipyTest(unittest.TestCase):
    file_lists = os.listdir("tip_examples")

    def assertException(self, func, exception, *args, **kwargs):
        try:
            func(*args, **kwargs)
        except exception:
            pass
        else:
            raise Exception(f"Should raise {exception.__name__}")
