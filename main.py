from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
import time

from selenium.webdriver.support.wait import WebDriverWait

import constants.stringConst as const
from services.seleniumService import SeleniumService
from bs4 import BeautifulSoup
from selenium.webdriver.support import expected_conditions as EC


# from utils.appUtil import AppUtil
# from utils.loggerUtil import logger #TODO


def run():
    # initiate driver
    driver = SeleniumService.init_web_drive()

    # appUtil = AppUtil()   #TODO

    try:
        for business in const.BUSINESSES_VALUES:
            for prefix in const.BUSINESS_NAME_PREFIXES:
                print(f"Prefix: {prefix} | business:{business}")
                driver.get(const.WEB_URL)
                business_name_field = driver.find_element(By.NAME, 'bizname')
                # Select the license type from the dropdown menu
                license_type_dropdown = driver.find_element(By.ID, 'licensetype2')
                business_name_field.send_keys(prefix)
                license_type_dropdown.send_keys(business)

                # Click the second GO button
                go_button = driver.find_element(By.NAME, 'go2')
                go_button.click()

                # Allow some time for the page to load
                time.sleep(2)

                # Capture the results page HTML

                all = []
                while True:
                    results_html = driver.page_source
                    if business == const.GENERAL_CONTRACT:
                        active_business = extract_general_contract_active_businesses(results_html)
                    elif business == const.ELECTRICAL_FIRM:
                        active_business = extract_electrical_firm_active_businesses(results_html)
                    else:
                        print('Not a matching business')

                    all.extend(active_business)

                    try:
                        next_button = driver.find_element(By.NAME, 'next')
                        next_button.click()
                        time.sleep(2)  # Adjust sleep time as necessary
                    except NoSuchElementException:
                        break

                process_each_business(driver, all)
    except Exception as e:
        message = f"An error occurred: {e}"
        print(message)
    finally:
        # Close the WebDriver
        driver.quit()


def extract_general_contract_active_businesses(page_source):
    soup = BeautifulSoup(page_source, 'html.parser')
    active_businesses = []
    rows = soup.find_all('tr')
    for row in rows:
        columns = row.find_all('td')
        if len(columns) >= 4:
            business_name = columns[0].get_text(strip=True)
            status = columns[3].get_text(strip=True)
            if status == 'ACTIVE':
                link = columns[1].find('a')['href']
                # active_businesses.append({'name': business_name, 'link': link})
                active_businesses.append((business_name, link))

    return active_businesses


def extract_electrical_firm_active_businesses(page_source):
    soup = BeautifulSoup(page_source, 'html.parser')
    active_businesses = []
    rows = soup.find_all('tr')
    for row in rows:
        columns = row.find_all('td')
        if len(columns) == 3:
            status = columns[2].text.strip()
            if status == 'ACTIVE':
                business_link = columns[0].find('a')['href']
                business_name = columns[0].text.strip()
                active_businesses.append((business_name, business_link))

    return active_businesses


def process_each_business(driver, active_businesses):
    for business_name, business_link in active_businesses:
        print(f"Processing business: {business_name}")
        driver.get(f'https://a810-bisweb.nyc.gov/bisweb/{business_link}')
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )
        # Extract data from the business detail page as needed
        business_page_source = driver.page_source
        # Process the business detail page (add your code here)
        print(f"Processed business: {business_name}")


if __name__ == '__main__':
    run()
