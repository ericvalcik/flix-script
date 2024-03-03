import os
import logging
import logging.handlers
from bs4 import BeautifulSoup
from time import sleep
import resend
from dotenv import load_dotenv

from playwright.sync_api import sync_playwright

load_dotenv()
resend.api_key = os.getenv("RESEND_API_KEY")
url = "https://www.cinemacity.cz/#/buy-tickets-by-cinema?in-cinema=1052&at=2024-03-15&for-movie=5783s2r&view-mode=list"

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger_stream_handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger_stream_handler.setFormatter(formatter)
logger.addHandler(logger_stream_handler)

# try:
#     SOME_SECRET = os.environ["SOME_SECRET"]
# except KeyError:
#     SOME_SECRET = "Token not available!"
# logger.info("Token not available!")
# raise


if __name__ == "__main__":
    with (sync_playwright() as p):
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        page.wait_for_load_state("networkidle")
        page_content = page.content()

        parser = 'html.parser'
        soup = BeautifulSoup(page_content, parser)
        logger.info("Whole page")
        logger.info(soup)

        # target_elements = soup.find_all(lambda tag: tag.name == 'h5' and "Pátek 15.03.2024" == tag.get_text(strip=True))
        target_elements = soup.find_all(lambda tag: tag.name == 'h5' and "Neděle 03.03.2024" == tag.get_text(strip=True))
        logger.info("Target elements")
        logger.info(target_elements)

        if len(target_elements) != 0:
            logger.info("New movie times are available!")
            logger.info("Sending email to eric.valcik@gmail.com")
            r = resend.Emails.send({
                "from": "github-tracker-action@resend.dev",
                "to": "eric.valcik@gmail.com",
                "subject": "CINEMA CITY BOT TRIGGERED!",
                "html": "<p><strong>New movies on 15-03-2024 !!!</strong></p>" +
                        f"<a href={url}>Link to the page</a><p>Link: {url}</p>"
            })
            logger.info(r)
        else:
            logger.info("No new movies :(")
