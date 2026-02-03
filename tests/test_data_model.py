# pytests for the file 'data_model.py' that manage the data from the file using Polars
# We use a fixture in conftest.py that creates a 3x3 csv file
from pathlib import Path
from unittest.mock import patch

import polars as pl
import pytest
from dirty_equals import IsFalseLike, IsInt, IsList, IsTrueLike, IsTuple
from polars.testing import assert_series_equal

from csv_ve.data_model import CSVDataModel


# test load
def test_load_valid_csv_with_headers(temp_csv_with_headers):
    """Test load csv file correctly and with headers and correct shape"""
    csv_path = temp_csv_with_headers

    model = CSVDataModel(str(csv_path))

    assert model.df is not None, "DataFrame should be loaded"
    assert model.modified == IsFalseLike
    assert model.modified == IsTrueLike
    # data schema
    assert model.row_count() == IsInt(exactly=3)
    assert model.column_count() == IsInt(exactly=3)
    # col names
    assert model.df.columns == IsList("name", "age", "city"), (
        "Column names should match"
    )


def test_load_empty_csv(temp_csv_empty):
    """empty csv only has headers"""
    csv_path = temp_csv_empty

    model = CSVDataModel(str(csv_path))

    assert model.df is not None, "DataFrame should be loaded"
    assert model.modified == IsFalseLike
    assert model.modified == IsTrueLike
    # data schema
    assert model.row_count() == IsInt(exactly=0)
    assert model.column_count() == IsInt(exactly=3)
    # col names
    assert model.df.columns == IsList("name", "age", "city"), (
        "Column names should match"
    )


def test_non_existent_file():
    non_existent_path = Path("i/dont/exist/file.csv")

    # Patch the `load` method to do nothing during initialization
    with patch.object(CSVDataModel, "load", return_value=None):
        model = CSVDataModel(str(non_existent_path))

    with pytest.raises(FileNotFoundError):
        model.load()


# test save
def test_save_writes_csv_and_resets_modified(temp_csv_with_headers):
    model = CSVDataModel(temp_csv_with_headers)

    # Modify the dataframe
    model.df = model.df.with_columns((pl.col("age") * 10).alias("age10"))
    model.modified == IsTrueLike

    model.save()

    # Reload: modified should be false and 'age10' should be the same on both
    reloaded = pl.read_csv(temp_csv_with_headers)

    assert model.modified == IsFalseLike
    assert_series_equal(reloaded["age10"], model.df["age10"])


def test_save_raises_if_no_data(temp_csv_with_headers):
    model = CSVDataModel(temp_csv_with_headers)
    model.df = None  # simulate corrupted / unloaded state

    with pytest.raises(RuntimeError, match="No data to save"):
        model.save()


# test edit cells
def test_set_cell_no_data(temp_csv_with_headers):
    model = CSVDataModel(temp_csv_with_headers)
    model.df = None  # simulate no data

    with pytest.raises(RuntimeError, match="No data loaded"):
        model.set_cell(1, 1, "a")


def test_row_idx_is_not_negative(temp_csv_with_headers):
    model = CSVDataModel(temp_csv_with_headers)
    row_idx = -1

    with pytest.raises(IndexError, match=f"Row index {row_idx} out of bounds"):
        model.set_cell(row_idx, 1, "a")


def test_row_idx_is_not_bigger_than_df_len(temp_csv_with_headers):
    model = CSVDataModel(temp_csv_with_headers)
    row_idx = len(model.df) + 1

    with pytest.raises(IndexError, match=f"Row index {row_idx} out of bounds"):
        model.set_cell(row_idx, 1, "a")


def test_col_idx_is_not_negative(temp_csv_with_headers):
    model = CSVDataModel(temp_csv_with_headers)
    col_idx = -1

    with pytest.raises(IndexError, match=f"Column index {col_idx} out of bounds"):
        model.set_cell(1, col_idx, "a")


def test_col_idx_is_not_bigger_than_nbr_col(temp_csv_with_headers):
    model = CSVDataModel(temp_csv_with_headers)
    col_idx = len(model.df.columns) + 1

    with pytest.raises(IndexError, match=f"Column index {col_idx} out of bounds"):
        model.set_cell(1, col_idx, "a")


def test_set_cell_updates_value_and_marks_modified(temp_csv_with_headers):
    model = CSVDataModel(temp_csv_with_headers)
    model.set_cell(row_idx=1, col_idx=1, value=99)

    # Assert
    assert model.df["age"][1] == IsInt(exactly=99)
    assert model.df["age"].to_list() == IsList(30, 99, 35)
    assert model.modified == IsTrueLike


# test add new rows and columns
def test_row_count_no_data(temp_csv_with_headers):
    model = CSVDataModel(temp_csv_with_headers)
    model.df = None

    assert model.row_count() == IsInt(exactly=0)


def test_row_count_with_data(temp_csv_with_headers):
    model = CSVDataModel(temp_csv_with_headers)

    assert model.row_count() == IsInt(exactly=3)


def test_col_count_no_data(temp_csv_with_headers):
    model = CSVDataModel(temp_csv_with_headers)
    model.df = None

    assert model.column_count() == IsInt(exactly=0)


def test_col_count_with_data(temp_csv_with_headers):
    model = CSVDataModel(temp_csv_with_headers)

    assert model.column_count() == IsInt(exactly=3)


# test insert_row
def test_insert_row_no_data(temp_csv_with_headers):
    model = CSVDataModel(temp_csv_with_headers)
    model.df = None  # simulate no data

    with pytest.raises(RuntimeError, match="No data loaded"):
        model.insert_row(1)


def test_insert_row_idx_not_negative(temp_csv_with_headers):
    model = CSVDataModel(temp_csv_with_headers)
    row_idx = -1

    with pytest.raises(IndexError, match=f"Row index {row_idx} out of bounds"):
        model.insert_row(row_idx)


def test_insert_row_idx_is_not_bigger_than_nbr_col(temp_csv_with_headers):
    model = CSVDataModel(temp_csv_with_headers)
    row_idx = len(model.df.columns) + 1

    with pytest.raises(IndexError, match=f"Row index {row_idx} out of bounds"):
        model.insert_row(row_idx)


def test_insert_row_inserts_empty_row_at_index(temp_csv_with_headers):
    model = CSVDataModel(temp_csv_with_headers)
    model.modified == IsFalseLike
    nbr_rows_before = len(model.df)

    model.insert_row(row_idx=1)

    assert model.df.shape == IsTuple(nbr_rows_before + 1, 3)
    assert model.df.row(1) == IsTuple(None, None, None)
    assert model.modified == IsTrueLike
