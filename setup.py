from setuptools import setup
setup(
    name = "overhead",
    version = "0.0.1",
    description = "A network scan detector based on analysis of netflow data.", 
    author = "Shervin Hajiesmaili",
    author_email = "shervin.h.esmaili@gmail.com",
    py_modules = ['main'],
    packages = ['overhead'],
    entry_points = {
        'console_scripts': ['overhead = main:main']})
