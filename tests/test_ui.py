import asyncio

from dirty_equals import Contains, HasLen, IsStr
from textual.widgets import DataTable, Input

from csv_ve.screens.goto_cell_screen import CoordInputScreen
from csv_ve.ui import CSVEditorApp


# temp_csv_with_headers is a 3x3 csv - First row of the table a labeled row so the row index starts at -1
class TestBasicKeybinds:
    "test: q and ctrl+s key behavior"

    async def test_quit(self, temp_csv_with_headers):
        "Test that 'q' quit the app"
        app = CSVEditorApp(csv_path=temp_csv_with_headers, theme=None)

        async with app.run_test() as pilot:
            await pilot.press("q")
            assert not app.is_running

    async def test_ctrl_s_saves_file(self, temp_csv_with_headers):
        """
        Test that ctrl+s triggers save and writes to file
        - only test that the modified flag and notify
        - test on actually saving the file are in test_data_model.py
        """
        app = CSVEditorApp(csv_path=temp_csv_with_headers, theme=None)
        async with app.run_test() as pilot:
            app.data_model.modified = True

            await pilot.press("ctrl+s")
            await pilot.pause()

            # check the file was actually written
            assert temp_csv_with_headers.exists()
            assert app.data_model.modified is False
            notifications = app._notifications
            assert any("Saved" in n.message for n in notifications)

    async def test_copy_cell_content(self, temp_csv_with_headers) -> None:
        """
        test: 'ctrl+c to copy highlighted cell content.
        test that pressing ctrl+c copies the content of the cell
        and that the copied content is the value under the cursor even after it has moved
        """
        app = CSVEditorApp(csv_path=temp_csv_with_headers, theme=None)
        async with app.run_test() as pilot:
            app.data_model.modified = True
            table = app.query_one(DataTable)
            # clipboard should be empty by default
            assert app.clipboard == ""

            await pilot.press("ctrl+c")
            await pilot.pause()
            # default cursor location is (0:0)
            assert app.clipboard == "Alice"

            table.move_cursor(row=2, column=2)  # 3rd row, 3rd col
            await pilot.pause()
            await pilot.press("ctrl+c")
            await pilot.pause()
            assert app.clipboard == "Berlin"

    async def test_add_new_row(self, temp_csv_with_headers) -> None:
        "pressing 'n' should add a row to the table"
        app = CSVEditorApp(csv_path=temp_csv_with_headers, theme=None)

        async with app.run_test() as pilot:
            initial_row_count = app.data_model.row_count()

            await pilot.press("n")
            assert app.data_model.row_count() == initial_row_count + 1

    async def test_add_new_col(self, temp_csv_with_headers) -> None:
        "pressing 'b' should add a col to the table"
        app = CSVEditorApp(csv_path=temp_csv_with_headers, theme=None)

        async with app.run_test() as pilot:
            initial_col_count = app.data_model.column_count()

            await pilot.press("b")
            assert app.data_model.column_count() == initial_col_count + 1

    async def test_del_row(self, temp_csv_with_headers) -> None:
        "pressing 'ctrl+n' should remove a row to the table"
        app = CSVEditorApp(csv_path=temp_csv_with_headers, theme=None)

        async with app.run_test() as pilot:
            initial_row_count = app.data_model.row_count()

            await pilot.press("ctrl+n")
            assert app.data_model.row_count() == initial_row_count - 1

    async def test_del_col(self, temp_csv_with_headers) -> None:
        "pressing 'ctrl+b' should remove a col to the table"
        app = CSVEditorApp(csv_path=temp_csv_with_headers, theme=None)

        async with app.run_test() as pilot:
            initial_col_count = app.data_model.column_count()

            await pilot.press("ctrl+b")
            assert app.data_model.column_count == initial_col_count - 1


