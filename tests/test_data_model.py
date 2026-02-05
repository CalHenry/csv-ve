# pytests for the file 'data_model.py' that manage the data from the file using Polars
# We use a fixture in conftest.py that creates a 3x3 csv file
from pathlib import Path
from unittest.mock import patch

import polars as pl
import pytest
from dirty_equals import HasLen, IsInt
from polars.testing import assert_series_equal

from csv_ve.data_model import CSVDataModel


class TestLoad:
    "test: load()"

    def test_load_valid_csv_with_headers(self, temp_csv_with_headers):
        """Test load csv file correctly and with headers and correct shape"""
        model = CSVDataModel(temp_csv_with_headers)
        assert model.df is not None
        assert model.modified is False

        assert model.row_count() == 3
        assert model.column_count() == 3
        assert model.df.columns == ["name", "age", "city"], "Column names should match"

    def test_load_empty_csv(self, temp_csv_empty):
        """empty csv with only headers"""
        model = CSVDataModel(temp_csv_empty)
        assert model.df is not None
        assert model.modified is False

        assert model.row_count() == 0
        assert model.column_count() == 3
        assert model.df.columns == ["name", "age", "city"], "Column names should match"

    def test_load_non_existent_file(self):
        non_existent_path = Path("i/dont/exist/file.csv")

        # Patch the `load` method to do nothing during initialization
        with patch.object(CSVDataModel, "load", return_value=None):
            model = CSVDataModel(str(non_existent_path))

        with pytest.raises(
            FileNotFoundError, match=f"CSV file not found: {non_existent_path}"
        ):
            model.load()


# reload() is not tested because it's just a wrapper of load()


class TestSave:
    "test: save()"

    def test_save_writes_csv_and_resets_modified(self, temp_csv_with_headers):
        model = CSVDataModel(temp_csv_with_headers)
        assert model.df is not None
        model.df = model.df.with_columns((pl.col("age") * 10).alias("age10"))
        model.modified is True

        model.save()

        # Reload: modified should be false and 'age10' should be the same on both
        reloaded = pl.read_csv(temp_csv_with_headers)

        assert model.modified is False
        assert_series_equal(reloaded["age10"], model.df["age10"])

    def test_save_raises_if_no_data(self, temp_csv_with_headers):
        model = CSVDataModel(temp_csv_with_headers)
        model.df = None  # simulate corrupted / unloaded state

        with pytest.raises(RuntimeError, match="No data to save"):
            model.save()


class TestSetCell:
    "test: set_cell()"

    def test_set_cell_no_data(self, temp_csv_with_headers):
        model = CSVDataModel(temp_csv_with_headers)
        model.df = None  # simulate no data

        with pytest.raises(RuntimeError, match="No data loaded"):
            model.set_cell(1, 1, "a")

    def test_row_idx_is_not_negative(self, temp_csv_with_headers):
        model = CSVDataModel(temp_csv_with_headers)
        row_idx = -1

        with pytest.raises(IndexError, match=f"Row index {row_idx} out of bounds"):
            model.set_cell(row_idx, 1, "a")

    def test_row_idx_is_not_out_of_bound(self, temp_csv_with_headers):
        model = CSVDataModel(temp_csv_with_headers)
        assert model.df is not None
        row_idx = len(model.df) + 1

        with pytest.raises(IndexError, match=f"Row index {row_idx} out of bounds"):
            model.set_cell(row_idx, 1, "a")

    def test_col_idx_is_not_negative(self, temp_csv_with_headers):
        model = CSVDataModel(temp_csv_with_headers)
        col_idx = -1

        with pytest.raises(IndexError, match=f"Column index {col_idx} out of bounds"):
            model.set_cell(1, col_idx, "a")

    def test_col_idx_is_not_out_of_bound(self, temp_csv_with_headers):
        model = CSVDataModel(temp_csv_with_headers)
        assert model.df is not None
        col_idx = len(model.df.columns) + 1

        with pytest.raises(IndexError, match=f"Column index {col_idx} out of bounds"):
            model.set_cell(1, col_idx, "a")

    def test_set_cell_updates_value_and_marks_modified(self, temp_csv_with_headers):
        model = CSVDataModel(temp_csv_with_headers)
        assert model.df is not None
        model.set_cell(row_idx=1, col_idx=1, value=99)

        assert model.df["age"][1] == IsInt(exactly=99)
        assert model.df["age"].to_list() == HasLen(3)
        assert model.modified is True


