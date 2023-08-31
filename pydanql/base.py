import psycopg2
import logging
import re
from .errors import DatabaseError

class Database:
    """
    Database class to manage PostgreSQL database operations.
    Provides methods for executing queries and fetching results.
    """

    def __init__(self, database='app_db', **kwargs):
        """
        Initialize Database class.

        :param database: name of the database to connect to.
        :param kwargs: additional keyword arguments like user, password, host, and port.
        """

        # Initialize the logger for this class
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

        try:
            # Attempt to establish a database connection
            self.conn = psycopg2.connect(
                dbname=database,
                user=kwargs.get('user'),
                password=kwargs.get('password'),
                host=kwargs.get('host'),
                port=kwargs.get('port')
            )
            # Create a cursor object
            self.cursor = self.conn.cursor()

            # Log a successful database connection
            self.logger.info("Database connection established.")

        except Exception as e:
            # Log the exception if database connection fails
            self.logger.exception("Failed to connect to the database.")
            raise DatabaseError(f"Failed to connect to the database.") from e

    def _clean_query(self, query):
        """
        Remove extra whitespaces from the query string.

        :param query: SQL query as a string.
        :return: cleaned SQL query as a string.
        """
        return re.sub(r'\s+', ' ', query).strip()

    def execute(self, query, params=()):
        """
        Execute an SQL query.

        :param query: SQL query as a string.
        :param params: parameters for SQL query as a tuple.
        """
        clean_query = self._clean_query(query)
        try:
            self.cursor.execute(clean_query, params)
            self.conn.commit()
            
            # Log the executed query
            self.logger.info(f"Executed query: {clean_query} with params: {params}")

        except Exception as e:
            # Log the exception if query execution fails
            self.logger.exception("Failed to execute query.")
            raise DatabaseError(f"Failed to execute query.") from e

    def fetch(self, query, params=()):
        """
        Fetch data from the database using an SQL query.

        :param query: SQL query as a string.
        :param params: parameters for SQL query as a tuple.
        :return: fetched data as a list of tuples.
        """
        clean_query = self._clean_query(query)
        try:
            self.cursor.execute(clean_query, params)
            result = self.cursor.fetchall()

            # Log the fetching operation
            self.logger.info(f"Fetched data with query: {clean_query} and params: {params}")

            return result

        except Exception as e:
            # Log the exception if fetching fails
            self.logger.exception("Failed to fetch data.")
            raise DatabaseError(f"Failed to fetch data.") from e

    def close(self):
        """
        Close the database connection.
        """
        try:
            self.conn.close()

            # Log the closing operation
            self.logger.info("Database connection closed.")

        except Exception as e:
            # Log the exception if closing the connection fails
            self.logger.exception("Failed to close the database connection.")
            raise DatabaseError("Failed to close the database connection.")
