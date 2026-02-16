import asyncio
from typing import List, Set, Dict
from playwright.async_api import async_playwright
from core.config import settings
from urllib.parse import urlparse, urljoin

class CrawlerService:
    def __init__(self, max_depth: int = settings.MAX_CRAWL_DEPTH):
        self.max_depth = max_depth
        self.visited: Set[str] = set()
        self.to_visit: List[Dict] = []
        self.results: List[Dict] = []

    async def crawl(self, start_url: str) -> List[Dict]:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(user_agent=settings.USER_AGENT)
            
            domain = urlparse(start_url).netloc
            self.to_visit.append({"url": start_url, "depth": 0})
            
            limit = 6 # Faster limit for on-the-fly audits
            while self.to_visit and len(self.results) < limit:
                current = self.to_visit.pop(0)
                url = current["url"]
                depth = current["depth"]
                
                if url in self.visited or depth > self.max_depth:
                    continue
                
                self.visited.add(url)
                print(f"Crawling: {url} (Depth: {depth}, Count: {len(self.results)})")
                
                page = await context.new_page()
                
                # Speed Optimization: Block images, css, and fonts
                await page.route("**/*.{png,jpg,jpeg,gif,svg,css,woff,woff2,ttf,otf}", lambda route: route.abort())
                
                try:
                    # Navigate with shorter timeout
                    response = await page.goto(url, wait_until="domcontentloaded", timeout=15000)

                    if not response:
                        continue
                        
                    content = await page.content()
                    metrics = await page.evaluate("""() => {
                        const perf = window.performance.timing;
                        if (!perf || perf.navigationStart === 0) return { ttfb: 300, load_time: 2000 };
                        const ttfb = perf.responseStart > perf.requestStart ? perf.responseStart - perf.requestStart : 300;
                        const load_time = perf.loadEventEnd > perf.navigationStart ? perf.loadEventEnd - perf.navigationStart : 2000;
                        return { ttfb, load_time, lcp: 0, cls: 0 };
                    }""")
                    
                    self.results.append({
                        "url": url,
                        "content": content,
                        "status": response.status,
                        "headers": dict(response.headers),
                        "metrics": {
                            "ttfb": float(metrics.get("ttfb") or 300),
                            "load_time": float(metrics.get("load_time") or 2000)
                        }
                    })
                    
                    if depth < self.max_depth and len(self.results) < limit:
                        links = await page.query_selector_all("a")
                        for link in links:
                            href = await link.get_attribute("href")
                            if href:
                                full_url = urljoin(url, href)
                                parsed_url = urlparse(full_url)
                                if parsed_url.netloc == domain and full_url not in self.visited:
                                    self.to_visit.append({"url": full_url, "depth": depth + 1})

                                    
                except Exception as e:
                    print(f"Error crawling {url}: {e}")
                finally:
                    await page.close()
                    
            await browser.close()
            return self.results
