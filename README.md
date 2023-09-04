Get support from [BLACKTREES](https://blacktre.es) or on [Github](https://github.com/jdnumm/pydanql)

# Pydanql: A Pydantic PostgreSQL Library

⚠️ **Early Version Warning**: This is an early version of the Pydanql library and is subject to changes. While we strive for stability, features and APIs may be altered as the library evolves. Your feedback is invaluable, so please feel free to provide it through [BLACKTREES](https://blacktre.es) or on [Github](https://github.com/jdnumm/pydanql).

## Introduction
Pydanql offers a streamlined way to interact with PostgreSQL databases using Python. This library combines robust database connection management, data modeling, and CRUD (Create, Read, Update, Delete) functionalities. Additionally, built-in logging features make debugging and error handling more straightforward.

## Quick Example

The following example demonstrates how to use the Pydanql library for database interactions. This assumes that the necessary classes—`Database`, `Table`, and `ObjectBaseModel`—are imported from Pydanql.

```python
from pydanql.base import Database
from pydanql.table import Table
# ObjectBaseModel is a Pydantic BaseModel equipped with default fields such as id, slug, date_created, and date_last_edit.
from pydanql.model import ObjectBaseModel

# Define the Book model using Pydantic
class Book(ObjectBaseModel):
    name: str
    author: str
    year: int

# Initialize the database connection
db = Database(database='test_db', user='username', password='password', host='localhost', port=5432)

# Set up a table for books
db.books = Table(db, Book)

# Add a new Book to the database
new_book = Book(name="The Lord of the Rings", author="J. R. R. Tolkien", year=1964)
db.books.add(new_book)

# Retrieve and display Books from the database
books = db.books.find_many()
for book in books:
    print(book)

# Close the database connection
db.close()
```

## Installation

To install the Pydanql library, run the following pip command:
```bash
pip install pydanql
```

## Components

- `Database`: Manages the connection to a PostgreSQL database.
- `ObjectBaseModel`: An enhanced Pydantic model with predefined fields.
- `Table`: A utility class for CRUD operations on database tables.
- `DatabaseError`: A specialized exception class for database-related issues.

## Features & Examples

- **Create a new record:**
    ```python
    new_car = Car(brand="Tesla", model="Model S", year=2020, color="Blue", miles=1000.5)
    db.cars_table.add(new_car)
    ```

- **Update an existing record:**
    ```python
    existing_car = db.cars_table.find_one(id=1)
    existing_car.color = "Green"
    db.cars_table.replace(existing_car)
    ```

- **Delete an existing record:**
    ```python
    existing_car = db.cars_table.find_one(id=1)
    db.cars_table.delete(existing_car)
    ```

- **Find records with queries:**

    Pydanql supports multiple types of queries to provide you with powerful search functionality. Below are some examples of how to use different query types.

    - **Exact Match:**
        ```python
        blue_cars = db.cars_table.find_many(color='Blue')
        ```
    
    - **Like Query:**
        ```python
        similar_colors = db.cars_table.find_many(color={'like': 'blu'})
        ```
    
    - **Range Query:**
        ```python
        recent_cars = db.cars_table.find_many(year={'range': [2015, 2021]})
        ```
    
    - **In Query:**
        ```python
        cars_by_models = db.cars_table.find_many(model={'in': ['Model S', 'Model X']})
        ```
    
    - **Greater Than (gt):**
        ```python
        high_mileage_cars = db.cars_table.find_many(miles={'gt': 50000})
        ```
    
    - **Less Than (lt):**
        ```python
        low_mileage_cars = db.cars_table.find_many(miles={'lt': 30000})
        ```
        
    - **Sorting, Offset and Count:**
        ```python
        db.cars_table.find_many(sort='-year', offset=10, count=10)
        ```
        
    - **Single Record:**
        ```python
        newest_car = db.cars_table.find_one(sort='-year')
        ```
        
By using these query types, you can execute more complex searches and filters on your records, making Pydanql a versatile tool for interacting with your PostgreSQL database.

- **Count records:**
    ```python
    total_cars = db.cars_table.count()
    ```

- **Simple pagination:**
    ```python
    page_1_results = db.cars_table.page(page_number=1, page_size=5)
    ```

- **Model with more complex data types and a custom method:**
    ```python
    class Book(ObjectBaseModel):
        name: str
        author: str
        year: int
        available: bool
        dimensions: Tuple = Field(default=(8,8), data_type="int[]", constraints=["NOT NULL"])
        meta: Dict = Field(default={}, data_type="JSONB", constraints=["NOT NULL"])

        def description(self):
            return f"Title: {self.name}, Author: {self.author}, Year: {self.year}"
    
    new_book = Book(name="The Lord of the Rings", author="J. R. R. Tolkien", available=True, year=1964, dimensions=(16,23), meta={ 'language': 'en' })
    db.books.add(new_book)

    # Invoke the custom description method
    print(new_book.description())
    ```

## License

Pydanql is licensed under the MIT license.