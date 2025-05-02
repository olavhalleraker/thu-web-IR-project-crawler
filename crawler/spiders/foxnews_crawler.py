import scrapy
from lxml import etree
from io import BytesIO


class FoxNewsSpider(scrapy.Spider):
    name = "foxnews_crawler"
    allowed_domains = ["foxnews.com"]
    start_urls = ["https://www.foxnews.com/sitemap.xml?type=articles"]

    def parse(self, response):
        # Parse XML sitemap manually with lxml
        try:
            tree = etree.parse(BytesIO(response.body))
        except Exception as e:
            self.logger.error(f"Failed to parse XML: {e}")
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
        # Extract title and summary
        title = response.css("head > title::text").get()
        summary = response.css('meta[name="description"]::attr(content)').get()

        if not summary:
            summary = response.css("p::text").get()  # fallback: first paragraph

        yield {
            "url": response.meta["url"],
            "lastmod": response.meta["lastmod"],
            "image_url": response.meta["image_url"],
            "title": title,
            "summary": summary,
        }
