from setuptools import setup
from setuptools.command.test import test as TestCommand
import sys

class PyTest(TestCommand):
    """ This class is copied directly from the docs """

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

setup(
    name = "summonses",
    version = "0.1",
    author = "Kevin Wilson",
    author_email = "khwilson@gmail.com",
    description = ("Analysis of how summonses affect collisions"),
    license = "Apache2",
    keywords = "example data-analysis nyc",
    url = "https://github.com/khwilson/summonses",
    packages=['summonses'],
    long_description=open('README.rst', 'r').read(),
    install_requires=open('requirements.txt', 'r').readlines(),
    tests_require=['pytest'],
    cmdclass={'test': PyTest}
)
