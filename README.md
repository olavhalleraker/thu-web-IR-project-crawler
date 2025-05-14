# thu-web-IR-project-crawler

Basic nice-to-have commands:

```
pip freeze > requirements.txt

scrapy crawl [crawler name] -o [file].[filetype]

scrapy genspider -t [type] [name] [domain]
```

For the updated spider "news_crawler":

```
scrapy crawl news_crawler  -a start_urls=[http://example.com/sitemap.xml] -a allowed_domains=[domain.com] -a is_sitemap_index=True -a enable_lang_detection=True -o [outputfile].[filetype]
```

Install requirements:
```
pip install -r requirements.txt
```

## Scrapes TODO
* https://edition.cnn.com/sitemap/article.xml
* https://www.bbc.com/sitemaps/https-index-com-archive.xml
* Reuters - https://www.reuters.com
* Al Jazeera English - https://www.aljazeera.com
* The Washington Post - https://www.washingtonpost.com
* USA Today -https://www.usatoday.com/robots.txt

## Scrapy docs
https://docs.scrapy.org/en/latest/