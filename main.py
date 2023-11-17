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
url = "https://shop.flixbus.cz/search?departureCity=49df5276-f874-46a8-89af-4df16905d56c&arrivalCity=40de1ad1-8646-11e6-9066-549f350fcb0c&route=Uhersk%C3%BD+Brod-Praha&rideDate=19.11.2023&adult=1&_locale=cs&features%5Bfeature.enable_distribusion%5D=1&features%5Bfeature.train_cities_only%5D=0&features%5Bfeature.auto_update_disabled%5D=0&features%5Bfeature.webc_search_station_suggestions_enabled%5D=0&features%5Bfeature.darken_page%5D=1&_sp=2c9ed49d-80ef-4c91-ae26-f9297f62be4d&_spnuid=c12c539f-c4d7-46bd-afb0-52e72dc4ad4a_1700257803473"

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

        target_elements = soup.find_all(lambda tag: tag.name == 'span' and "14:45" == tag.get_text(strip=True))
        logger.info("Target elements")
        logger.info(target_elements)

        element = target_elements[0]
        parent_div = element.parent.parent.parent.parent.parent.parent
        fully_booked_all = \
            parent_div.find_all(lambda tag: tag.name == 'div' and "Plně obsazeno" == tag.get_text(strip=True))
        logger.info("Fully booked all finds")
        logger.info(fully_booked_all)

        if len(fully_booked_all) == 0:
            logger.info("Not fully booked!")
            logger.info("Sending email to eric.valcik@gmail.com")
            r = resend.Emails.send({
                "from": "flix-script-action@resend.dev",
                "to": "eric.valcik@gmail.com",
                "subject": "Bus is not fully booked!",
                "html": "<p>Bus at 14:45 is <strong>NOT FULLY BOOKED</strong>!</p>"
            })
            logger.info(r)
        else:
            logger.info("It's fully booked!")
