scraper.py


import re
import time
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
import pandas as pd
from fake_useragent import UserAgent
import logging
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
class LeadScraper:
    def __init__(self):
        self.ua = UserAgent()
        self.ddgs = DDGS()
    def search_leads(self, query, days='m', max_results=20):
        """
        Search for leads using DuckDuckGo.
        days: 'd' (day), 'w' (week), 'm' (month), 'y' (year)
        """
        logger.info(f"Searching for: {query} with timelimit={days}")
        results = []
        
        # Strategy 1: Default Backend
        try:
            # backend='api' is usually faster/more stable for simple text search
            # timelimit='m' corresponds to last month (~30 days)
            ddgs_gen = self.ddgs.text(query, timelimit=days, max_results=max_results, backend='api')
            for r in ddgs_gen:
                results.append(r)
            results = list(self.ddgs.text(query, timelimit=days, max_results=max_results))
            if results: return results
        except Exception as e:
            logger.error(f"Error during search: {e}")
        
            logger.warning(f"Default search failed: {e}")
        # Strategy 2: HTML Backend (Fallback)
        try:
            logger.info("Trying HTML backend fallback...")
            results = list(self.ddgs.text(query, timelimit=days, max_results=max_results, backend="html"))
            if results: return results
        except Exception as e:
             logger.warning(f"HTML backend failed: {e}")
             
        # Strategy 3: Lite Backend (Last resort, no time filter usually)
        try:
            logger.info("Trying Lite backend fallback...")
            # Lite backend often doesn't support time limits well, so we might drop it or keep it.
            # Let's try keeping it but acknowledging it might fail strict time filtering
            results = list(self.ddgs.text(query, max_results=max_results, backend="lite"))
        except Exception as e:
            logger.error(f"All search strategies failed: {e}")
        return results
    def extract_emails(self, text):
    df = scraper.process_leads("Ristorante", "cercasi cameriere", max_results=5)
    print(df)


