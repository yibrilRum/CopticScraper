import scrapy, re

class CopticSpider(scrapy.Spider):
    name = "coptic_spider"
    allowed_domains = ["copticchurch.net"]
    start_urls = ["https://www.copticchurch.net/coptic_language"]

    visited_urls = set()

    coptic_unicode_re = re.compile(
        r"[\u2C80-\u2CFF\u0370-\u03FF\u0300-\u036F]+"
    )
    def parse(self, response):
        page_title = response.css("h1::text").get() or "Untitled"
        paragraphs = response.css("font.coptic::text").getall()

        if response.url in self.visited_urls:
            return
        self.visited_urls.add(response.url)

        coptic_text = [
            p.strip() for p in paragraphs if self.coptic_unicode_re.search(p)
        ]

        yield {
            "title": page_title,
            "content": coptic_text,
        }

        for next_page in response.css("a::attr(href)").getall():
            if "coptic" in next_page or next_page.startswith("/"):
                yield response.follow(next_page, self.parse)