import scrapy, re

class CopticSpider(scrapy.Spider):
    name = "new_coptic_spider"
    allowed_domains = [
        # "copticchurch.net",
        "copticscriptorium.org"
    ]
    start_urls = [
        # "https://www.copticchurch.net/coptic_language",  # Coptic Alphabet page
        # "https://www.copticchurch.net/coptic_language/learn-common-greetings",  # Common Greetings page
        "https://copticscriptorium.org"
    ]

    visited_urls = set()
    coptic_unicode_re = re.compile(r"[\u2C80-\u2CFF\u0370-\u03FF\u0300-\u036F]+")

    def parse(self, response):
        page_title = response.css("h1::text").get() or "Untitled"

        # Ensure we are only visiting a page once (in case of pagination or multiple links)
        if response.url in self.visited_urls:
            return
        self.visited_urls.add(response.url)

        # Parsing for "Learn Common Greetings"
        if "learn-common-greetings" in response.url:
            self.logger.info(f"Scraping common greetings from {response.url}")

            # Extract English and Coptic text from <p> tags
            english_text = response.css('p.MsoNormal::text').getall()
            coptic_text = response.css('p.coptic::text').getall()

            # Clean the extracted text
            english_text = [text.strip() for text in english_text if text.strip()]
            coptic_text = [text.strip() for text in coptic_text if text.strip()]

            # Ensure that both lists are the same length (i.e., each English text has a corresponding Coptic text)
            if len(english_text) == len(coptic_text):
                greetings = [
                    {
                        "english": english,
                        "coptic": coptic
                    }
                    for english, coptic in zip(english_text, coptic_text)
                    if self.coptic_unicode_re.search(coptic)  # Ensure valid Coptic text
                ]

                if greetings:
                    yield {
                        "title": page_title,
                        "content": greetings,
                    }
                else:
                    self.logger.info(f"No valid Coptic text found on {response.url}")

        # Parsing for "Coptic Alphabet" page
        elif "coptic_language" in response.url:
            self.logger.info(f"Scraping Coptic alphabet from {response.url}")

            # Extract Coptic letters from the alphabet page
            coptic_letters = response.css("font.coptic::text").getall()

            # Filter Coptic content (ensuring we capture only Coptic Unicode characters)
            coptic_text = [letter.strip() for letter in coptic_letters if self.coptic_unicode_re.search(letter)]

            if coptic_text:
                yield {
                    "title": page_title,
                    "content": coptic_text,
                }
            else:
                self.logger.info(f"No Coptic letters found on {response.url}")
        
        # Follow additional links if necessary (pagination or additional pages)
        for next_page in response.css("a::attr(href)").getall():
            if "coptic" in next_page or next_page.startswith("/"):
                yield response.follow(next_page, self.parse)