from collections import OrderedDict
from time import time
import unittest

try:
    from django.test.runner import DiscoverRunner
except ImportError:
    raise("Django 1.8 or 1.9 needs to be installed to use this test runner.")

from .tabulate import tabulate

class Bcolors:
    MAGENTA = '\033[95m'
    BLUE = '\033[1;94m'
    TURQ = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''

def get_color(runtime, longest_test):
    """
    Returns color based on test time.
    Tests under .5s get GREEN
    Tests higher than .5 are divided into three segments
        slow, painful, agonizing
        Yellow, Magenta, Red
    """
    if runtime < .5:
        return Bcolors.GREEN
    segment = ((longest_test - .5) / 3)
    runtime -= .5
    if runtime <= segment:
        return Bcolors.YELLOW
    elif runtime <= segment * 2:
        return Bcolors.MAGENTA
    return Bcolors.RED

class BenchTextTestResult(unittest.TextTestResult):
    """Overrides TextTestRunner to add benchmartk tool"""

    def __init__(self, *args, **kwargs):

        self.benchmark = kwargs.pop('benchmark')
        super(BenchTextTestResult, self).__init__(*args, **kwargs)
        self.bench_dict = OrderedDict()


    def startTestRun(self):
        pass


    def write_totals(self, table, class_name, totals):

        table.append({
            "Test": "---------------------------",
            "Runtime": "-------",
            "Percent": "-------",
        })
        table.append({
            "Test": "{}{}{}".format(Bcolors.TURQ, class_name, Bcolors.END),
            "Runtime": "{0}{1:.5f}{2}".format(
                Bcolors.TURQ, totals['runtime'], Bcolors.END
            ),
            "Percent": "{}{:>7.2f}%{}".format(
                Bcolors.TURQ, totals['percent'], Bcolors.END)
        })



    def stopTestRun(self):

        if not self.benchmark:
            return

        total_run_time = 0
        longest_test = 0

        # Loop through tests to get total run time
        for class_name, runtimes in self.bench_dict.items():
            runtimes['runtime'] = runtimes['stop'] - runtimes['start']
            total_run_time += runtimes['runtime']
            longest_test = max(longest_test, runtimes['runtime'])

        table = list()
        totals = {'runtime': 0, 'percent': 0}

        class_name = ''
        for full_path, runtimes in self.bench_dict.items():
            runtime = runtimes['runtime']
            color = get_color(runtime, longest_test)

            # Write header/divider for new class
            if class_name != runtimes['class_name']:

                if totals['runtime'] > 0:
                    self.write_totals(table, class_name, totals)
                    totals = {'runtime': 0, 'percent': 0}

                class_name = runtimes['class_name']
                module = runtimes['module']
                table.append({})
                table.append({"Test": "{}{}.{}{}".format(
                    Bcolors.BLUE, module, class_name, Bcolors.END
                )})



            percent = runtime / total_run_time * 100
            totals['runtime'] += runtime
            totals['percent'] += percent
            table.append({
                "Test": ": " + runtimes['test_name'],
                "Runtime": "{0}{1:.5f}{2}".format(
                    color, runtime, Bcolors.END
                ),
                "Percent": "{:>7.2f}%".format(percent)
            })

        self.write_totals(table, class_name, totals)

        self.stream.writeln()
        self.stream.writeln()
        self.stream.writeln(tabulate(
            table,
            headers="keys",
            aligns=('left', 'right', 'right')
        ))

    def parseTest(self, test):
        module = test.__module__
        class_name = test.__class__.__name__
        test_name = test._testMethodName
        uniq = "{}.{}.{}".format(module, class_name, test_name)
        return uniq, module, class_name, test_name

    def startTest(self, test):
        # Run at start of each test method

        uniq, module, class_name, test_name = self.parseTest(test)

        self.bench_dict[uniq] = {
            'start': time(),
            'test_name': test_name,
            'class_name': class_name,
            'module': module,
        }
        super(BenchTextTestResult, self).startTest(test)

    def stopTest(self, test):
        uniq, module, class_name, test_name = self.parseTest(test)

        super(BenchTextTestResult, self).stopTest(test)
        self.bench_dict[uniq]['stop'] = time()


class BenchTextTestRunner(unittest.TextTestRunner):
    """Overrides TextTestRunner to add benchmartk tool"""

    resultclass = BenchTextTestResult

    def __init__(self, *args, **kwargs):

        self.benchmark = kwargs.pop('benchmark')
        super(BenchTextTestRunner, self).__init__(*args, **kwargs)

    def _makeResult(self):
        return self.resultclass(
            self.stream, self.descriptions, self.verbosity,
            benchmark=self.benchmark
        )


class BenchRunner(DiscoverRunner):

    test_runner = BenchTextTestRunner

    def __init__(self, *args, **kwargs):

        super(BenchRunner, self).__init__(*args, **kwargs)
        self.benchmark = kwargs.get('benchmark', False)


    @classmethod
    def add_arguments(cls, parser):
        super(BenchRunner, cls).add_arguments(parser)
        parser.add_argument('-b', '--benchmark',
            action='store_true', dest='benchmark', default=False,
            help='Record and display a benchark of the run tests.')


    def run_suite(self, suite, **kwargs):
        resultclass = self.get_resultclass()
        return self.test_runner(
            verbosity=self.verbosity,
            failfast=self.failfast,
            resultclass=resultclass,
            benchmark=self.benchmark,
        ).run(suite)
