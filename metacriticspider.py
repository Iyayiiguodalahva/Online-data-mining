import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

class MetacriticSpiderSelenium(scrapy.Spider):
    name = "metacriticspider"  # Unique identifier for the spider
    allowed_domains = ["metacritic.com"]  # Limits the spider to the specified domain
    start_urls = ["https://www.metacritic.com/browse/movie/"]  # Starting URL for the spider

    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.77 Safari/537.36",
        "ROBOTSTXT_OBEY": False,
        "FEED_URI": 'final.json',  # Specifies where to save the output
        "FEED_FORMAT": 'json'       # Specifies the format of the output file
    }

    def __init__(self, *args, **kwargs):
        super(MetacriticSpiderSelenium, self).__init__(*args, **kwargs)

        # Configure Selenium WebDriver
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Enable headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")

        # Set up the WebDriver
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=chrome_options
        )

    def parse(self, response):
        try:
            self.driver.get(response.url)  # Use WebDriver to navigate to the URL
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.c-finderProductCard"))
            )

            # Handle cookies if the consent pop-up appears
            try:
                cookie_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
                )
                self.logger.info("Cookie consent button found. Clicking...")
                cookie_button.click()
                time.sleep(2)  # Wait for the dialog to close
            except TimeoutException:
                self.logger.info("No cookie consent button found. Proceeding...")

            page_count = 0  # Counter to track the number of pages scraped

            while page_count < 4:  # Limit scraping to the first page
                html = self.driver.page_source
                sel_response = scrapy.http.HtmlResponse(url=self.driver.current_url, body=html, encoding="utf-8")

                movies = sel_response.css("div.c-finderProductCard")
                for movie in movies:
                    title = movie.css('h3.c-finderProductCard_titleHeading span::text').getall()
                    metascores = movie.css('div.c-siteReviewScore span::text').get()
                    url = movie.css("a.c-finderProductCard_container::attr(href)").get()
                    release_date = movie.css("div.c-finderProductCard_meta span.u-text-uppercase::text").get()
                    rated = movie.xpath('.//div[@class="c-finderProductCard_meta"]/span[span[contains(@class, "u-text-capitalize")]]/text()').get()

                    # Ensure the movie URL is joined to form the full URL
                    movie_url = response.urljoin(url) if url else None

                    # Schedule a request to the movie details page
                    if movie_url:
                        yield scrapy.Request(
                            url=movie_url,
                            callback=self.parse_movie_details,
                            meta={
                                "title": " ".join(title).strip() if title else None,
                                "metascores": metascores.strip() if metascores else None,
                                "movie_url": movie_url,
                                "release_date": release_date.strip() if release_date else None,
                                "rated": rated.strip() if rated else None,
                            },
                        )
                try:
                    self.logger.info("Scrolling down the page...")
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)

                    next_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "span.c-navigationPagination_item--next.enabled"))
                    )
                    self.logger.info("Next button found, clicking...")
                    next_button.click()
                    time.sleep(5)
                    page_count += 1  # Increment the page count
                except TimeoutException:
                    self.logger.info("No more pages to navigate.")
                    break
                except Exception as e:
                    self.logger.error(f"An error occurred: {e}", exc_info=True)
                    break

        finally:
            self.driver.quit()  # Ensure the WebDriver is closed

    def parse_movie_details(self, response):
        # Extract metadata passed from the main page
        title = response.meta.get("title")
        metascores = response.meta.get("metascores")
        movie_url = response.meta.get("movie_url")
        release_date = response.meta.get("release_date")
        rated = response.meta.get("rated")
        genre = response.css("span.c-globalButton_label::text").get(default='N/A').strip()
        userscores = response.css('div.c-siteReviewScore_user span[data-v-e408cafe]::text').get(default='N/A').strip()

        # Yield the extracted details
        yield {
            "title": title,
            "release_date": release_date,
            "genre": genre,
            "metascores": metascores,
            "userscores": userscores,
            "rated": rated,
            "movie_url": movie_url,
        }

