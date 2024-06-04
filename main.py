from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.wait import WebDriverWait
from psycopg2.extras import execute_batch
import constants.stringConst as const
import constants.queries as query
from connection import Connection
from services.seleniumService import SeleniumService
from bs4 import BeautifulSoup
from selenium.webdriver.support import expected_conditions as EC
import re


# from utils.appUtil import AppUtil
# from utils.loggerUtil import logger #TODO


def run():
    # initiate driver
    driver = SeleniumService.init_web_drive()
    db_con = Connection.connect_to_db()
    db_cursor = db_con.cursor()

    # appUtil = AppUtil()   #TODO

    try:
        for business_type in const.BUSINESSES_TYPES:
            print(f'Data extracting started for business type {business_type}')
            for prefix in const.BUSINESS_NAME_PREFIXES:
                print(f"Prefix: {prefix} | business type:{business_type}")
                driver.get(const.WEB_URL)
                business_name_field = driver.find_element(By.NAME, 'bizname')
                # Select the license type from the dropdown menu
                license_type_dropdown = driver.find_element(By.ID, 'licensetype2')
                business_name_field.send_keys(prefix)
                license_type_dropdown.send_keys(business_type)

                # Click the second GO button
                go_button = driver.find_element(By.NAME, 'go2')
                go_button.click()

                # Allow some time for the page to load
                time.sleep(0.005)

                # Capture the results page HTML

                all = []
                while True:
                    results_html = driver.page_source
                    if business_type == const.CONST_GENERAL_CONTRACT:
                        active_business = extract_general_contract_active_businesses(results_html)
                    elif business_type == const.CONST_ELECTRICAL_FIRM:
                        active_business = extract_electrical_firm_active_businesses(results_html)
                    else:
                        print('Not a matching business business_type')

                    all.extend(active_business)

                    try:
                        next_button = driver.find_element(By.NAME, 'next')
                        next_button.click()
                        time.sleep(0.005)  # Adjust sleep time as necessary
                    except NoSuchElementException:
                        break

                process_each_business(driver, all, business_type, db_con, db_cursor)
        print("====COMPLETED======")
    except Exception as e:
        # add intemediate chatch and skip any non processed recrods
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


def process_each_business(driver, active_businesses, business_type, db_con, db_cursor):
    for business_name, business_link in active_businesses:
        print(f"Processing.. Type: {business_type} | business: {business_name}")
        driver.get(f'https://a810-bisweb.nyc.gov/bisweb/{business_link}')
        WebDriverWait(driver, 0.005).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )

        # Extract data from the business detail page as needed
        business_page_source = driver.page_source
        soup = BeautifulSoup(business_page_source, 'html.parser')

        if business_type == const.CONST_ELECTRICAL_FIRM:
            contact_details_list = extract_electrical_firm_contact_details(soup)

            licensee_list = extract_electrical_firm_licensee_details(
                soup.find_all('table')[6])  # TODO: this can be empty

            if len(licensee_list) > 0:
                insert_data = create_electrical_firm_business_contact_db_data(contact_details_list, licensee_list)
                execute_batch(db_cursor, query.INSERT_BUSINESS_CONTACT_DETAILS_ELECTRICAL_FIRM, insert_data)
                db_con.commit()
            else:
                print('No licensees to insert')

            insurance_data_to_insert = extract_electrical_firm_insurance_details(soup.find_all('table')[4],
                                                                                 business_name)
            execute_batch(db_cursor, query.INSERT_LICENSEE_DETAILS_ELECTRICAL_FIRM, insurance_data_to_insert)
            db_con.commit()

        if business_type == const.CONST_GENERAL_CONTRACT:
            contact_details = extract_general_contract_contact_details(soup)
            licensee_list = extract_general_contract_licensee_details(soup.find_all('table')[3])
            insert_data = create_general_contract_business_contact_db_data(contact_details, licensee_list)
            db_cursor.execute(query.INSERT_BUSINESS_CONTACT_DETAILS_GENERAL_CONTRACT, insert_data)
            db_con.commit()

            insurance_data_to_insert = extract_general_contract_insurance_details(soup.find_all('table')[6],
                                                                                  business_name, licensee_list[0])

            execute_batch(db_cursor, query.INSERT_LICENSEE_DETAILS_GENERAL_CONTRACT, insurance_data_to_insert)
            db_con.commit()


def create_electrical_firm_business_contact_db_data(contact_details_list, licensee_details_list):
    db_rows = []
    for licensee in licensee_details_list:
        licensee.extend(contact_details_list)
        licensee.append(const.CONST_ELECTRICAL_FIRM)
        db_rows.append(licensee)
    return db_rows


def create_general_contract_business_contact_db_data(contact_details_list, licensee_details):
    licensee_details.extend(contact_details_list)
    licensee_details.append(const.CONST_GENERAL_CONTRACT)
    return tuple(licensee_details)


def extract_general_contract_contact_details(soup):
    """
        Extracts insurance details for an general contract from the given BeautifulSoup object.

        Args:
            soup (BeautifulSoup): A BeautifulSoup object containing the parsed HTML of the page.

        Returns:
        """
    # Extract Office Address
    address_tag = soup.find('b', string=lambda text: 'Office Address' in text if text else False)
    if address_tag:
        address = address_tag.parent.get_text(strip=True).split(':')[-1].strip()
    else:
        address = const.CONST_NA
    # Extract phone
    business_phone_tag = soup.find('b', string=lambda text: 'Business Phone' in text if text else False)
    if business_phone_tag:
        business_phone = business_phone_tag.parent.get_text(strip=True).split(':')[-1].strip()
    else:
        business_phone = const.CONST_NA

    # business name
    business_name_tag = soup.find('b', string=lambda text: 'Business 1' in text if text else False)
    if business_name_tag:
        business_name = business_name_tag.parent.parent.get_text(strip=True).split(':')[-1].strip()
    else:
        business_name = const.CONST_NA

    return [business_name, address, business_phone]


