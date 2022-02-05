from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'A simple python protocol for working with disposable email clients'
LONG_DESCRIPTION = ''

# Setting up
setup(
    name="disposable_email",
    version=VERSION,
    author="AJ Anderson",
    author_email="ajanderson1@gmail.com",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'disposableEmail'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