class TestVimKeybinds:
    "test: h j k l G and g"

    async def test_table_left(self, temp_csv_with_headers) -> None:
        """Pressing 'h' moves the cursor left in the DataTable"""
        app = CSVEditorApp(csv_path=temp_csv_with_headers, theme=None)

        async with app.run_test() as pilot:
            table = app.query_one(DataTable)
            table.focus()
            await pilot.pause()
            table.move_cursor(column=1)
            initial_column = table.cursor_column

            await pilot.press("h")
            await pilot.pause()

            assert table.cursor_column == initial_column - 1

    async def test_h_only_works_when_table_focused(self, temp_csv_with_headers) -> None:
        app = CSVEditorApp(csv_path=temp_csv_with_headers, theme=None)

        async with app.run_test() as pilot:
            table = app.query_one(DataTable)
            app.query_one("#formula_bar").focus()  # unfocus the table
            await pilot.pause()
            initial_column = table.cursor_column

            await pilot.press("h")
            await pilot.pause()

            assert table.cursor_column == initial_column

    async def test_table_down(self, temp_csv_with_headers):
        """Pressing 'j' moves the cursor down in the DataTable"""
        app = CSVEditorApp(csv_path=temp_csv_with_headers, theme=None)

        async with app.run_test() as pilot:
            table = app.query_one(DataTable)
            table.focus()
            await pilot.pause()
            initial_row = table.cursor_row

            await pilot.press("j")
            await pilot.pause()

            assert table.cursor_row == initial_row + 1

    async def test_j_only_works_when_table_focused(self, temp_csv_with_headers):
        app = CSVEditorApp(csv_path=temp_csv_with_headers, theme=None)

        async with app.run_test() as pilot:
            table = app.query_one(DataTable)
            app.query_one("#formula_bar").focus()  # unfocus the table
            await pilot.pause()
            initial_row = table.cursor_row

            await pilot.press("j")
            await pilot.pause()

            assert table.cursor_row == initial_row

    async def test_table_up(self, temp_csv_with_headers):
        """Pressing 'k' moves the cursor up in the DataTable"""
        app = CSVEditorApp(csv_path=temp_csv_with_headers, theme=None)

        async with app.run_test() as pilot:
            table = app.query_one(DataTable)
            table.focus()
            await pilot.pause()
            table.move_cursor(row=1)
            initial_row = table.cursor_row

            await pilot.press("k")
            await pilot.pause()

            assert table.cursor_row == initial_row - 1

    async def test_k_only_works_when_table_focused(self, temp_csv_with_headers):
        app = CSVEditorApp(csv_path=temp_csv_with_headers, theme=None)

        async with app.run_test() as pilot:
            table = app.query_one(DataTable)
            app.query_one("#formula_bar").focus()  # unfocus the table
            await pilot.pause()
            initial_row = table.cursor_row

            await pilot.press("k")
            await pilot.pause()

            assert table.cursor_row == initial_row

    async def test_table_right(self, temp_csv_with_headers):
        """Pressing 'l' moves the cursor right in the DataTable"""
        app = CSVEditorApp(csv_path=temp_csv_with_headers, theme=None)

        async with app.run_test() as pilot:
            table = app.query_one(DataTable)
            table.focus()
            await pilot.pause()
            initial_column = table.cursor_column

            await pilot.press("l")
            await pilot.pause()

            assert table.cursor_column == initial_column + 1

    async def test_l_only_works_when_table_focused(self, temp_csv_with_headers):
        app = CSVEditorApp(csv_path=temp_csv_with_headers, theme=None)

        async with app.run_test() as pilot:
            table = app.query_one(DataTable)
            app.query_one("#formula_bar").focus()  # unfocus the table
            await pilot.pause()
            initial_column = table.cursor_column

            await pilot.press("l")
            await pilot.pause()

            assert table.cursor_column == initial_column

    async def test_table_bottom(self, temp_csv_with_headers):
        """Pressing 'G' moves the cursor to the bottom of the DataTable"""
        app = CSVEditorApp(csv_path=temp_csv_with_headers, theme=None)

        async with app.run_test() as pilot:
            table = app.query_one(DataTable)
            table.focus()
            await pilot.pause()
            row_count = table.row_count

            await pilot.press("G")
            await pilot.pause()

            assert table.cursor_row == row_count - 1  # row index starts at 0

    async def test_G_only_works_when_table_focused(self, temp_csv_with_headers):
        app = CSVEditorApp(csv_path=temp_csv_with_headers, theme=None)

        async with app.run_test() as pilot:
            table = app.query_one(DataTable)
            app.query_one("#formula_bar").focus()  # unfocus the table
            await pilot.pause()
            initial_row_idx = table.cursor_row

            await pilot.press("G")
            await pilot.pause()

            assert table.cursor_row == initial_row_idx

    async def test_table_top(self, temp_csv_with_headers):
        """Pressing 'g' moves the cursor to the top of the DataTable"""
        app = CSVEditorApp(csv_path=temp_csv_with_headers, theme=None)

        async with app.run_test() as pilot:
            table = app.query_one(DataTable)
            table.focus()
            await pilot.pause()

            await pilot.press("g")
            await pilot.pause()

            assert table.cursor_row == 0  # row index starts at 0

    async def test_g_only_works_when_table_focused(self, temp_csv_with_headers):
        app = CSVEditorApp(csv_path=temp_csv_with_headers, theme=None)

        async with app.run_test() as pilot:
            table = app.query_one(DataTable)
            app.query_one("#formula_bar").focus()  # unfocus the table
            await pilot.pause()
            initial_row_idx = table.cursor_row

            await pilot.press("g")
            await pilot.pause()

            assert table.cursor_row == initial_row_idx


class TestLoadData:
    "test: load_data()"

    async def test_load_data_no_data(slef, temp_csv_with_headers):
        app = CSVEditorApp(temp_csv_with_headers, theme=None)
        async with app.run_test() as pilot:
            app.data_model.df = None
            app.load_data()
            await pilot.pause()

            assert app.sub_title == "No data loaded"

    async def test_load_data_row(self, temp_csv_with_headers):
        app = CSVEditorApp(temp_csv_with_headers, theme=None)

        async with app.run_test() as pilot:
            app.load_data()
            await pilot.pause()
            table = app.query_one(DataTable)

            assert table.row_count == 3
            assert table.columns == HasLen(3)
            assert app.sub_title == Contains("test_data.csv | 3 rows × 3 cols")


