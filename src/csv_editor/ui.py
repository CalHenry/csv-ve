from pathlib import Path

from data_model import CSVDataModel
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Footer, Header, Input, Label


class EditCellScreen(ModalScreen[str]):
    """Modal screen for editing a cell value"""

    def __init__(self, current_value: str, row: int, col: int):
        super().__init__()
        self.current_value = str(current_value)
        self.row = row
        self.col = col

    def compose(self) -> ComposeResult:
        with Container(id="edit-dialog"):
            yield Label(f"Edit cell ({self.row}, {self.col})")
            yield Input(value=self.current_value, id="cell-input")
            with Container(id="button-container"):
                yield Button("Save", variant="primary", id="save")
                yield Button("Cancel", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            input_widget = self.query_one("#cell-input", Input)
            self.dismiss(input_widget.value)
        else:
            self.dismiss(None)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.dismiss(event.value)


class CSVEditorApp(App):
    """A Textual app for editing CSV files"""

    CSS_PATH = "csveditorapp.tcss"
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("s", "save", "Save"),
        Binding("r", "reload", "Reload"),
        Binding("e", "edit_cell", "Edit Cell", show=True),
    ]

    def __init__(self, csv_path: str):
        super().__init__()
        self.csv_path = csv_path
        self.data_model = CSVDataModel(csv_path)

    def compose(self) -> ComposeResult:
        """Create child widgets"""
        yield Header()
        with Vertical(id="main-container"):
            yield DataTable(cursor_type="cell", header_height=2)
            yield Label("", id="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        """Load data when app starts"""
        self.load_data()

    def load_data(self) -> None:
        """Load CSV data into the DataTable"""
        table = self.query_one(DataTable)
        table.clear(columns=True)

        df = self.data_model.df

        if df is None:
            self.update_status("No data loaded")
            return

        # Add columns
        for col_name in df.columns:
            table.add_column(col_name, key=col_name)

        # Add rows
        for row in df.iter_rows():
            table.add_row(*row)

        self.update_status(
            f"Loaded: {self.csv_path} ({len(df)} rows, {len(df.columns)} cols)"
        )

    def update_status(self, message: str) -> None:
        """Update the status bar"""
        status = self.query_one("#status-bar", Label)
        modified = " [MODIFIED]" if self.data_model.modified else ""
        status.update(f"{message}{modified}")

    def action_edit_cell(self) -> None:
        """Open edit dialog for selected cell"""
        table = self.query_one(DataTable)

        if table.cursor_coordinate is None:
            return

        row_key, col_key = table.coordinate_to_cell_key(table.cursor_coordinate)
        row_idx = table.get_row_index(row_key)
        col_idx = list(table.columns.keys()).index(col_key)

        current_value = table.get_cell(row_key, col_key)

        def handle_edit(new_value: str | None) -> None:
            if new_value is not None:
                try:
                    # Update data model
                    self.data_model.set_cell(row_idx, col_idx, new_value)

                    # Update table display
                    table.update_cell(row_key, col_key, new_value)

                    self.update_status(f"Updated cell ({row_idx}, {col_idx})")
                except Exception as e:
                    self.update_status(f"Error: {e}")

        self.push_screen(EditCellScreen(current_value, row_idx, col_idx), handle_edit)

    def action_save(self) -> None:
        """Save the CSV file"""
        try:
            self.data_model.save()
            self.update_status("Saved successfully")
        except Exception as e:
            self.update_status(f"Save failed: {e}")

    def action_reload(self) -> None:
        """Reload the CSV file from disk"""
        try:
            self.data_model.reload()
            self.load_data()
            self.update_status("Reloaded from disk")
        except Exception as e:
            self.update_status(f"Reload failed: {e}")


def main():
    import sys

    if len(sys.argv) < 2:
        print("Usage: python app.py <csv_file>")
        sys.exit(1)

    csv_file = sys.argv[1]

    if not Path(csv_file).exists():
        print(f"Error: File '{csv_file}' not found")
        sys.exit(1)

    app = CSVEditorApp(csv_file)
    app.run()


if __name__ == "__main__":
    main()
