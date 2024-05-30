INSERT_BUSINESS_CONTACT_DETAILS = 'INSERT INTO business_contact (business_name,business_office_address,business_phone_number,business_type,licensee) VALUES (%s,%s,%s,%s,%s) RETURNING id'
INSERT_LICENSEE_DETAILS = 'INSERT INTO insurance_data (business_contact_id,insurance_type,policy,required,company,expiration_date) VALUES (%s,%s,%s,%s,%s,%s)'
