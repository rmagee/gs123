#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

requirements = ['Click>=6.0', ]

setup_requirements = []

test_requirements = []

setup(
    author="SerialLab, Corp",
    author_email='slab@serial-lab.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    description="Set of python-based tools to convert various GS1 formats "
                "to and from others.",
    entry_points={
        'console_scripts': [
            'gs123=gs123.cli:main',
        ],
    },
    install_requires=requirements,
    license="GNU General Public License v3",
    long_description=readme,
    include_package_data=True,
    keywords='gs123',
    name='gs123',
    packages=find_packages(include=['gs123']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://gitlab.com/serial-lab/gs123',
    version='1.0.2',
    zip_safe=False,
)