#this code is for the whole website via the link
"""
import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

class MetacriticSpiderSelenium(scrapy.Spider):
    name = "metacriticspider"  # Unique identifier for the spider
    allowed_domains = ["metacritic.com"]  # Limits the spider to the specified domain
    start_urls = ["https://www.metacritic.com/browse/movie/"]  # Starting URL for the spider

    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.77 Safari/537.36",
        "ROBOTSTXT_OBEY": False,
        "FEED_URI": 'final.json',  # Specifies where to save the output
        "FEED_FORMAT": 'json'       # Specifies the format of the output file
    }

    def __init__(self, *args, **kwargs):
        super(MetacriticSpiderSelenium, self).__init__(*args, **kwargs)

        # Configure Selenium WebDriver
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Enable headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")

        # Set up the WebDriver
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=chrome_options
        )

    def parse(self, response):
        try:
            self.driver.get(response.url)  # Use WebDriver to navigate to the URL
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.c-finderProductCard"))
            )

            # Handle cookies if the consent pop-up appears
            try:
                cookie_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
                )
                self.logger.info("Cookie consent button found. Clicking...")
                cookie_button.click()
                time.sleep(2)  # Wait for the dialog to close
            except TimeoutException:
                self.logger.info("No cookie consent button found. Proceeding...")

            page_count = 0  # Counter to track the number of pages scraped

            while True:  # Limit scraping to the first page
                html = self.driver.page_source
                sel_response = scrapy.http.HtmlResponse(url=self.driver.current_url, body=html, encoding="utf-8")

                movies = sel_response.css("div.c-finderProductCard")
                for movie in movies:
                    title = movie.css('h3.c-finderProductCard_titleHeading span::text').getall()
                    metascores = movie.css('div.c-siteReviewScore span::text').get()
                    url = movie.css("a.c-finderProductCard_container::attr(href)").get()
                    release_date = movie.css("div.c-finderProductCard_meta span.u-text-uppercase::text").get()
                    rated = movie.xpath('.//div[@class="c-finderProductCard_meta"]/span[span[contains(@class, "u-text-capitalize")]]/text()').get()

                    # Ensure the movie URL is joined to form the full URL
                    movie_url = response.urljoin(url) if url else None

                    # Schedule a request to the movie details page
                    if movie_url:
                        yield scrapy.Request(
                            url=movie_url,
                            callback=self.parse_movie_details,
                            meta={
                                "title": " ".join(title).strip() if title else None,
                                "metascores": metascores.strip() if metascores else None,
                                "movie_url": movie_url,
                                "release_date": release_date.strip() if release_date else None,
                                "rated": rated.strip() if rated else None,
                            },
                        )
                try:
                    self.logger.info("Scrolling down the page...")
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)

                    next_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "span.c-navigationPagination_item--next.enabled"))
                    )
                    self.logger.info("Next button found, clicking...")
                    next_button.click()
                    time.sleep(5)
                    page_count += 1  # Increment the page count
                except TimeoutException:
                    self.logger.info("No more pages to navigate.")
                    break
                except Exception as e:
                    self.logger.error(f"An error occurred: {e}", exc_info=True)
                    break

        finally:
            self.driver.quit()  # Ensure the WebDriver is closed

    def parse_movie_details(self, response):
        # Extract metadata passed from the main page
        title = response.meta.get("title")
        metascores = response.meta.get("metascores")
        movie_url = response.meta.get("movie_url")
        release_date = response.meta.get("release_date")
        rated = response.meta.get("rated")
        genre = response.css("span.c-globalButton_label::text").get(default='N/A').strip()
        userscores = response.css('div.c-siteReviewScore_user span[data-v-e408cafe]::text').get(default='N/A').strip()

        # Yield the extracted details
        yield {
            "title": title,
            "release_date": release_date,
            "genre": genre,
            "metascores": metascores,
            "userscores": userscores,
            "rated": rated,
            "movie_url": movie_url,
        }
"""