import constants.stringConst as const
from bs4 import BeautifulSoup


class GeneralContractor:
    @staticmethod
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

    @staticmethod
    def extract_general_contract_contact_details(soup):
        """
            Extracts insurance details for an general contract from the given BeautifulSoup object.

            Args:
                soup (BeautifulSoup): A BeautifulSoup object containing the parsed HTML of the page.

            Returns:
                dict: A dictionary containing the extracted details with keys:
                    - CONST_BUSINESS_NAME: The name of the business.
                    - CONST_BUSINESS_OFFICE_ADDRESS: The office address of the business.
                    - CONST_BUSINESS_PHONE_NUMBER: The business phone number.
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

        return {const.CONST_BUSINESS_NAME: business_name, const.CONST_BUSINESS_OFFICE_ADDRESS: address,
                const.CONST_BUSINESS_PHONE_NUMBER: business_phone}

    @staticmethod
    def extract_general_contract_licensee_details(table):
        """
            Extracts licensee details for a general contract from the given HTML table.

            Args:
                table (BeautifulSoup): A BeautifulSoup object containing the parsed HTML table.

            Returns:
                dict: A dictionary containing the extracted details with keys
                    - CONST_LICENSEE_NAME: The name of the licensee.
                    - CONST_CONTRACTOR_ID: Contractor id.
                    - CONST_EXPIRATION_DATE: Exp Date.
            """
        licensee_name = table.find('td', class_='centercolhdg').find('b').getText(strip=True)
        contractor_id = \
            table.find('b', string=lambda text: 'Contractor ID' in text if text else False).parent.get_text(
                strip=True).split(
                ':')[-1].strip()
        expiration_date = \
            table.find('b', string=lambda text: 'Expiration' in text if text else False).parent.get_text(
                strip=True).split(
                ':')[-1].strip()
        return {const.CONST_LICENSEE_NAME: licensee_name, const.CONST_CONTRACTOR_ID: contractor_id,
                const.CONST_EXPIRATION_DATE: expiration_date}

    @staticmethod
    def extract_general_contract_insurance_details(table):
        """
            Extracts insurance details for an general contract from the given HTML table.a

            Args:
                table (BeautifulSoup): A BeautifulSoup object containing the parsed HTML table.

            Returns:
                list: A list of lists, each containing the following details for each insurance entry:
                    - Insurance type
                    - Policy number
                    - Required (yes/no)
                    - Insurance company
                    - Expiration date
            """
        insurance_list = []

        # Iterate through the table rows
        for row in table.find_all('tr')[3:]:
            columns = row.find_all('td')
            if len(columns) != 5:
                break
            else:
                insurance_type = columns[0].get_text(strip=True)
                policy = columns[1].get_text(strip=True)
                required = columns[2].get_text(strip=True)
                company = columns[3].get_text(strip=True)
                exp_date = columns[4].get_text(strip=True)
                insurance_list.append([insurance_type, policy, required, company, exp_date])

        return insurance_list
