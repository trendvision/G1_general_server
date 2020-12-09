# -*- coding: utf-8 -*-

"""
I switched my motto; instead of saying "fuck tomorrow"
That buck that bought a bottle could've struck the lotto.
"""

__author__ = 'Nikolai Tschacher'
__updated__ = '18.08.2018'  # day.month.year
__home__ = 'incolumitas.com'

from GoogleScraperG1.proxies import Proxy
from GoogleScraperG1.config import get_config
import logging

"""
All objects imported here are exposed as the public API of GoogleScraper
"""

from GoogleScraperG1.core import scrape_with_config
from GoogleScraperG1.scraping import GoogleSearchError, MaliciousRequestDetected

logging.getLogger(__name__)
