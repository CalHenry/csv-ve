import asyncio

from dirty_equals import Contains, HasLen
from textual.notifications import Notification
from textual.widgets import DataTable

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


class TestVimKeybinds:
    "test: h j k l G and g key behavior"

    async def test_table_left(self, temp_csv_with_headers):
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

    async def test_h_only_works_when_table_focused(self, temp_csv_with_headers):
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

    async def test_notifications_expires(self, temp_csv_with_headers) -> None:
        """Save notifications should expire from an app."""
        app = CSVEditorApp(temp_csv_with_headers, theme=None)
        async with app.run_test() as pilot:
            await pilot.press("ctrl+s")

            assert len(pilot.app._notifications) == 1
            # notifications last for ~4 sec
            await asyncio.sleep(5)
            assert len(pilot.app._notifications) == 0
