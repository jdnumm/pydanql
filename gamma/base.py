import psycopg2
import logging
import re

from .errors import DatabaseError


class Database:
    def __init__(self, database='app_db', **kwargs):

        # Initialize logger
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

        try:
            self.conn = psycopg2.connect(
                dbname=database,
                user=kwargs.get('user'),
                password=kwargs.get('password'),
                host=kwargs.get('host'),
                port=kwargs.get('port')
            )

            self.cursor = self.conn.cursor()
            self.logger.info("Database connection established.")

        except Exception as e:
            self.logger.exception("Failed to connect to the database.")
            raise DatabaseError(f"Failed to connect to the database.") from e

    def _clean_query(self, query):
        return re.sub(r'\s+', ' ', query).strip()

    def execute(self, query, params=()):
        clean_query = self._clean_query(query)
        try:
            self.cursor.execute(clean_query, params)
            self.conn.commit()
            self.logger.info(f"Executed query: {clean_query} with params: {params}")

        except Exception as e:
            self.logger.exception("Failed to execute query.")
            raise DatabaseError(f"Failed to execute query.") from e

    def fetch(self, query, params=()):
        clean_query = self._clean_query(query)
        try:
            self.cursor.execute(clean_query, params)
            result = self.cursor.fetchall()
            self.logger.info(f"Fetched data with query: {clean_query} and params: {params}")
            return result

        except Exception as e:
            self.logger.exception("Failed to fetch data.")
            raise DatabaseError(f"Failed to fetch data.") from e

    def close(self):
        try:
            self.conn.close()
            self.logger.info("Database connection closed.")

        except Exception as e:
            self.logger.exception("Failed to close the database connection.")
            raise DatabaseError("Failed to close the database connection.")
