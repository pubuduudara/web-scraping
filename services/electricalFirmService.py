import constants.stringConst as const
from bs4 import BeautifulSoup
from helpers.appUtil import AppUtil


class ElectricalFirmService:

    @staticmethod
    def extract_electrical_firm_active_businesses(page_source):
        """
            Extracts active electrical firm businesses from a given HTML page source.

            Args:
                page_source (str): The HTML source code of the webpage containing business data.

            Returns:
                list[tuple[str, str]]: A list of tuples containing the business name and its corresponding link,
                for businesses with an "ACTIVE" status. If no active businesses are found, an empty list is returned.
            """
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def create_electrical_firm_business_contact_db_data(contact_details_list, licensee_details_list, pageURL):
        db_rows = []
        for licensee in licensee_details_list:
            licensee.extend(contact_details_list)
            licensee.append(const.CONST_ELECTRICAL_FIRM)
            licensee.append(pageURL)
            db_rows.append(licensee)
        return db_rows

    @staticmethod
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
                insurance_type = AppUtil.sanitize_data(columns[0].get_text(strip=True))
                policy = AppUtil.sanitize_data(columns[1].get_text(strip=True))
                required = AppUtil.sanitize_data(columns[2].get_text(strip=True))
                company = AppUtil.sanitize_data(columns[3].get_text(strip=True))
                exp_date = AppUtil.sanitize_data(columns[4].get_text(strip=True))
                insurance_list.append(
                    (const.CONST_ELECTRICAL_FIRM, business_name, insurance_type, policy, required, company, exp_date))

        return insurance_list