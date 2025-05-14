import scrapy
from lxml import etree
from io import BytesIO
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
import random
import time

# List of user agents to randomize requests and avoid detection
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
]

TIME_SLEEP = 0.7

class NewsSpider(scrapy.Spider):
    name = "news_crawler"
    
    # Flags to determine sitemap type and language filtering
    is_sitemap_index = False
    enable_lang_detection = False
    allowed_domains = None
    start_urls = None
    
    def __init__(self, *args, **kwargs):
        super(NewsSpider, self).__init__(*args, **kwargs)
        # Get flags from kwargs
        self.is_sitemap_index = kwargs.get('is_sitemap_index', self.is_sitemap_index) in ['True', True, 'true', '1']
        self.enable_lang_detection = kwargs.get('enable_lang_detection', self.enable_lang_detection) in ['True', True, 'true', '1']
        
        # Initialize start URLs
        start_urls_arg = kwargs.get('start_urls')
        if start_urls_arg:
            self.start_urls = [start_urls_arg]
        else:
            self.start_urls = []

    def start_requests(self):
        # Make initial request(s) with a randomized User-Agent
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                headers={'User-Agent': random.choice(USER_AGENTS)}
            )

    def parse(self, response):
        # Parse XML sitemap or sitemap index
        try:
            tree = etree.parse(BytesIO(response.body))
        except Exception as e:
            self.logger.error(f"Failed to parse XML: {e}")
            return

        ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

        if self.is_sitemap_index:
            # If this is a sitemap index, fetch all nested sitemaps
            for sitemap in tree.xpath("//sm:sitemap", namespaces=ns):
                loc = sitemap.find("sm:loc", ns)
                if loc is not None and loc.text:
                    yield scrapy.Request(
                        url=loc.text,
                        callback=self.parse_sitemap,
                        headers={'User-Agent': random.choice(USER_AGENTS)}
                    )
        else:
            # Otherwise, parse it directly as a sitemap
            yield from self.parse_sitemap(response)

    def parse_sitemap(self, response):
        # Parse individual sitemap and extract article URLs
        try:
            tree = etree.parse(BytesIO(response.body))
        except Exception as e:
            self.logger.error(f"Failed to parse sitemap XML: {e}")
            return

        ns = {
            'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9',
            'image': 'http://www.google.com/schemas/sitemap-image/1.1',
        }

        for url in tree.xpath("//sm:url", namespaces=ns):
            loc = url.find("sm:loc", ns)
            lastmod = url.find("sm:lastmod", ns)
            image = url.find("image:image/image:loc", ns)
            title = url.find("sm:title", ns)

            article_url = loc.text if loc is not None else None

            if article_url:
                yield scrapy.Request(
                    url=article_url,
                    callback=self.parse_article,
                    headers={'User-Agent': random.choice(USER_AGENTS)},
                    meta={
                        "url": article_url,
                        "lastmod": lastmod.text if lastmod is not None else None,
                        "image_url": image.text if image is not None else None,
                        "title": title.text if title is not None else None
                    }
                )

    def parse_article(self, response):
        # Wait a short, random time to avoid hammering servers
        time.sleep(TIME_SLEEP)

        # Extract article title and summary
        title = response.meta["title"]
        if title == None:
            title = response.css("head > title::text").get()
        summary = response.css('meta[name="description"]::attr(content)').get()
        
        if not summary:
            summary = response.css("p::text").get()

        # Optional: filter out non-English content
        if self.enable_lang_detection:
            lang_attr = response.xpath("//html/@lang").get()
            text_for_lang_check = summary or title

            if lang_attr and not lang_attr.startswith("en"):
                return

            if not lang_attr and text_for_lang_check:
                try:
                    language = detect(text_for_lang_check)
                    if language != "en":
                        return
                except LangDetectException:
                    return

        # Yield extracted article data
        yield {
            "url": response.meta["url"],
            "lastmod": response.meta["lastmod"],
            "image_url": response.meta["image_url"],
            "title": title,
            "summary": summary,
        }
