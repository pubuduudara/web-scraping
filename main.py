from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.wait import WebDriverWait
from psycopg2.extras import execute_batch
import constants.stringConst as const
import constants.queries as query
from connection import Connection
from services.electricalFirmService import ElectricalFirmService
from services.generalContractorService import GeneralContractorService
from services.seleniumService import SeleniumService
from bs4 import BeautifulSoup
from selenium.webdriver.support import expected_conditions as EC


def run():
    try:
        driver = SeleniumService.init_web_drive()
        db_con = Connection.connect_to_db()
        db_cursor = db_con.cursor()
        electrical_firm = ElectricalFirmService()
        general_contractor = GeneralContractorService()
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
                        active_business = general_contractor.extract_general_contract_active_businesses(results_html)
                    elif business_type == const.CONST_ELECTRICAL_FIRM:
                        active_business = electrical_firm.extract_electrical_firm_active_businesses(results_html)
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


def process_each_business(driver, active_businesses, business_type, db_con, db_cursor):
    for business_name, business_link in active_businesses:
        print(f"Processing.. Type: {business_type} | business: {business_name}")
        URL = f'https://a810-bisweb.nyc.gov/bisweb/{business_link}'
        driver.get(URL)
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
                insert_data = create_electrical_firm_business_contact_db_data(contact_details_list, licensee_list, URL)
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
            insert_data = create_general_contract_business_contact_db_data(contact_details, licensee_list, URL)
            db_cursor.execute(query.INSERT_BUSINESS_CONTACT_DETAILS_GENERAL_CONTRACT, insert_data)
            db_con.commit()

            insurance_data_to_insert = extract_general_contract_insurance_details(soup.find_all('table')[6],
                                                                                  business_name, licensee_list[0])

            execute_batch(db_cursor, query.INSERT_LICENSEE_DETAILS_GENERAL_CONTRACT, insurance_data_to_insert)
            db_con.commit()


if __name__ == '__main__':
    run()
