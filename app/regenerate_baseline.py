
import asyncio
import os
import sys

# Ensure we can import from current directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.crawler_service import CrawlerService
from services.extractor_service import ExtractorService
from core.config import settings

async def main():
    url = "https://www.bajajlifeinsurance.com/"
    print(f"Starting baseline regeneration for {url}...")
    print(f"Config: Max Depth={settings.MAX_CRAWL_DEPTH}, Max Pages={settings.MAX_PAGES}")
    
    crawler = CrawlerService()
    pages = await crawler.crawl(url) # This uses the wrapper which calls crawl_stream internally
    print(f"Crawled {len(pages)} pages.")
    
    if not pages:
        print("Error: No pages crawled.")
        return

    extractor = ExtractorService()
    try:
        data = await extractor.extract_full_site_data(url, pages)
        path = await extractor.save_baseline(data)
        print(f"Baseline regeneration complete. Saved to {path}")
    except Exception as e:
        print(f"Error during extraction: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
