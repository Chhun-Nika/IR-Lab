import re
from urllib.parse import parse_qsl, urljoin, urlsplit, urlunsplit

from .books import BooksSpider


LISTING_PATHS = {"/", "/catalogue/page-2.html"}


class BooksGraphSpider(BooksSpider):
    name = "books_graph"
    custom_settings = {
        "CONCURRENT_REQUESTS": 1,
        "DEPTH_LIMIT": 2,
        "DEPTH_PRIORITY": 1,
        "SCHEDULER_MEMORY_QUEUE": "scrapy.squeues.FifoMemoryQueue",
        "SCHEDULER_DISK_QUEUE": "scrapy.squeues.PickleFifoDiskQueue",
        "RETRY_ENABLED": False,
        "REDIRECT_ENABLED": False,
        "METAREFRESH_ENABLED": False,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.listing_urls = set(self.start_urls)
        self.book_urls = set()

    @staticmethod
    def scoped_url(page_url, href):
        """Normalize a link and keep only the two listings or direct book URLs."""
        try:
            parts = urlsplit(urljoin(page_url, href))
        except ValueError:
            return None
        if parts.scheme != "https" or parts.netloc.lower() != "books.toscrape.com":
            return None
        for key, _ in parse_qsl(parts.query, keep_blank_values=True):
            key = key.lower()
            if key != "utm" and not key.startswith("utm_"):
                return None
        path = "/" if parts.path in ("", "/index.html") else parts.path
        if path not in LISTING_PATHS and not re.fullmatch(
            r"/catalogue/[^/]+/index\.html", path
        ):
            return None
        return urlunsplit(("https", "books.toscrape.com", path, "", ""))

    def parse(self, response):
        for href in response.css("article.product_pod h3 a::attr(href)").getall():
            if len(self.book_urls) >= 6:
                break
            url = self.scoped_url(response.url, href)
            if url is None or url in self.book_urls or urlsplit(url).path in LISTING_PATHS:
                continue
            self.book_urls.add(url)
            yield response.follow(url, callback=self.parse_book)

        href = response.css("li.next a::attr(href)").get()
        if href and len(self.listing_urls) < 2:
            url = self.scoped_url(response.url, href)
            second_listing = urljoin(self.start_urls[0], "catalogue/page-2.html")
            if url == second_listing and url not in self.listing_urls:
                self.listing_urls.add(url)
                yield response.follow(url, callback=self.parse)
