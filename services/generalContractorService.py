import constants.stringConst as const
from bs4 import BeautifulSoup
from helpers.appUtil import AppUtil


class GeneralContractorService:

    @staticmethod
    def extract_general_contract_active_businesses(page_source):
        """
            Extracts the names and links of active businesses from the provided HTML page source.

            This function parses the HTML content using BeautifulSoup to find and extract rows of business data. It checks the
            status of each business and includes only those marked as 'ACTIVE'. The extracted information includes the
            business name and a hyperlink associated with it.

            Parameters:
            page_source (str): The HTML content of the page as a string.

            Returns:
            list: A list of tuples, each containing the business name and its corresponding hyperlink, for businesses that are active.
            """
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
            Extracts contact details for a general contract from the given BeautifulSoup object.

            This function retrieves the office address, business phone number, and business name from the parsed HTML
            content. It searches for specific tags and extracts the relevant text. If the required information is not
            found, it returns a predefined constant indicating the absence of data.

            Args:
                soup (BeautifulSoup): A BeautifulSoup object containing the parsed HTML of the page.

            Returns:
                list: A list containing the business name, office address, and business phone number.
                      If any of these details are not found, a constant indicating 'not available' is returned for those fields.
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

    @staticmethod
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
            table.find('b', string=lambda text: 'Expiration' in text if text else False).parent.get_text(
                strip=True).split(
                ':')[-1].strip()
        return [AppUtil.remove_extra_spaces(licensee_name), expiration_date, contractor_id]

    @staticmethod
    def create_general_contract_business_contact_db_data(contact_details_list, licensee_details, pageURL):
        """
            Combines contact details, licensee details, and additional information into a single tuple for database entry.

            Returns:
                tuple: A tuple containing the combined data of licensee details, contact details, contract type constant,
                       and the page URL.
            """
        licensee_details.extend(contact_details_list)
        licensee_details.append(const.CONST_GENERAL_CONTRACT)
        licensee_details.append(pageURL)
        return tuple(licensee_details)

    @staticmethod
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
                insurance_type = AppUtil.sanitize_data(columns[0].get_text(strip=True))
                policy = AppUtil.sanitize_data(columns[1].get_text(strip=True))
                required = AppUtil.sanitize_data(columns[2].get_text(strip=True))
                company = AppUtil.sanitize_data(columns[3].get_text(strip=True))
                exp_date = AppUtil.sanitize_data(columns[4].get_text(strip=True))
                insurance_list.append(
                    (const.CONST_GENERAL_CONTRACT, licensee_name, business_name, insurance_type, policy, required,
                     company,
                     exp_date))

        return insurance_list
