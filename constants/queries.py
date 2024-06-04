INSERT_BUSINESS_CONTACT_DETAILS_ELECTRICAL_FIRM = 'INSERT INTO business_contact (licensee,license_number,expiration_date,status,business_name,business_office_address,business_phone_number,business_type,page_url) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id'
INSERT_BUSINESS_CONTACT_DETAILS_GENERAL_CONTRACT = 'INSERT INTO business_contact (licensee,expiration_date,contractor_id,business_name,business_office_address,business_phone_number,business_type,page_url) VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id'

INSERT_INSURANCE_DATA = 'INSERT INTO insurance_data (insurance_type,policy,required,company,expiration_date,business_contact_id) VALUES (%s,%s,%s,%s,%s,%s)'
