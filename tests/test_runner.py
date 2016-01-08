from .context import *

import unittest
from django_bench_runner.runner import BenchRunner, Bcolors, get_color

class BenchRunnerSuite(unittest.TestCase):

    def test_benchrunner(self):
        """
        General 'does it run' test.
        """
        b = BenchRunner()
        self.assertEqual(b.benchmark, False)


    def test_colors(self):
        self.assertEqual(get_color(5, 5), Bcolors.RED)
        self.assertEqual(get_color(.2, 5), Bcolors.GREEN)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(BenchRunnerSuite))
    return suite

if __name__ == "__main__":
    unittest.TextTestRunner().run(suite())
