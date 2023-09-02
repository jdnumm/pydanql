from pydantic import ValidationError
from uuid import uuid4
from datetime import datetime
from pydantic import BaseModel
from http import HTTPStatus
from typing import Type, Optional
import inflect

# Initialize the inflect engine
p = inflect.engine()

def get_all_annotations(cls):
    """
    Returns all annotations for a given class, including those from its base classes.

    Parameters:
    - cls: The class to extract annotations from

    Returns:
    - Dictionary of annotations
    """
    annotations = {}
    for base in reversed(cls.__mro__):
        annotations.update(getattr(base, '__annotations__', {}))
    return annotations

class Table:
    """
    Represents a database table.

    Attributes:
    - TYPE_MAPPING: Maps Python types to SQL column types.
    """
    TYPE_MAPPING = {
        int: "INTEGER",
        float: "REAL",
        str: "TEXT",
        bool: "BOOLEAN",
        bytes: "BYTEA",
        bytearray: "BYTEA",
        memoryview: "BYTEA",
        datetime: "TIMESTAMP",
        # Add additional types as needed
    }

    def __init__(self, db, model, table_name=None):
        """
        Initialize the Table class.

        Parameters:
        - db: Database connection
        - model: Pydantic model describing the table schema
        - table_name: Optional custom name for the table
        """
        self.db = db
        self.model = model
        self.name = table_name or p.plural(self.model.__name__)
        self.schema = self._generate_schema_from_model()
        self.columns = self._generate_columns_from_model()
        self._create_table()

    def _generate_columns_from_model(self) -> str:
        """Generate column names from the model."""
        field_names = []
        all_annotations = get_all_annotations(self.model)
        for name in all_annotations.keys():
            field_names.append(name)
        return field_names

    def _generate_schema_from_model(self) -> str:
        """Generate the schema from the model's annotations."""
        columns = []
        all_annotations = get_all_annotations(self.model)
        for name, column in all_annotations.items():
            # Handle Optional, List, etc.
            field_type = column.__origin__ if hasattr(column, '__origin__') else column  
            # Default to TEXT type if not found in TYPE_MAPPING
            column_type = self.TYPE_MAPPING.get(field_type, "TEXT")

            constraints = []

            # Get constraints and data type if defined on pydantic Field
            pydantic_field = self.model.__fields__[name]
            if pydantic_field.json_schema_extra:
                constraints.extend(pydantic_field.json_schema_extra.get('constraints'))
                if pydantic_field.json_schema_extra.get('data_type'):
                    column_type = pydantic_field.json_schema_extra.get('data_type')
            elif 'Optional' in str(column):
                constraints.append('NULL')
            else:
                constraints.append('NOT NULL')

            columns.append(f"{name} {column_type} {' '.join(constraints)}")

        return ", ".join(columns)

    def _create_table(self):
        """Create the table if it doesn't exist."""
        schema = self._generate_schema_from_model()
        print(schema)
        query = f"CREATE TABLE IF NOT EXISTS {self.name} ({schema});"
        self.db.execute(query)

    def _construct_query_for_insert_or_replace(self, object: BaseModel, replace=False):
        """
        Construct query for INSERT or REPLACE operations.

        Parameters:
        - object: The Pydantic model instance to insert or replace
        - replace: Whether to replace the existing record or not

        Returns:
        - The constructed query and data
        """
        columns = self.columns.copy()
        print(columns)

        # Handle the 'replace' case
        if replace:
            columns_str = ', '.join(columns)
            placeholders = ', '.join(['%s'] * len(columns))

            updates = ', '.join([f"{field} = EXCLUDED.{field}" for field in columns])
            query = f"""
                INSERT INTO {self.name} ({columns_str}) VALUES ({placeholders})
                ON CONFLICT (id) DO UPDATE SET {updates}
            """
        # Handle the 'insert' case
        else:
            if getattr(object, "id", None) is None:
                columns.remove('id')

            columns_str = ', '.join(columns)
            placeholders = ', '.join(['%s'] * len(columns))
            query = f"INSERT INTO {self.name} ({columns_str}) VALUES ({placeholders})"

        data = [getattr(object, field) for field in columns]
        return query, data

    def _construct_where_clause(self, **kwargs):
        """
        Constructs the WHERE clause for filtering.

        Parameters:
        - **kwargs: Keyword arguments specifying the filtering conditions

        Returns:
        - SQL WHERE clause and list of values to insert into the query
        """
        if not kwargs:
            return "", []

        clauses = []
        values = []

        # Iterate through all keyword arguments to construct the WHERE clause
        for key, value in kwargs.items():
            if isinstance(value, dict):
                # Handle LIKE query
                if 'like' in value:
                    print('like search')
                    clauses.append(f"{key} LIKE %s")
                    values.append(value['like'].replace('*','%'))
                # Handle range query
                elif 'range' in value:
                    low, high = value['range']
                    clauses.append(f"{key} >= %s AND {key} <= %s")
                    values.extend([low, high])
                # Handle IN query
                elif 'in' in value:
                    placeholders = ', '.join(['%s'] * len(value['in']))
                    clauses.append(f"{key} IN ({placeholders})")
                    values.extend(value['in'])
                # Handle greater than query
                elif 'gt' in value:
                    clauses.append(f"{key} > %s")
                    values.append(value['gt'])
                # Handle less than query
                elif 'lt' in value:
                    clauses.append(f"{key} < %s")
                    values.append(value['lt'])
            else:
                clauses.append(f"{key} = %s")
                values.append(value)

        clause = "WHERE " + " AND ".join(clauses)

        return clause, values

    def _construct_pagination_clauses(self, offset=None, count=None):
        """
        Constructs the LIMIT and OFFSET clauses for pagination.

        Parameters:
        - offset: Starting position for the query
        - count: Number of records to return

        Returns:
        - SQL LIMIT and OFFSET clauses
        """
        limit_clause = f"LIMIT {int(count)}" if count is not None else ""
        offset_clause = f"OFFSET {int(offset)}" if offset is not None else ""

        return limit_clause, offset_clause

    def _construct_order_by_clause(self, sort=None):
        """
        Constructs the ORDER BY clause for sorting.

        Parameters:
        - sort: Column to sort by (optionally prefixed with '-' for DESC)

        Returns:
        - SQL ORDER BY clause
        """
        order_by_clause = ""
        if sort:
            if sort.startswith('-'):
                direction = "DESC"
                sort = sort[1:]
            else:
                direction = "ASC"
            if sort in self.columns:
                order_by_clause = f"ORDER BY {sort} {direction}"
            else:
                raise ValueError(f"Invalid sort column: {sort}")

        return order_by_clause

    def find_many(self, offset=None, count=None, sort=None, **kwargs):
        """
        Finds multiple records based on the given filters, sort order, and pagination options.

        Parameters:
        - offset: The offset for pagination.
        - count: The number of records to return.
        - sort: The column to sort the results.
        - **kwargs: Additional filtering criteria.

        Returns:
        - A list of model instances that match the criteria.
        """
        where_clause, values = self._construct_where_clause(**kwargs)
        limit_clause, offset_clause = self._construct_pagination_clauses(offset, count)
        order_by_clause = self._construct_order_by_clause(sort)

        query = f"SELECT * FROM {self.name} {where_clause} {order_by_clause} {limit_clause} {offset_clause}"

        results = self.db.fetch(query, tuple(values))

        return [self.model(**{column_name: value for column_name, value in zip(self.columns, res)}) for res in results]

    def find_one(self, **kwargs):
        """
        Finds a single record based on the given filters.

        Parameters:
        - **kwargs: Additional filtering criteria.

        Returns:
        - A single model instance if found, else None.
        """
        results = self.find_many(count=1, **kwargs)
        return results[0] if results else None

    def count(self, **kwargs):
        """
        Returns the total number of records that match the given criteria.

        Parameters:
        - **kwargs: Additional filtering criteria.

        Returns:
        - Integer representing the total number of matching records.
        """
        where_clause, values = self._construct_where_clause(**kwargs)

        query = f"SELECT COUNT(*) FROM {self.name} {where_clause}"
        total_records = self.db.fetch(query, tuple(values))
        return total_records[0][0] if total_records else 0

    def add(self, object: BaseModel):
        """
        Adds a new record to the table.

        Parameters:
        - object: The Pydantic model instance representing the record.

        Returns:
        - None
        """
        try:
            # Setting current time for 'date_created' and '_date_last_edit'
            object.date_created = datetime.now()
            object._date_last_edit = object.date_created

            # Validating the model
            valid_object = self.model(**object.dict())
            query, data = self._construct_query_for_insert_or_replace(valid_object)
            self.db.execute(query, data)

        except ValidationError as e:
            print(f"Validation error: {e}")

    def replace(self, object: BaseModel):
        """
        Replaces an existing record in the table.

        Parameters:
        - object: The Pydantic model instance representing the new state of the record.

        Returns:
        - None
        """
        try:
            # Updating the last edit time
            object._date_last_edit = datetime.now()

            query, data = self._construct_query_for_insert_or_replace(object, replace=True)
            self.db.execute(query, data)
        except Exception as e:
            print(f"Error replacing record: {e}")

    def delete(self, object: BaseModel):
        """
        Deletes a record from the table.

        Parameters:
        - object: The Pydantic model instance representing the record to be deleted.

        Returns:
        - None
        """
        # Constructing the SQL query for the delete operation
        query = f'DELETE FROM {self.name} WHERE id = %s'

        try:
            # Executing the SQL query to delete the record
            self.db.execute(query, (object.id,))
        except Exception as e:
            print(f"Error deleting record: {e}")

    def page(self, page_number, page_size=10, **kwargs):
        """
        Paginates through the records in the table based on the given page number and size.

        Parameters:
        - page_number: The current page number, starts from 1.
        - page_size: Number of records to return per page. Defaults to 10.
        - **kwargs: Additional filtering criteria for the records.

        Returns:
        - A list of model instances representing the current page's data.
        """
        # Validate page_number
        if page_number <= 0:
            raise ValueError("Page number should be 1 or higher")

        # Calculate the offset based on the page number and size
        offset = (page_number - 1) * page_size

        # Use find_many to fetch the desired records
        return self.find_many(offset=offset, count=page_size, **kwargs)

    def page_count(self, page_size=10, **kwargs):
        """
        Calculates the total number of pages based on the given page size and filtering criteria.

        Parameters:
        - page_size: Number of records to return per page. Defaults to 10.
        - **kwargs: Additional filtering criteria for the records.

        Returns:
        - Integer representing the total number of pages.
        """
        # Find the total number of records that match the criteria
        total_records = self.count(**kwargs)

        # Calculate the number of pages
        pages = total_records // page_size
        if total_records % page_size > 0:
            pages += 1

        return pages

# End of the Table class
