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
            results = list(self.ddgs.text(query, timelimit=days, max_results=max_results))
            if results: return results
        except Exception as e:
            logger.warning(f"Default search failed: {e}")

        # Strategy 2: HTML Backend (Fallback)
        try:
            logger.info("Trying HTML backend fallback...")
            results = list(self.ddgs.text(query, timelimit=days, max_results=max_results, backend="html"))
            if results: return results
        except Exception as e:
            logger.warning(f"HTML backend failed: {e}")
             
        # Strategy 3: Lite Backend (Last resort)
        try:
            logger.info("Trying Lite backend fallback...")
            results = list(self.ddgs.text(query, max_results=max_results, backend="lite"))
        except Exception as e:
            logger.error(f"All search strategies failed: {e}")

        return results

    def extract_emails(self, text):
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = set(re.findall(email_pattern, text))
        return list(emails)

    def scrape_url(self, url):
        try:
            headers = {'User-Agent': self.ua.random}
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                text = soup.get_text(separator=' ', strip=True)
                emails = self.extract_emails(text)
                snippet = text[:500] + "..." if len(text) > 500 else text
                return emails, snippet
        except Exception as e:
            logger.warning(f"Failed to scrape {url}: {e}")
        return [], ""

    def process_leads(self, activity, problem, sites=None, days='m', max_results=20):
        # Removing quotes to allow broader search (not exact match only)
        query = f'{activity} {problem}'
        if sites:
            site_list = [s.strip() for s in sites.split(',')]
            if site_list:
                site_query = " OR ".join([f"site:{s}" for s in site_list])
                query += f" ({site_query})"

        logger.info(f"Final Query: {query}")
        
        search_results = self.search_leads(query, days=days, max_results=max_results)
        
        processed_data = []

        for res in search_results:
            title = res.get('title', 'No Title')
            link = res.get('href', '')
            snippet_search = res.get('body', '')
            
            emails = self.extract_emails(snippet_search)
            
            if not emails and link:
                time.sleep(1) 
                extracted_emails, page_text = self.scrape_url(link)
                emails.extend(extracted_emails)
                if not snippet_search:
                    snippet_search = page_text

            emails = list(set(emails))
            
            processed_data.append({
                'Activity': activity,
                'Problem': problem,
                'Source Title': title,
                'URL': link,
                'Snippet': snippet_search,
                'Emails': ", ".join(emails) if emails else "Not Found",
                'Date Found': pd.Timestamp.now().strftime('%Y-%m-%d')
            })
            
        return pd.DataFrame(processed_data)




