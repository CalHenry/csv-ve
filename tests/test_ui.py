from textual.widgets import DataTable

from csv_ve.ui import CSVEditorApp


# temp_csv_with_headers is a 3x3 csv - First row of the table a labeled row so the row index starts at -1
class TestBasicKeybinds:
    async def test_quit(self, temp_csv_with_headers):
        "Test that 'q' quit the app"
        app = CSVEditorApp(csv_path=temp_csv_with_headers, theme=None)

        async with app.run_test() as pilot:
            # Press 'q' to quit
            await pilot.press("q")
            assert not app.is_running

    async def test_ctrl_s_saves_file(self, temp_csv_with_headers):
        """
        Test that ctrl+s triggers save and writes to file
        - only test that the modified flag and notify
        - test on actually saving the file are in data_model.py
        """
        app = CSVEditorApp(csv_path=temp_csv_with_headers, theme=None)
        async with app.run_test() as pilot:
            app.data_model.modified = True
            # Simulate Ctrl+S keypress
            await pilot.press("ctrl+s")
            await pilot.pause()

            # check the file was actually written
            assert temp_csv_with_headers.exists()
            # check modified flag is cleared
            assert app.data_model.modified is False
            # check the notify
            notifications = app._notifications
            assert any("Saved" in n.message for n in notifications)


class TestVimKeybinds:
    async def test_table_left(self, temp_csv_with_headers):
        """Pressing 'h' moves the cursor left in the DataTable"""
        app = CSVEditorApp(csv_path=temp_csv_with_headers, theme=None)

        async with app.run_test() as pilot:
            table = app.query_one(DataTable)
            table.focus()
            await pilot.pause()

            table.move_cursor(column=1)
            initial_column = table.cursor_column

            # 'h' should move the cursor
            await pilot.press("h")
            await pilot.pause()
            assert table.cursor_column == initial_column - 1

    async def test_h_only_works_when_table_focused(self, temp_csv_with_headers):
        app = CSVEditorApp(csv_path=temp_csv_with_headers, theme=None)

        async with app.run_test() as pilot:
            table = app.query_one(DataTable)
            app.query_one("#formula_bar").focus()  # unfocus the table
            await pilot.pause()

            table.move_cursor(column=1)
            initial_column = table.cursor_column

            # 'h' should not move the cursor
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

            table.move_cursor(row=1)
            initial_row = table.cursor_row

            # 'j' should move the cursor
            await pilot.press("j")
            await pilot.pause()
            assert table.cursor_row == initial_row + 1

    async def test_j_only_works_when_table_focused(self, temp_csv_with_headers):
        app = CSVEditorApp(csv_path=temp_csv_with_headers, theme=None)

        async with app.run_test() as pilot:
            table = app.query_one(DataTable)
            app.query_one("#formula_bar").focus()  # unfocus the table
            await pilot.pause()

            table.move_cursor(row=1)
            initial_row = table.cursor_row

            # 'j' should not move the cursor
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

            # 'k' should move the cursor
            await pilot.press("k")
            await pilot.pause()
            assert table.cursor_row == initial_row - 1

    async def test_k_only_works_when_table_focused(self, temp_csv_with_headers):
        app = CSVEditorApp(csv_path=temp_csv_with_headers, theme=None)

        async with app.run_test() as pilot:
            table = app.query_one(DataTable)
            app.query_one("#formula_bar").focus()  # unfocus the table
            await pilot.pause()

            table.move_cursor(row=1)
            initial_row = table.cursor_row

            # 'k' should not move the cursor
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

            table.move_cursor(column=1)
            initial_column = table.cursor_column

            # 'l' should move the cursor
            await pilot.press("l")
            await pilot.pause()
            assert table.cursor_column == initial_column + 1

    async def test_l_only_works_when_table_focused(self, temp_csv_with_headers):
        app = CSVEditorApp(csv_path=temp_csv_with_headers, theme=None)

        async with app.run_test() as pilot:
            table = app.query_one(DataTable)
            app.query_one("#formula_bar").focus()  # unfocus the table
            await pilot.pause()

            table.move_cursor(column=1)
            initial_column = table.cursor_column

            # 'l' should not move the cursor
            await pilot.press("l")
            await pilot.pause()
            assert table.cursor_column == initial_column
