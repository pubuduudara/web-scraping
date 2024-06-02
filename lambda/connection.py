import os

import psycopg2 as psycopg2


class Connection:
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

        # Connect to the PostgreSQL database
        connection = psycopg2.connect(
            dbname=os.environ['DB_NAME'],
            user=os.environ['DB_USER'],
            password=os.environ['DB_PASSWORD'],
            host=os.environ['DB_HOST'],
            port=os.environ['DB_PORT']
        )
        return connection
