import pytest
from unittest.mock import Mock, patch
from pydanql.base import Database
from pydanql.errors import DatabaseError


def test_database_initialization():
    with patch('psycopg2.connect', return_value=Mock()):
        db = Database()
        assert db is not None