def extract_general_contract_licensee_details(table):
    """
        Extracts licensee details for a general contract from the given HTML table.

        Args:
            table (BeautifulSoup): A BeautifulSoup object containing the parsed HTML table.

        Returns:
            List
        """
    licensee_name = table.find('td', class_='centercolhdg').find('b').getText(strip=True)
    contractor_id = \
        table.find('b', string=lambda text: 'Contractor ID' in text if text else False).parent.get_text(
            strip=True).split(
            ':')[-1].strip()
    expiration_date = \
        table.find('b', string=lambda text: 'Expiration' in text if text else False).parent.get_text(strip=True).split(
            ':')[-1].strip()
    return [remove_extra_spaces(licensee_name), expiration_date, contractor_id]


def extract_electrical_firm_contact_details(soup):
    """
        Extracts insurance details for an electrical firm from the given BeautifulSoup object.

        Args:
            soup (BeautifulSoup): A BeautifulSoup object containing the parsed HTML of the page.

        Returns:
            List
        """
    # Extract Office Address
    address_tag = soup.find('td', string=lambda text: 'Office Address' in text if text else False)
    if address_tag:
        address = address_tag.find_next_sibling('td').get_text(strip=True)
    else:
        address = const.CONST_NA
    # Extract phone
    business_phone_tag = soup.find('td', string=lambda text: 'Business Phone' in text if text else False)
    if business_phone_tag:
        business_phone_value = business_phone_tag.find_next_sibling('td').get_text(strip=True)
    else:
        business_phone_value = const.CONST_NA

    # business name
    business_name_tag = soup.find('b', string=lambda text: 'Business 1' in text if text else False)
    if business_name_tag:
        business_name = business_name_tag.parent.get_text(strip=True).split(':')[-1].strip()
    else:
        business_name = const.CONST_NA

    return [business_name, address, business_phone_value]


def extract_electrical_firm_licensee_details(table):
    """
        Extracts licensee details for an electrical firm from the given HTML table.

        Args:
            table (BeautifulSoup): A BeautifulSoup object containing the parsed HTML table.

        Returns:
            list: A list of lists, each containing the following details for each 'RESPONSIBLE REP':
                - Licensee name
                - License number
                - Expiration date
                - Status
        """
    if len(table.find_all('tr')) <= 1:
        print("Table has no licensee entries")
        return []
    else:
        # Define variables to hold the extracted values
        licensee_list = []
        # Iterate through the table rows
        for row in table.find_all('tr')[1:]:
            columns = row.find_all('td')
            relationship = columns[2].get_text(strip=True)
            if relationship == 'RESPONSIBLE REP':
                licensee = columns[0].get_text(strip=True)
                license_number = columns[1].get_text(strip=True)
                expiration_date = columns[3].get_text(strip=True)
                status = columns[4].get_text(strip=True)
                licensee_list.append([licensee, license_number, expiration_date, status])

        return licensee_list


def extract_electrical_firm_insurance_details(table, business_name):
    """
        Extracts insurance details for an electrical firm from the given HTML table.a

        Args:
            table (BeautifulSoup): A BeautifulSoup object containing the parsed HTML table.

        Returns:
            list: A list of lists, each containing the following details for each insurance entry:
            :param business_name:
            :param table:

        """
    insurance_list = []
    all_tr = table.find_all('tr')
    if len(all_tr) == 7:
        start_index = 3
    else:
        start_index = 2
    # Iterate through the table rows
    for row in table.find_all('tr')[start_index:]:
        columns = row.find_all('td')
        if len(columns) != 5:
            break
        else:
            insurance_type = sanitize_data(columns[0].get_text(strip=True))
            policy = sanitize_data(columns[1].get_text(strip=True))
            required = sanitize_data(columns[2].get_text(strip=True))
            company = sanitize_data(columns[3].get_text(strip=True))
            exp_date = sanitize_data(columns[4].get_text(strip=True))
            insurance_list.append(
                (const.CONST_ELECTRICAL_FIRM, business_name, insurance_type, policy, required, company, exp_date))

    return insurance_list


def extract_general_contract_insurance_details(table, business_name, licensee_name):
    """
        Extracts insurance details for an general contract from the given HTML table.a

        Args:
            table (BeautifulSoup): A BeautifulSoup object containing the parsed HTML table.

        Returns:
            list
            :param licensee_name:
            :param table:
            :param business_name:
        """
    insurance_list = []
    all_tr = table.find_all('tr')
    if len(all_tr) == 9:
        start_index = 4
    else:
        start_index = 3

    # Iterate through the table rows
    for row in table.find_all('tr')[start_index:]:
        columns = row.find_all('td')
        if len(columns) != 5:
            break
        else:
            insurance_type = sanitize_data(columns[0].get_text(strip=True))
            policy = sanitize_data(columns[1].get_text(strip=True))
            required = sanitize_data(columns[2].get_text(strip=True))
            company = sanitize_data(columns[3].get_text(strip=True))
            exp_date = sanitize_data(columns[4].get_text(strip=True))
            insurance_list.append(
                (const.CONST_GENERAL_CONTRACT, licensee_name, business_name, insurance_type, policy, required, company,
                 exp_date))

    return insurance_list


def sanitize_data(value):
    return value if value != '' else None


def remove_extra_spaces(text):
    cleaned_text = re.sub(r'\s+', ' ', text)
    return cleaned_text.strip()


if __name__ == '__main__':
    run()
