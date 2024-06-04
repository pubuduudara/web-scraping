import psycopg2 as psycopg2
from psycopg2.extras import execute_batch
import constants.stringConst as const


class Connection:
    db_cursor = None

    def __init__(self):
        db_cursor = self.connect_to_db()

    @staticmethod
    def connect_to_db():
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
        try:
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
            message = f"An error occurred in batch_insert: {e}"
            print(message)

    @staticmethod
    def batch_insert(query, data):
        try:
            execute_batch(Connection.db_cursor, query, data)
        except Exception as e:
            message = f"An error occurred in connect_to_db: {e}"
            print(message)
