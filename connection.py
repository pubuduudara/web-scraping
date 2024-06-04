import psycopg2 as psycopg2

import constants.stringConst as const


class Connection:
    @staticmethod
    def connect_to_db():
        try:

            """
            Connect to a PostgreSQL database and execute sample queries.
    
            Parameters:
            dbname (str): Name of the database
            user (str): Database user
            password (str): Password for the database user
            host (str): Host where the database is running
            port (str): Port where the database is running
    
            Returns:
            None
            """

            # Connect to the PostgreSQL database
            connection = psycopg2.connect(
                dbname=const.DB_NAME,
                user=const.DB_USER,
                password=const.DB_PASSWORD,
                host=const.DB_HOST,
                port=const.DB_PORT
            )
            return connection
        except Exception as e:
            message = f"An error occurred connect_to_db: {e}"
            print(message)
