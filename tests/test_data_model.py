# pytests for the file 'data_model.py' that manage the data from the file using Polars
# We use a fixture in conftest.py that creates a 3x3 csv file
from pathlib import Path
from unittest.mock import patch

import pytest
from dirty_equals import IsInt, IsList

from csv_ve.data_model import CSVDataModel


def test_load_valid_csv_with_headers(temp_csv_with_headers):
    """Test load csv file correctly and with headers and correct shape"""
    csv_path = temp_csv_with_headers

    model = CSVDataModel(str(csv_path))

    assert model.df is not None, "DataFrame should be loaded"
    assert model.modified is False, "Newly loaded file should not be modified"
    assert model.has_header is True, "Should detect headers"
    # data schema
    assert model.row_count() == IsInt(exactly=3), "Should have 3 data rows"
    assert model.column_count() == IsInt(exactly=3), "Should have 3 columns"
    # col names
    assert model.df.columns == IsList("name", "age", "city"), (
        "Column names should match"
    )


def test_non_existent_file():
    non_existent_path = Path("i/dont/exist/file.csv")

    # Patch the `load` method to do nothing during initialization
    with patch.object(CSVDataModel, "load", return_value=None):
        model = CSVDataModel(str(non_existent_path))

    # manually call `load` and expect filenotfound exception
    with pytest.raises(FileNotFoundError):
        model.load()
