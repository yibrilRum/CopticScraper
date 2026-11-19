import scrapy
import re

class UniversalCopticSpider(scrapy.Spider):
    name = "universal_coptic_spider"

    # Set domains and start URLs dynamically
    allowed_domains = ["copticscriptorium.org"]
    start_urls = ["https://copticscriptorium.org"]

    # Track visited URLs
    visited_urls = set()

    # Coptic Unicode ranges for detection
    coptic_unicode_re = re.compile(r"[\u2C80-\u2CFF\u0370-\u03FF\u0300-\u036F]+")

    def __init__(self, urls=None, *args, **kwargs):
        """
        Allow URLs to be passed dynamically when starting the spider.
        Usage:
            scrapy crawl universal_coptic_spider -a urls="https://example.com,https://another.com"
        """
        super().__init__(*args, **kwargs)
        if urls:
            self.start_urls = urls.split(",")
            self.allowed_domains = [url.split("//")[-1].split("/")[0] for url in self.start_urls]

    def parse(self, response):
        # Avoid duplicate visits
        if response.url in self.visited_urls:
            return
        self.visited_urls.add(response.url)

        # Extract page title for reference
        page_title = response.css("title::text").get() or response.url

        # Find all visible text in the HTML
        all_text = response.xpath("//text()").getall()

        # Filter valid Coptic text using the Unicode regex
        coptic_text = [text.strip() for text in all_text if self.coptic_unicode_re.search(text)]

        if coptic_text:
            yield {
                "url": response.url,
                "title": page_title,
                "content": coptic_text,
            }
        else:
            self.logger.info(f"No Coptic text found on {response.url}")

        # Follow links to crawl more pages
        for next_page in response.css("a::attr(href)").getall():
            # Normalize relative links
            next_page = response.urljoin(next_page)
            if next_page not in self.visited_urls:
                yield scrapy.Request(next_page, callback=self.parse)