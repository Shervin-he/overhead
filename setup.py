from setuptools import setup
from overhead import __version__

setup(
    name="overhead",
    version=__version__,
    description="A network scan detector based on analysis of netflow data.",
    author="Shervin Hajiesmaili",
    author_email="shervin.h.esmaili@gmail.com",
    py_modules=['main'],
    packages=['overhead'],
    entry_points={
        'console_scripts': ['overhead = main:main']})
