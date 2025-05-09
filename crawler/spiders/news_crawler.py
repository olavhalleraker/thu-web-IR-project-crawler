import scrapy
from lxml import etree
from io import BytesIO
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException

class NewsSpider(scrapy.Spider):
    name = "news_crawler"
    
    # Configuration parameters (set these when initializing the spider)
    is_sitemap_index = False  #True if crawling a sitemap index (BBC: https://www.bbc.com/sitemaps/https-index-com-archive.xml), False for direct sitemap (FoxNews: https://www.foxnews.com/sitemap.xml?type=articles)
    enable_lang_detection = False  # True to enable English language detection
    
    # Sset when initializing the spider
    allowed_domains = None
    start_urls = None
    
    def __init__(self, *args, **kwargs):
        super(NewsSpider, self).__init__(*args, **kwargs)
        
        self.is_sitemap_index = kwargs.get('is_sitemap_index', self.is_sitemap_index) in ['True', True, 'true', '1']
        self.enable_lang_detection = kwargs.get('enable_lang_detection', self.enable_lang_detection) in ['True', True, 'true', '1']
        
        # Parse start_urls from command-line string to list
        start_urls_arg = kwargs.get('start_urls')
        if start_urls_arg:
            self.start_urls = [start_urls_arg]
        else:
            self.start_urls = []


    def parse(self, response):
        # Parse XML sitemap manually with lxml
        try:
            tree = etree.parse(BytesIO(response.body))
        except Exception as e:
            self.logger.error(f"Failed to parse XML: {e}")
            return

        ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

        if self.is_sitemap_index:
            # Handle sitemap index (BBC style)
            for sitemap in tree.xpath("//sm:sitemap", namespaces=ns):
                loc = sitemap.find("sm:loc", ns)
                if loc is not None and loc.text:
                    yield scrapy.Request(url=loc.text, callback=self.parse_sitemap)
        else:
            # Handle direct sitemap (FoxNews style)
            yield from self.parse_sitemap(response)

    def parse_sitemap(self, response):
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

            article_url = loc.text if loc is not None else None

            if article_url:
                yield scrapy.Request(
                    url=article_url,
                    callback=self.parse_article,
                    meta={
                        "url": article_url,
                        "lastmod": lastmod.text if lastmod is not None else None,
                        "image_url": image.text if image is not None else None,
                    }
                )

    def parse_article(self, response):
        title = response.css("head > title::text").get()
        summary = response.css('meta[name="description"]::attr(content)').get()
        
        if not summary:
            summary = response.css("p::text").get()

        # Skip non-English articles if language detection is enabled
        if self.enable_lang_detection:
            lang_attr = response.xpath("//html/@lang").get()
            text_for_lang_check = summary or title

            # Use HTML lang attribute first
            if lang_attr and not lang_attr.startswith("en"):
                return

            # Fallback to langdetect only if lang attribute is missing
            if not lang_attr and text_for_lang_check:
                try:
                    language = detect(text_for_lang_check)
                    if language != "en":
                        return
                except LangDetectException:
                    return

        yield {
            "url": response.meta["url"],
            "lastmod": response.meta["lastmod"],
            "image_url": response.meta["image_url"],
            "title": title,
            "summary": summary,
        }