from rich.text import Text
from textual.reactive import reactive
from textual.widgets import Static


def excel_column_label(index: int) -> str:
    label = ""
    while index > 0:
        index -= 1
        label = chr(65 + (index % 26)) + label
        index //= 26
    return label


class IndexColumn(Static):
    """Pure visual Excel-like column index row"""

    column_count = reactive(0)
    column_width = reactive(10)

    def __init__(self, column_count: int = 0, column_width: int = 10, **kwargs):
        super().__init__(**kwargs)
        self.column_count = column_count
        self.column_width = column_width

    def render(self) -> Text:
        text = Text(no_wrap=True)

        for i in range(1, self.column_count + 1):
            label = excel_column_label(i)
            text.append(label.center(self.column_width), style="bold")

        return text
