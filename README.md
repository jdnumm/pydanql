Get support from [BLACKTREES](https://blacktre.es) or on [Github](https://github.com/jdnumm/pydanql)

# Pydanql a Pydantic PostgreSQL Library

## Introduction
The Pydanql Library offers a simple and effective way to interact with a PostgreSQL database. It provides robust classes for database connections, data modeling, and CRUD (Create, Read, Update, Delete) operations. The library is equipped with built-in logging for easier debugging and error handling.

## Quick Example
Here's a brief example to show how to use the Pydanql Python Library to interact with a PostgreSQL database, assuming that the relevant classes `Database`, `Table`, and `ObjecBaseModel` are imported from the Pydanql package.

```python
from pydanql.base import Database
from pydanql.table import Table
from pydanql.model import ObjectBaseModel


# Define Book model as Pydantic Model
class Book(ObjectBaseModel):
    name: str
    author: str
    year: int

# Initialize database
db = Database(database='test_db', user='username', password='password', host='localhost', port=5432)

# Initialize Table
db.books = Table(db, Book)

# Add a new Book
new_book = Book(name="The Lord of the Rings", author="J. R. R. Tolkien", year=1964)
db.books.add(new_book)

# Find Books
books= db.books.find_many()
for book in books:
    print(book)

# Close Connection
db.close()
```

## Installation
To install, you can simply use pip:
```bash
pip install pydanql
```

## Components
- `Database`: Manages the connection to a PostgreSQL database.
- `ObjectBaseModel`: A base Pydantic model with some default fields.
- `Table`: A generic class to manage database tables.
- `DatabaseError`: A custom exception class for database-related issues.

## Features & Examples
- Create a new record:

    ```python
    new_car = Car(brand="Tesla", model="Model S", year=2020, color="Blue", miles=1000.5)
    db.cars_table.add(new_car)
    ```

- Replace an existing record:

    ```python
    existing_car = cars_table.find_one(id=1)
    existing_car.color = "Green"
    db.cars_table.replace(existing_car)
    ```

- Count records:

    ```python
    total_cars = db.cars_table.count()
    ```

- Pagination:

    ```python
    page_1_results = db.cars_table.page(page_number=1, page_size=5)
    ```


## License
Pydanql is licensed under the MIT license.