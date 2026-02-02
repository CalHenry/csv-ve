from unittest.mock import Mock, patch

import pytest


## test_data_model.py
@pytest.fixture
def temp_csv_with_headers(tmp_path):
    """
    Creates a temporary CSV file with headers for testing.
    """

    csv_content = """name,age,city
Alice,30,Paris
Bob,25,London
Charlie,35,Berlin"""

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


## test_cli.py
@pytest.fixture
def mock_csv_path():
    """Fixture for a valid CSV path mock"""
    with patch("csv_ve.cli.Path") as mock_path_class:
        mock_path_instance = Mock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.suffix.lower.return_value = ".csv"
        mock_path_class.return_value = mock_path_instance
        yield mock_path_class


@pytest.fixture
def mock_app():
    """Fixture for CSVEditorApp mock"""
    with patch("csv_ve.cli.CSVEditorApp") as mock_app_class:
        mock_app_instance = Mock()
        mock_app_class.return_value = mock_app_instance
        yield mock_app_class


@pytest.fixture
def temp_txt(tmp_path):
    txt_content = """some text"""

    txt_file = tmp_path / "test_data.txt"
    txt_file.write_text(txt_content)

    return txt_file