class TestRowCount:
    "test: row_count()"

    def test_row_count_no_data(self, temp_csv_with_headers):
        model = CSVDataModel(temp_csv_with_headers)
        model.df = None  # simulate no data

        assert model.row_count() == 0

    def test_row_count_with_data(self, temp_csv_with_headers):
        model = CSVDataModel(temp_csv_with_headers)

        assert model.row_count() == 3

    def test_col_count_no_data(self, temp_csv_with_headers):
        model = CSVDataModel(temp_csv_with_headers)
        model.df = None  # simulate no data

        assert model.column_count() == 0

    def test_col_count_with_data(self, temp_csv_with_headers):
        model = CSVDataModel(temp_csv_with_headers)

        assert model.column_count() == 3


class TestInsertRow:
    "test: insert_row()"

    def test_insert_row_with_no_data(self, temp_csv_with_headers):
        "test: insert_row()"
        model = CSVDataModel(temp_csv_with_headers)
        model.df = None  # simulate no data

        with pytest.raises(RuntimeError, match="No data loaded"):
            model.insert_row(1)

    def test_insert_row_idx_not_negative(self, temp_csv_with_headers):
        "test: insert_row()"
        model = CSVDataModel(temp_csv_with_headers)
        row_idx = -1

        with pytest.raises(IndexError, match=f"Row index {row_idx} out of bounds"):
            model.insert_row(row_idx)

    def test_insert_row_idx_is_not_out_of_bound(self, temp_csv_with_headers):
        "test: insert_row()"
        model = CSVDataModel(temp_csv_with_headers)
        assert model.df is not None
        row_idx = len(model.df.columns) + 1

        with pytest.raises(IndexError, match=f"Row index {row_idx} out of bounds"):
            model.insert_row(row_idx)

    def test_insert_row_inserts_empty_row_at_index(self, temp_csv_with_headers):
        "test: insert_row()"
        model = CSVDataModel(temp_csv_with_headers)
        assert model.df is not None
        model.modified is False
        nbr_rows_before = len(model.df)

        model.insert_row(row_idx=1)

        assert model.df.shape == (nbr_rows_before + 1, 3)
        assert model.df.row(1) == (None, None, None)
        assert model.modified is True


class TestInsertColumn:
    "test insert_column()"

    def test_insert_col_no_data(self, temp_csv_with_headers):
        model = CSVDataModel(temp_csv_with_headers)
        model.df = None  # simulate no data

        with pytest.raises(RuntimeError, match="No data loaded"):
            model.insert_column(1)

    def test_insert_col_idx_not_negative(self, temp_csv_with_headers):
        model = CSVDataModel(temp_csv_with_headers)
        row_idx = -1

        with pytest.raises(IndexError, match=f"Column index {row_idx} out of bounds"):
            model.insert_column(row_idx)

    def test_insert_column_beginning(self, temp_csv_with_headers):
        model = CSVDataModel(temp_csv_with_headers)
        assert model.df is not None
        model.insert_column(0, "new_beginning")

        assert model.df.columns[0] == "new_beginning"
        assert model.df.columns == ["new_beginning", "name", "age", "city"]
        assert len(model.df) == 3  # assert insert_col don't change the rows nbr
        assert len(model.df.columns) == 4
        assert model.modified is True

    def test_insert_column_in_middle(self, temp_csv_with_headers):
        model = CSVDataModel(temp_csv_with_headers)
        assert model.df is not None
        model.insert_column(1, "new_middle")

        assert model.df.columns[1] == "new_middle"
        assert model.df.columns == ["name", "new_middle", "age", "city"]
        assert len(model.df) == 3
        assert len(model.df.columns) == 4
        assert model.modified is True

    def test_insert_column_end(self, temp_csv_with_headers):
        model = CSVDataModel(temp_csv_with_headers)
        assert model.df is not None
        model.insert_column(3, "new_end")

        assert model.df.columns[-1] == "new_end"
        assert model.df.columns == ["name", "age", "city", "new_end"]
        assert len(model.df) == 3
        assert len(model.df.columns) == 4
        assert model.modified is True

    def test_insert_column_no_name(self, temp_csv_with_headers):
        "no names -> takes the"
        model = CSVDataModel(temp_csv_with_headers)
        assert model.df is not None
        col_idx = 1
        model.insert_column(col_idx)

        assert model.df.columns[1] == f"Column_{col_idx}"
        assert len(model.df) == 3
        assert len(model.df.columns) == 4
        assert model.modified is True

    def test_insert_column_auto_name(self, temp_csv_with_headers):
        "test no collisions between new names and existant names."
        model = CSVDataModel(temp_csv_with_headers)
        assert model.df is not None
        model.df = model.df.rename(
            {"age": "Column_1"}
        )  # we have to rename to the default col name of insert_column() to test
        print(model.df.columns)
        model.insert_column(2)
        print(model.df.columns)
        assert (
            model.df.columns[2] == "Column_2"
        )  # Column_1 already existing so it uses the next one: Column_2
        assert model.modified is True

    def test_insert_column_new_values_none(self, temp_csv_with_headers):
        "new values in the col should be = None"
        model = CSVDataModel(temp_csv_with_headers)
        assert model.df is not None

        model.insert_column(1, "Test_Col")
        assert model.df["Test_Col"].to_list() == [None, None, None]


