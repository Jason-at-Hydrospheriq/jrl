import pytest
from src.dummy_class import dummy_class

def test_main():
    # Arrange
    dummy = dummy_class()

    # Act
    result = dummy.dummy_method()

    # Assert
    assert result == "This is a dummy method."

