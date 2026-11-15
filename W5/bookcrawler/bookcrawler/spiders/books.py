import hashlib, re, scrapy

RATINGS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def __init__(self, max_pages=2, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_pages = max(1, int(max_pages))
        self.pages_seen = 0

    def parse(self, response):
        self.pages_seen += 1
        # TODO: for each card, yield response.follow(href, callback=self.parse_book)
        cards = response.css("article.product_pod")
        for card in cards:
            href = card.css("h3 a::attr(href)").get()
            if href:
                yield response.follow(href, callback=self.parse_book)
        # TODO: if pages_seen < max_pages, follow li.next a
        if self.pages_seen < self.max_pages:
            next_href = response.css("li.next a::attr(href)").get()
            if next_href:
                yield response.follow(
                    next_href,
                    callback=self.parse
                )

    def parse_book(self, response):
        # TODO: extract full detail fields, clean missing values
        
        title = response.css("div.product_main h1::text").get()
        
        description = " ".join(response.css("#product_description + p::text").getall()).strip()

        category = response.css(
            "ul.breadcrumb li:nth-child(3) a::text"
        ).get()

        price_text = response.css("p.price_color::text").get()
        price_gbp = float(price_text.replace("£", "")) if price_text else None
        
        rating_text = response.css("p.star-rating::attr(class)").get(default="").split()
        rating = RATINGS.get(rating_text[1]) if len(rating_text) > 1 else None
        
        availability = " ".join(response.css("div.product_main p.instock.availability::text").getall()).strip()

        # avoid empty value of either title or description
        text = " ".join(field for field in [title, description] if field)
           
        # TODO: yield an IR-ready dict (see field list above)
        yield {
            "doc_id": response.url,
            "title": title,
            "text": text,
            "description": description,
            "url": response.url,
            "category": category,
            "price_gbp": price_gbp,
            "rating": rating,
            "availability": availability,
            "source": "books.toscrape.com"
        }


  