import pytest


@pytest.fixture
def temp_csv_with_headers(tmp_path):
    """
    Creates a temporary CSV file with headers for testing.
    tmp_path is a pytest built-in fixture that provides a temporary directory.
    """
    # Define your CSV content
    csv_content = """name,age,city
Alice,30,Paris
Bob,25,London
Charlie,35,Berlin"""

    # Create the temporary CSV file
    csv_file = tmp_path / "test_data.csv"
    csv_file.write_text(csv_content)

    return csv_file


@pytest.fixture
def temp_csv_no_headers(tmp_path):
    csv_content = """Alice,30,Paris
Bob,25,London"""
    csv_file = tmp_path / "no_headers.csv"
    csv_file.write_text(csv_content)
    return csv_file


@pytest.fixture
def temp_csv_empty(tmp_path):
    csv_content = """name,age,city"""  # Only headers
    csv_file = tmp_path / "empty.csv"
    csv_file.write_text(csv_content)
    return csv_file