class TestNotifications:
    "test: notifications of the app with 'app.notify()"

    async def test_save_notif(self, temp_csv_with_headers) -> None:
        """reload should produce a notif."""
        app = CSVEditorApp(temp_csv_with_headers, theme=None)
        async with app.run_test() as pilot:
            assert len(pilot.app._notifications) == 0
            await pilot.press("ctrl+s")
            await pilot.pause()

            assert len(pilot.app._notifications) == 1

    async def test_reload_notif(self, temp_csv_with_headers) -> None:
        """reload should produce a notif."""
        app = CSVEditorApp(temp_csv_with_headers, theme=None)
        async with app.run_test() as pilot:
            assert len(pilot.app._notifications) == 0
            await pilot.press("ctrl+r")
            await pilot.pause()

            assert len(pilot.app._notifications) == 1

    async def test_notifications_expires(self, temp_csv_with_headers) -> None:
        """Save notifications should expire from an apps"""
        app = CSVEditorApp(temp_csv_with_headers, theme=None)
        async with app.run_test() as pilot:
            await pilot.press("ctrl+s")

            assert len(pilot.app._notifications) == 1
            # notifications last for ~4 sec
            await asyncio.sleep(5)
            assert len(pilot.app._notifications) == 0


class TestFormulaBar:
    "test: on_data_table_cell_highlighted()"

    async def test_formula_bat_value_updates(self, temp_csv_with_headers) -> None:
        """value bar should display the value under the cursor (highlighted cell)"""
        app = CSVEditorApp(temp_csv_with_headers, theme=None)
        async with app.run_test() as pilot:
            table = app.query_one(DataTable)
            formula_bar = app.query_one("#formula_bar", Input)
            await pilot.pause()
            # Default position is first cell first col (0:0)
            assert formula_bar.value == IsStr(regex="Alice")

            table.move_cursor(row=1, column=1)  # (1:1)
            await pilot.pause()
            # formula_bar.value returns strings
            assert formula_bar.value == IsStr(regex="25")

    #! Todo: Handle case where cell might not exist


class TestEditCell:
    "test: action_edit_cell()"


class TestGotocell:
    "test: action_goto_cell()"

    async def test_goto_cell_opens_coord_input_screen(self, temp_csv_with_headers):
        """Pressing 'ctrl+g should open CoordInputScreen"""
        app = CSVEditorApp(csv_path=temp_csv_with_headers, theme=None)

        async with app.run_test() as pilot:
            await pilot.press("ctrl+g")
            assert isinstance(app.screen, CoordInputScreen)

    async def test_goto_cell_passes_correct_max_values(self, temp_csv_with_headers):
        """Test that max_row and max_col are correctly passed to CoordInputScreen"""
        app = CSVEditorApp(csv_path=temp_csv_with_headers, theme=None)

        async with app.run_test() as pilot:
            table = app.query_one(DataTable)

            expected_max_row = table.row_count
            expected_max_col = len(table.columns)

            await pilot.press("ctrl+g")
            await pilot.pause()

            assert app.screen.max_row == expected_max_row
            assert app.screen.max_col == expected_max_col

    async def test_goto_valid_coordinates(self, temp_csv_with_headers):
        """Test moving cursor to valid coordinates"""
        app = CSVEditorApp(csv_path=temp_csv_with_headers, theme=None)

        async with app.run_test() as pilot:
            table = app.query_one(DataTable)

            # Open navigation screen
            await pilot.press("ctrl+g")
            # input is in 3 parts 'row' ':' and 'col'
            await pilot.click("#coord_input")
            await pilot.press("2", ":", "1", "enter")
            await pilot.pause()

            assert table.cursor_row == 2
            assert table.cursor_column == 0

    async def test_goto_coordinates_row_only(self, temp_csv_with_headers) -> None:
        """Test row coordinate only (col should stay current)"""
        app = CSVEditorApp(csv_path=temp_csv_with_headers, theme=None)

        async with app.run_test() as pilot:
            table = app.query_one(DataTable)

            table.move_cursor(row=0, column=2)
            await pilot.pause()
            initial_col = table.cursor_column

            await pilot.press("ctrl+g")

            await pilot.click("#coord_input")
            await pilot.press("3", ":", "enter")
            await pilot.pause()

            # row should change, column should remain the same
            assert table.cursor_row == 2
            assert table.cursor_column == initial_col

    async def test_goto_coordinates_col_only(self, temp_csv_with_headers) -> None:
        """Test row coordinate only (row should stay current)"""
        app = CSVEditorApp(csv_path=temp_csv_with_headers, theme=None)

        async with app.run_test() as pilot:
            table = app.query_one(DataTable)

            table.move_cursor(row=2, column=0)
            await pilot.pause()
            initial_row = table.cursor_row

            await pilot.press("ctrl+g")

            await pilot.click("#coord_input")
            await pilot.press(":", "3", "enter")
            await pilot.pause()

            # row should change, column should remain the same
            assert table.cursor_row == initial_row
            assert table.cursor_column == 2
