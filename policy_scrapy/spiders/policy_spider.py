import scrapy
import pandas as pd
from pathlib import Path
from urllib.parse import urlparse, urljoin
from scrapy_playwright.page import PageMethod


class PolicySpider(scrapy.Spider):
    name = "policy_spider"

    custom_settings = {
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "PLAYWRIGHT_BROWSER_TYPE": "chromium",
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 45000,
        "LOG_LEVEL": "INFO"
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        base_path = Path(__file__).resolve().parent.parent.parent
        self.input_file = base_path / "domains.csv"
        self.keyword_file = base_path / "keywords.txt"
        self.output_file = base_path / "subdirectories.csv"
        self.results = {}
        self.processed_domains = set()

        self._load_domains()
        self._load_keywords()

    def _load_domains(self):
        self.domains = pd.read_csv(self.input_file)["domain"].dropna().tolist()
        for domain in self.domains:
            self.results[domain] = []

    def _load_keywords(self):
        with open(self.keyword_file, "r") as f:
            self.keywords = [line.strip().lower() for line in f if line.strip()]

    def start_requests(self):
        for domain in self.domains:
            url = f"https://{domain}"
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={
                    "playwright": True,
                    "playwright_page_methods": [PageMethod("wait_for_selector", "a")],
                    "domain": domain
                },
                errback=self.errback,
                dont_filter=True
            )

    def parse(self, response):
        domain = response.meta["domain"]
        url = response.url
        self.logger.info(f"Parsing {domain}: {url}")

        try:
            for href in response.css("a::attr(href)").getall():
                abs_url = urljoin(url, href)
                parsed = urlparse(abs_url)

                base_netloc = urlparse(f"https://{domain}").netloc.replace("www.", "")
                link_netloc = parsed.netloc.replace("www.", "")

                if link_netloc != base_netloc:
                    continue

                path = parsed.path.rstrip("/")
                if any(kw in path.lower() for kw in self.keywords):
                    if path and path not in self.results[domain]:
                        self.results[domain].append(path)

        except Exception as e:
            self.logger.error(f"Error parsing {domain}: {e}")

        self.processed_domains.add(domain)

    def errback(self, failure):
        domain = failure.request.meta.get("domain")
        self.logger.error(f"Error fetching {domain}: {failure}")
        if domain:
            self.processed_domains.add(domain)

    def closed(self, reason):
        self.logger.info(f"Spider closed: {reason}")
        self.write_results()

    def write_results(self):
        rows = []
        for domain in self.domains:
            paths = self.results.get(domain, [])
            rows.append([domain] + paths)
        pd.DataFrame(rows).to_csv(self.output_file, index=False, header=False)
        self.logger.info(f"Results written to: {self.output_file}")