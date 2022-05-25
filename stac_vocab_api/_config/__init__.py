# encoding: utf-8
"""

"""
__author__ = 'Rhys Evans'
__date__ = '01 Jan 2022'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'rhys.r.evans@stfc.ac.uk'

from logging import DEBUG
from os import path, getenv

DEBUG = False
APP_DIR = getenv("APP_DIR", path.dirname(path.dirname(path.realpath(__file__))))
LOGFILE = getenv("LOGFILE", path.join(APP_DIR, "cache", "stac_vocab_api.log"))
CACHE_FILE = getenv("CACHE_FILE", path.join(APP_DIR, "cache", "GRAPH.p"))
CEDA_VOCAB_LOCATION = getenv("CEDA_VOCAB_LOCATION", path.join(APP_DIR, "data", "ceda.xml"))
CACHE_HOURS = getenv("CACHE_HOURS", 1)
