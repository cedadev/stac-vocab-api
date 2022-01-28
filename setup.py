# encoding: utf-8
"""

"""
__author__ = 'Rhys Evans'
__date__ = '01 Jan 2022'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'rhys.r.evans@stfc.ac.uk'

from setuptools import setup, find_namespace_packages

with open("README.md") as readme_file:
    _long_description = readme_file.read()

setup(
    name='stac_vocab_api',
    description='stac-vocab-api',
    author='Richard Smith',
    url='https://github.com/cedadev/stac-vocab-api/',
    long_description=_long_description,
    long_description_content_type='text/markdown',
    license='BSD - See asset_extractor/LICENSE file for details',
    packages=find_namespace_packages(),
    python_requires='>=3.5',
    package_data={
        'stac_vocab_api': [
            'LICENSE'
        ]
    },
    install_requires=[
        'attrs',
        'fastapi',
    ],
    extras_require={
        'server': ["uvicorn[standard]>=0.12.0,<0.14.0"],
        'dev': [
            'pytest',
            'requests'
        ]
    },
    entry_points={
    }
)