from pydantic import ValidationError
from uuid import uuid4
from datetime import datetime
from pydantic import BaseModel
from http import HTTPStatus


class Table:
    META_SCHEMA = """
        id SERIAL PRIMARY KEY,
        date_created TEXT,
        date_last_edit TEXT,
        slug TEXT UNIQUE
    """
    META_FIELDS=['id','date_created','date_last_edit','slug']


    def __init__(self, db, model, table, fields=None, schema=None, include_meta=True):

        self.db = db
        self.model = model
        self.table = table
        self.schema = self._generate_schema(schema, include_meta)
        self._create_table()
        # Return list of Object models get columns from db. Maybe not the fastest method
        self.columns = self.META_FIELDS+fields

    def _generate_schema(self, schema=None, include_meta=True):
        if schema is None:
            s = self.META_SCHEMA
        if include_meta:
            s = self.META_SCHEMA + ',' + schema
        return f"({s})"

    def _create_table(self):
        query = f"""
        CREATE TABLE IF NOT EXISTS {self.table} {self.schema}
        """
        self.db.execute(query)
        query = f"""
        CREATE INDEX IF NOT EXISTS idx_slug ON {self.table}(slug)
        """
        self.db.execute(query)

    def _construct_query_for_insert_or_replace(self, object: BaseModel, replace=False):
        columns = self.columns.copy()

        if replace:
            columns_str = ', '.join(columns)
            placeholders = ', '.join(['%s'] * len(columns))

            updates = ', '.join([f"{field} = EXCLUDED.{field}" for field in columns])
            query = f"""
                INSERT INTO {self.table} ({columns_str}) VALUES ({placeholders})
                ON CONFLICT (id) DO UPDATE SET {updates}
            """
        else:
            if getattr(object, "id", None) is None:
                columns.remove('id')

            columns_str = ', '.join(columns)
            placeholders = ', '.join(['%s'] * len(columns))
            query = f"INSERT INTO {self.table} ({columns_str}) VALUES ({placeholders})"

        data = [getattr(object, field) for field in columns]
        return query, data

    def _construct_where_clause(self, **kwargs):
        """Constructs the WHERE clause for filtering."""

        if not kwargs:
            return "", []

        clauses = []
        values = []

        for key, value in kwargs.items():
            if isinstance(value, dict):
                # LIKE query
                if 'like' in value:
                    print('like search')
                    clauses.append(f"{key} LIKE %s")
                    values.append(value['like'].replace('*','%'))

                # Range query
                elif 'range' in value:
                    low, high = value['range']
                    clauses.append(f"{key} >= %s AND {key} <= %s")
                    values.extend([low, high])

                # IN query
                elif 'in' in value:
                    placeholders = ', '.join(['%s'] * len(value['in']))
                    clauses.append(f"{key} IN ({placeholders})")
                    values.extend(value['in'])

                # Greater than
                elif 'gt' in value:
                    clauses.append(f"{key} > %s")
                    values.append(value['gt'])

                # Less than
                elif 'lt' in value:
                    clauses.append(f"{key} < %s")
                    values.append(value['lt'])

            else:
                clauses.append(f"{key} = %s")
                values.append(value)

        clause = "WHERE " + " AND ".join(clauses)

        return clause, values


    def _construct_pagination_clauses(self, offset=None, count=None):
        """Constructs the LIMIT and OFFSET clauses for pagination."""
        limit_clause = f"LIMIT {int(count)}" if count is not None else ""
        offset_clause = f"OFFSET {int(offset)}" if offset is not None else ""

        return limit_clause, offset_clause


    def _construct_order_by_clause(self, sort=None):
        # Construct the ORDER BY clause
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
        where_clause, values = self._construct_where_clause(**kwargs)
        limit_clause, offset_clause = self._construct_pagination_clauses(offset, count)
        order_by_clause = self._construct_order_by_clause(sort)

        query = f"SELECT * FROM {self.table} {where_clause} {order_by_clause} {limit_clause} {offset_clause}"

        results = self.db.fetch(query, tuple(values))

        return [self.model(**{column_name: value for column_name, value in zip(self.columns, res)}) for res in results]


    def find_one(self, **kwargs):
        results = self.find_many(count=1, **kwargs)
        return results[0] if results else None


    def count(self, **kwargs):
        """Returns the total number of records that match the given criteria."""
        where_clause, values = self._construct_where_clause(**kwargs)

        query = f"SELECT COUNT(*) FROM {self.table} {where_clause}"
        total_records = self.db.fetch(query, tuple(values))
        return total_records[0][0] if total_records else 0

    def add(self, object: BaseModel):
        try:
            object.date_created = datetime.now()  # Set current time
            object._date_last_edit = object.date_created   # Set current time for last edit

            valid_object = self.model(**object.dict())
            query, data = self._construct_query_for_insert_or_replace(valid_object)
            self.db.execute(query, data)

        except ValidationError as e:
            print(f"Validation error: {e}")

    def replace(self, object: BaseModel):
        try:
            object._date_last_edit = datetime.now()  # Set current time for last edit

            query, data = self._construct_query_for_insert_or_replace(object, replace=True)
            self.db.execute(query, data)
        except Exception as e:
            print(f"Error replacing record: {e}")

    def delete(self, object: BaseModel):
        # Constructing the SQL query for the delete operation
        query = f'DELETE FROM {self.table} WHERE id = %s'

        try:
            self.db.execute(query, (object.id,))
        except Exception as e:
            print(f"Error deleting record: {e}")


    def page(self, page_number, page_size=10, **kwargs):
        """
        Paginate through the table results based on page number and page size.

        Parameters:
        - page_number: The current page number. Defaults to 1.
        - page_size: Number of records per page. Defaults to 10.
        - **kwargs: Additional filtering criteria.

        Returns:
        - A list of model instances representing the current page's data.
        """
        if page_number <= 0:
            raise ValueError("Page number should be 1 or higher")

        # Calculate offset based on page number and page size
        offset = (page_number - 1) * page_size
        
        # Use the find_many method to fetch the desired records
        results = self.find_many(offset=offset, count=page_size, **kwargs)
        
        return results

    def page_count(self, page_size=10, **kwargs):
        """Returns the total number of pages."""
        total_records = self.count(**kwargs)
        pages = total_records // page_size
        if total_records % page_size > 0:
            pages += 1

        return pages

