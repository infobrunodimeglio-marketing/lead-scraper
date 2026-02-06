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
        try:
            # backend='api' is usually faster/more stable for simple text search
            # timelimit='m' corresponds to last month (~30 days)
            ddgs_gen = self.ddgs.text(query, timelimit=days, max_results=max_results, backend='api')
            for r in ddgs_gen:
                results.append(r)
        except Exception as e:
            logger.error(f"Error during search: {e}")
        
        return results

    def extract_emails(self, text):
        """Extract emails from text using regex."""
        # Standard email regex
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = set(re.findall(email_pattern, text))
        # Filter out common junk emails if needed (optional)
        return list(emails)

    def scrape_url(self, url):
        """
        Visit the URL and extract emails and main text.
        This is a 'best effort' scraper.
        """
        try:
            headers = {'User-Agent': self.ua.random}
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                text = soup.get_text(separator=' ', strip=True)
                emails = self.extract_emails(text)
                snippet = text[:500] + "..." if len(text) > 500 else text # First 500 chars as content preview
                return emails, snippet
        except Exception as e:
            logger.warning(f"Failed to scrape {url}: {e}")
        
        return [], ""

    def process_leads(self, activity, problem, sites=None, days='m', max_results=20):
        """
        Orchestrate the search and extraction.
        """
        query = f'{activity} {problem}'
        if sites:
            site_list = [s.strip() for s in sites.split(',')]
            # Constructing a site: operator query might be too long if many sites.
            # Instead, we can append "site:facebook.com OR site:linkedin.com" etc.
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
            
            # Extract basic info found in the search snippet itself
            emails = self.extract_emails(snippet_search)
            
            # Deep scrape (optional - can be slow)
            # For now, let's just rely on the search snippet to be fast, 
            # OR we can visit the page if no email found.
            if not emails and link:
                 # Adding a small delay to be polite
                time.sleep(1) 
                extracted_emails, page_text = self.scrape_url(link)
                emails.extend(extracted_emails)
                if not snippet_search:
                    snippet_search = page_text

            # Clean emails list
            emails = list(set(emails))
            
            # Only add if we perceive it as relevant, or just return everything found
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

if __name__ == "__main__":
    # Test run
    scraper = LeadScraper()
    df = scraper.process_leads("Ristorante", "cercasi cameriere", max_results=5)
    print(df)

