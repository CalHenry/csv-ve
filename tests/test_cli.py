from io import StringIO

import pytest
from dirty_equals import IsStr
from rich.console import Console
from typer.testing import CliRunner

from csv_ve.cli import THEME_ALIASES, csv_ve_cli, resolve_theme

runner = CliRunner()
# write rich to stdout - pytest don't see rich output to stdout otherwise
console = Console(file=StringIO())

# Issue:
# Can't capture rich output in stdout, result.stdout = ''
# Can't assert the error content


# CLI
class TestMainCommand:
    """Test the main CLI command"""

    def test_main_with_valid_csv_file(self, mock_csv_path, mock_app):
        """Test main command with a valid CSV file"""
        result = runner.invoke(csv_ve_cli, ["test.csv"])

        assert result.exit_code == 0
        mock_csv_path.assert_called_once_with("test.csv")
        mock_app.assert_called_once_with(
            csv_path="test.csv", theme=THEME_ALIASES["dark"]
        )
        mock_app.return_value.run.assert_called_once()

    def test_main_with_theme_option(self, mock_csv_path, mock_app):
        """Test --theme option"""
        result = runner.invoke(csv_ve_cli, ["test.csv", "--theme", "light"])

        assert result.exit_code == 0
        mock_app.assert_called_once_with(
            csv_path="test.csv", theme=THEME_ALIASES["light"]
        )
        mock_app.return_value.run.assert_called_once()

    def test_main_with_short_theme_option(self, mock_csv_path, mock_app):
        "Test -t option"
        result = runner.invoke(csv_ve_cli, ["test.csv", "-t", "dark"])

        # Assertions
        assert result.exit_code == 0
        mock_app.assert_called_once_with(
            csv_path="test.csv", theme=THEME_ALIASES["dark"]
        )

    def test_main_with_nonexistent_file(self, mock_csv_path):
        result = runner.invoke(csv_ve_cli, ["nonexistent.csv"])

        # Assertions
        assert result.exit_code == 1
        # assert "Error: File 'nonexistent.csv' not found" in result.stdout

    def test_main_with_non_csv_file(self, mock_csv_path):
        result = runner.invoke(csv_ve_cli, ["file.txt"])

        # Assertions
        assert result.exit_code == 1
        print(f"testes{result.stdout}")
        # assert "[red]Error: File 'nonexistent.csv' not found[/red]" in result.stdout

    def test_main_with_invalid_theme(self, mock_csv_path):
        result = runner.invoke(csv_ve_cli, ["test.csv", "--theme", "invalid-theme"])

        # Assertions
        assert result.exit_code == 1
        # assert "Error: Theme 'invalid-theme' not found" in result.stdout
        # assert "Available themes:" in result.stdout

    def test_main_with_valid_builtin_theme(self, mock_csv_path, mock_app):
        result = runner.invoke(csv_ve_cli, ["test.csv", "--theme", "nord"])

        # Assertions
        assert result.exit_code == 0
        mock_app.assert_called_once_with(csv_path="test.csv", theme="nord")

    def test_main_without_file_argument(self):
        result = runner.invoke(csv_ve_cli, [])

        # Assertions
        assert result.exit_code != 0
        # assert "Missing argument" in result.stdout or "Error" in result.stdout


# Themes
class TestResolveTheme:
    """Test the resolve_theme function"""

    def test_resolve_theme_none_returns_default_dark(self):
        """Test that None input returns the default dark theme"""
        assert resolve_theme(None) == THEME_ALIASES["dark"]

    def test_resolve_theme_dark_alias(self):
        """Test that 'dark' resolves to the dark theme alias"""
        assert resolve_theme("dark") == THEME_ALIASES["dark"]

    def test_resolve_theme_light_alias(self):
        """Test that 'light' resolves to the light theme alias"""
        assert resolve_theme("light") == THEME_ALIASES["light"]

    def test_resolve_theme_case_insensitive(self):
        """Test that theme resolution is case-insensitive for aliases"""
        assert resolve_theme("DARK") == THEME_ALIASES["dark"]
        assert resolve_theme("Light") == THEME_ALIASES["light"]
        assert resolve_theme("DaRk") == THEME_ALIASES["dark"]

    def test_resolve_theme_textual_builtin(self):
        """Test that textual builtin theme names pass through"""
        assert resolve_theme("nord") == "nord"
        assert resolve_theme("dracula") == "dracula"


class TestThemeAliases:
    """Test THEME_ALIASES constant"""

    def test_theme_aliases_contains_dark_and_light(self):
        assert "dark" in THEME_ALIASES
        assert "light" in THEME_ALIASES

    def test_theme_aliases_values_are_strings(self):
        for value in THEME_ALIASES.values():
            assert value == IsStr


class TestIntegration:
    """Integration tests using temporary files"""

    def test_with_real_csv_file(self, temp_csv_with_headers, mock_app):
        """Test with a real temporary CSV file"""
        # Create a temporary CSV file
        csv_path = temp_csv_with_headers

        # Run command
        result = runner.invoke(csv_ve_cli, [str(csv_path)])

        # Assertions
        assert result.exit_code == 0
        mock_app.assert_called_once()
        mock_app.return_value.run.assert_called_once()

    def test_with_real_non_csv_file(self, temp_txt):
        """Test with a real temporary non-CSV file"""
        text_file = temp_txt
        # Run command
        result = runner.invoke(csv_ve_cli, [str(text_file)])

        # Assertions
        assert result.exit_code == 1
        assert "is not a CSV file" in result.stdout
