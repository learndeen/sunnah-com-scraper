import requests
from bs4 import BeautifulSoup
import json
import time
import os

class SunnahScraper:
    BASE_URL = "https://sunnah.com"
    
    def __init__(self, output_dir="data"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
    def get_soup(self, url):
        """Helper to fetch page and return BeautifulSoup object."""
        try:
            print(f"Fetching {url}...")
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'})
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    def get_collections(self):
        """Fetch all collections from the home page."""
        soup = self.get_soup(self.BASE_URL)
        if not soup:
            return []
            
        collections = []
        # Identifying collection links - usually in a specific container locally
        # Based on exploration, looking for links in .collection_title or similar
        # For robustness, we'll look for the main collection blocks
        
        # Try to find the distinct collection tiles
        collection_elements = soup.select('.collection_title a')
        if not collection_elements:
             # Fallback: try looking for any links that look like collections (div with class collection_title)
             collection_divs = soup.select('div.collection_title')
             for div in collection_divs:
                 a = div.find('a')
                 if a:
                     collection_elements.append(a)

        for link in collection_elements:
            href = link.get('href')
            name = link.get_text(strip=True)
            if href and not href.startswith('http'): # Internal link
                collections.append({
                    "name": name,
                    "slug": href.strip('/'),
                    "url": self.BASE_URL + href
                })
        
        return collections

    def get_books(self, collection_slug):
        """Fetch all books for a given collection."""
        url = f"{self.BASE_URL}/{collection_slug}"
        soup = self.get_soup(url)
        if not soup:
            return []
            
        books = []
        # Books are usually listed as div.book_title or distinct blocks
        # We will look for links that follow pattern /{collection_slug}/{number}
        
        # Strategy: Look for the book info containers
        book_divs = soup.select('.book_title') 
        
        # If .book_title works
        for div in book_divs:
            a = div.find('a')
            if not a:
                # Sometimes the div itself might be clickable or different structure
                continue
                
            # The structure usually is <div class="book_title"><a href="/bukhari/1">...</a></div>
            # Or <div class="book_info">...</div>
            
            # Use specific extraction
            href = a.get('href')
            title = a.get_text(strip=True)
            
            # Extract book number from href usually /slug/number
            if href:
                parts = href.strip('/').split('/')
                if len(parts) >= 2:
                    book_number = parts[-1]
                    books.append({
                        "number": book_number,
                        "title": title,
                        "url": self.BASE_URL + href
                    })
                    
        # Fallback if specific classes failed, look for book range links (common in sunnah.com)
        if not books:
             # Try finding all links that match the pattern
             pass # For now, assume the class selector works as observed in sibling sites

        return books

    def get_hadiths(self, collection_slug, book_number):
        """Fetch all hadiths from a book page."""
        url = f"{self.BASE_URL}/{collection_slug}/{book_number}"
        soup = self.get_soup(url)
        if not soup:
            return []
            
        hadiths = []
        hadith_containers = soup.select('.actualHadithContainer')
        
        for container in hadith_containers:
            hadith_data = {}
            
            # English Text
            english_node = container.select_one('.english_hadith_full')
            if english_node:
                hadith_data['text_en'] = english_node.get_text(strip=True)
            
            # Arabic Text
            arabic_node = container.select_one('.arabic_hadith_full')
            if arabic_node:
                hadith_data['text_ar'] = arabic_node.get_text(strip=True)
                
            # References
            # References are often in a table at the bottom of the container
            ref_table = container.select_one('.hadith_reference')
            if ref_table:
                # Parsing key-value pairs from the reference table
                refs = {}
                rows = ref_table.find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) == 2:
                        key = cols[0].get_text(strip=True).strip(':')
                        val = cols[1].get_text(strip=True)
                        refs[key] = val
                hadith_data['references'] = refs
            
            # Chapter header (sometimes it's before the hadith)
            # This is tricky as chapter headers are siblings to hadith containers usually
            # Getting previous sibling with class .chapter might work if we iterate all children
            
            if hadith_data:
                hadiths.append(hadith_data)
                
        return hadiths

    def run(self, collection_limit=None, book_limit=None, collection_slug=None):
        """Run the scraper."""
        print("Starting scraper...")
        collections = self.get_collections()
        
        if collection_slug:
            collections = [c for c in collections if c['slug'] == collection_slug]
            if not collections:
                print(f"Error: Collection with slug '{collection_slug}' not found.")
                return
        
        print(f"Found {len(collections)} collections to process.")
        
        if collection_limit and not collection_slug:
            collections = collections[:collection_limit]
            
        for collection in collections:
            print(f"\nProcessing Collection: {collection['name']}")
            books = self.get_books(collection['slug'])
            print(f"Found {len(books)} books in {collection['name']}.")
            
            if book_limit:
                books = books[:book_limit]
            
            for book in books:
                print(f"  Scraping Book {book['number']}: {book['title']}")
                hadiths = self.get_hadiths(collection['slug'], book['number'])
                print(f"  Found {len(hadiths)} hadiths.")
                
                # Save data
                filename = f"{collection['slug']}_{book['number']}.json"
                filepath = os.path.join(self.output_dir, filename)
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump({
                        "collection": collection,
                        "book": book,
                        "hadiths": hadiths
                    }, f, ensure_ascii=False, indent=2)
                
                time.sleep(1) # Be polite
                
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Scrape Sunnah.com")
    parser.add_argument("--collections", type=int, default=1, help="Limit number of collections to scrape (default: 1)")
    parser.add_argument("--books", type=int, default=1, help="Limit number of books per collection (default: 1)")
    parser.add_argument("--slug", type=str, help="Scrape a specific collection by slug (e.g., 'muslim', 'bukhari')")
    parser.add_argument("--all", action="store_true", help="Scrape everything (overrides limits)")
    
    args = parser.parse_args()
    
    scraper = SunnahScraper()
    
    if args.all:
        scraper.run(collection_slug=args.slug)
    else:
        scraper.run(collection_limit=args.collections, book_limit=args.books, collection_slug=args.slug)
