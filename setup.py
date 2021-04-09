#!/usr/bin/env python
from setuptools import find_packages, setup

# Get the long description from the README file
with open("README.md", "r") as fh:
    long_description = fh.read()

requirements = [
    'aiohttp<4.0',
]

setup(
    name="simple-fbmessenger",
    version="0.1.0",
    author="Soenke Huster",
    author_email="projects@eknoes.de",
    description="An unofficial simple library to provide basic communication with Facebooks Messenger API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/eknoes/simple-fbmessenger",
    license="GPLv3",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        (
            'License :: OSI Approved :: '
            'GNU General Public License v3 (GPLv3)'
        ),
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Communications :: Chat',
        'Topic :: Internet',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    python_requires='>=3.6',
    project_urls={
        'Bug Reports': 'https://github.com/eknoes/simple-fbmessenger/issues',
        'Source': 'https://github.com/eknoes/simple-fbmessenger',
    },
)