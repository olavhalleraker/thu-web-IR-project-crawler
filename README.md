# 🔍 BiasSearch Crawler - Tsinghua Web Information Retrieval Project

This repository (`thu-web-IR-project-crawler`) provides the web crawling component for the **BiasSearch** project, an AI-powered news article search engine that retrieves and classifies articles **in favor**, **against**, or **neutral** with respect to the user's query. It is developed for the **Web Information Retrieval** course at **Tsinghua University**.

The repository handles:

- **Automated crawling** of news websites through their sitemaps to discover articles
- **Metadata extraction** including article URLs, titles, summaries, image URLs and publication dates
- **Data preparation** by storing articles in structured JSON format for the retrieval system
- **Language filtering** (optional) to maintain English-only content

The crawled articles are used by the search API, in the repository (`thu-web-IR-project-api`), which processes them for retrieval and classification
so frontend web application, in the repository (in a separate repository) ultimately displays them to users based on their query


---

## 📁 Repository Structure


```
thu-web-IR-project-crawler
│
├── articles/                   # Folder containing crawled JSON article data
│
├── crawler/                    # Scrapy project folder
│   ├── __init__.py
│   ├── items.py                # Placeholder for item definitions (not used)
│   ├── middlewares.py          # Optional custom middleware (default behavior)
│   ├── pipelines.py            # Optional processing pipeline (default behavior)
│   ├── settings.py             # Scrapy project settings
│   ├── json_unifier.py         # Utility to merge all individual JSONs into one
│   └── spiders/                # Spider folder (used by scrapy framework)
│       ├── news_crawler.py     # Main Scrapy spider for crawling news articles
│
├── articles_database.json      # JSON output of json_unifier.py
├── scrapy.cfg                  # Scrapy configuration file
├── requirements.txt            # Python dependencies
└── README.md                   # You're reading this!
```
---

## 🔧 Usage Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```
### 2 Generate a scrapy spider based on a template

```bash
scrapy genspider -t [type] [name] [domain]
```

### 3. Run spiders in the `spiders` folder
```bash
scrapy crawl [crawler name] -o [file].[filetype]
```

### 4. Run `news_cralwer.py` spider
```bash
scrapy runspider news_crawler.py -a start_urls=https://example.com/sitemap.xml -a is_sitemap_index=True -a enable_lang_detection=True -o articles/example.json
```

**Configuration Flags:**
- `start_urls`: Initial URL to start crawling from
- `is_sitemap_index`: Set to `True` when crawling a sitemap index
- `enable_lang_detection`: Set to `True` to filter non-English content
- `-o`: Output file to save crawled data
---
## 🔑 Key Components

### 1. News Crawler 🕷️
Implemented in `search.py` The primary spider implementation that:
- Handles both sitemap indexes and individual sitemaps
- Extracts article URLs and metadata
- Implements english language detection (optional)
- Respects robots.txt rules


### 2. JSON unifier 🔗
Implemented in `search.py`, utility script that:
- Combines all individual article JSON files from the `articles/` directory
- Creates a single unified JSON database (`articles_database.json`)
- Maintains proper JSON formatting

### 3. Scrapy Configuration Files ⚙️
- `settings.py`: Configures crawler behavior (user agents, throttling, etc.)
- `middlewares.py`: Custom middleware implementations
- `pipelines.py`: Item processing pipelines (currently minimal)
- `items.py`: Data structure definitions (currently empty)

---
Olav Larsen Halleraker  
Guillermo Rodrigo Pérez  
Project for Web Information Retrieval — Tsinghua University 2024/2025