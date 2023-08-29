import pytest
from unittest.mock import Mock, patch
from gamma.base import Database
from gamma.errors import DatabaseError


def test_database_initialization():
    with patch('psycopg2.connect', return_value=Mock()):
        db = Database()
        assert db is not None
