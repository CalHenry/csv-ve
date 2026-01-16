# this file is usefull to run csv-ve from source as a module with 'uv run python -m csv-ve'

from .cli import csv_ve_cli

if __name__ == "__main__":
    csv_ve_cli()