class TestDeleteRow:
    "test: delete_row()"

    def test_del_row_no_data(self, temp_csv_with_headers):
        model = CSVDataModel(temp_csv_with_headers)
        model.df = None  # simulate no data

        with pytest.raises(RuntimeError, match="No data loaded"):
            model.delete_row(1)

    def test_del_row_idx_not_negative(self, temp_csv_with_headers):
        model = CSVDataModel(temp_csv_with_headers)
        row_idx = -1

        with pytest.raises(IndexError, match=f"Row index {row_idx} out of bounds"):
            model.delete_row(row_idx)

    def test_del_col_idx_not_out_of_bound(self, temp_csv_with_headers):
        model = CSVDataModel(temp_csv_with_headers)
        assert model.df is not None
        row_idx = len(model.df.columns) + 1

        with pytest.raises(IndexError, match=f"Row index {row_idx} out of bounds"):
            model.delete_row(row_idx)

    def test_del_row_cant_del_last_existing_row(self, temp_csv_with_headers):
        "We should not be able to delete row if the table is 1 row (where is the table then)"
        model = CSVDataModel(temp_csv_with_headers)
        assert model.df is not None
        model.df = model.df.head(1)

        with pytest.raises(ValueError, match="Cannot delete the last remaining row"):
            model.delete_row(0)

    def test_delete_row_remove_correct_row(self, temp_csv_with_headers):
        """Specified row should be deleted and marks data as modified"""
        model = CSVDataModel(temp_csv_with_headers)
        assert model.df is not None
        assert model.modified is False

        model.delete_row(1)

        assert len(model.df) == 2
        assert model.df["name"].to_list() == HasLen(2)
        assert model.df["age"].to_list() == HasLen(2)
        assert model.modified is True


class TestDeleteCol:
    "test: delete_column()"

    def test_del_col_no_data(self, temp_csv_with_headers):
        model = CSVDataModel(temp_csv_with_headers)
        model.df = None  # simulate no data

        with pytest.raises(RuntimeError, match="No data loaded"):
            model.delete_column(1)

    def test_del_col_idx_not_negative(self, temp_csv_with_headers):
        model = CSVDataModel(temp_csv_with_headers)
        col_idx = -1

        with pytest.raises(IndexError, match=f"Column index {col_idx} out of bounds"):
            model.delete_column(col_idx)

    def test_del_col_idx_not_out_of_bound(self, temp_csv_with_headers):
        model = CSVDataModel(temp_csv_with_headers)
        col_idx = -1

        with pytest.raises(IndexError, match=f"Column index {col_idx} out of bounds"):
            model.delete_column(col_idx)
        assert model.df is not None
        col_idx = len(model.df.columns) + 1

        with pytest.raises(IndexError, match=f"Column index {col_idx} out of bounds"):
            model.delete_column(col_idx)

    def test_del_col_cant_del_last_existing_col(self, temp_csv_with_headers):
        "We should not be able to delete row if the table is 1 row (where is the table then)"
        model = CSVDataModel(temp_csv_with_headers)
        assert model.df is not None
        model.df = model.df.select(pl.first())  # keep only first column

        with pytest.raises(ValueError, match="Cannot delete the last remaining column"):
            model.delete_column(0)

    def test_delete_col_remove_correct_col(self, temp_csv_with_headers):
        """Specified col should be deleted and marks data as modified"""
        model = CSVDataModel(temp_csv_with_headers)
        assert model.df is not None
        model.modified is False

        model.delete_column(1)

        assert len(model.df.columns) == 2
        assert model.modified is True
