# Gamma Python PostgreSQL Library

## Introduction
The Gamma Library offers a simple and effective way to interact with a PostgreSQL database. It provides robust classes for database connections, data modeling, and CRUD (Create, Read, Update, Delete) operations. The library is equipped with built-in logging for easier debugging and error handling.

## Quick Example
Here's a brief example to show how to use the Gamma Python Library to interact with a PostgreSQL database, assuming that the relevant classes `Database`, `Table`, and `ObjectMetaModel` are imported from the Gamma package.

```python
# Initialize database
db = Database(database='test_db', user='username', password='password', host='localhost', port=5432)

# Define Car model
class Car(ObjectMetaModel):
    brand: str
    model: str
    year: int
    color: str
    miles: float

# Initialize Cars table
class Cars(Table):
    def __init__(self, db):
        super().__init__(db, Car, "Cars",
            fields=['brand','model','year','color','miles'],
            schema="""
                brand TEXT NOT NULL,
                model TEXT NOT NULL,
                year INTEGER NOT NULL,
                color TEXT NOT NULL,
                miles REAL NOT NULL
            """)

cars_table = Cars(db)

# Add a new car
new_car = Car(brand="Tesla", model="Model S", year=2020, color="Red", miles=1200.5)
cars_table.add(new_car)

# Fetch and delete a car
result = cars_table.find_one(brand="Tesla", color="Red")
cars_table.delete(result)

# Close database
db.close()
```

## Installation
To install, you can simply use pip:
```bash
pip install gamma-kit
```

## Components
- `Database`: Manages the connection to a PostgreSQL database.
- `ObjectMetaModel`: A base Pydantic model with some default fields.
- `Table`: A generic class to manage database tables.
- `DatabaseError`: A custom exception class for database-related issues.

## Features & Examples
- Create a new record:

    ```python
    new_car = Car(brand="Tesla", model="Model S", year=2020, color="Blue", miles=1000.5)
    cars_table.add(new_car)
    ```

- Replace an existing record:

    ```python
    existing_car = cars_table.find_one(id=1)
    existing_car.color = "Green"
    cars_table.replace(existing_car)
    ```

- Count records:

    ```python
    total_cars = cars_table.count()
    ```

- Pagination:

    ```python
    page_1_results = cars_table.page(page_number=1, page_size=5)
    ```


## Quick Note on Naming
In Germany, the name "Gamma" is associated with the Mickey Mouse character Eega Beeva, who has the magical ability to store an endless number of objects in his pocket. Similar to Eega Beeva's pocket, the Gamma Python Library aims to provide a versatile and almost endless way to handle and store your database objects.

## License
Gamma is licensed under the MIT license.