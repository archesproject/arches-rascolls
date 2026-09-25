from pathlib import Path

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

SOURCE_FILE_PATTERNS = ("*.xlsx", "*.zip")

IMPORTER_SUBCOMMANDS = {
    "tile-excel": "tile-excel-importer",
    "branch-excel": "branch-excel-importer",
}


class Command(BaseCommand):
    help = (
        "Import RaSColls *.xlsx and *.zip files and rebuild descriptors, search index, and report configs.\n\n"
        "Examples:\n"
        "  python manage.py load_rascolls_data ../rascolls-data-pkg\n"
        "  python manage.py load_rascolls_data ../rascolls-data-pkg --format branch-excel"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "data_dir",
            help="Path to the rascolls-data-pkg directory containing *.xlsx and/or *.zip files.",
        )
        parser.add_argument(
            "--format",
            choices=list(IMPORTER_SUBCOMMANDS.keys()),
            default="tile-excel",
            help="Import format to use (default: tile-excel).",
        )

    def handle(self, *args, **options):
        data_dir = Path(options["data_dir"]).resolve()
        if not data_dir.is_dir():
            raise CommandError(f"'{data_dir}' is not a directory.")

        self.stdout.write("\n>>> report_configs load")
        call_command("report_configs", "load")

        source_files = sorted(
            path for pattern in SOURCE_FILE_PATTERNS for path in data_dir.glob(pattern)
        )
        if not source_files:
            patterns = ", ".join(SOURCE_FILE_PATTERNS)
            raise CommandError(f"No {patterns} files found in '{data_dir}'.")

        subcommand = IMPORTER_SUBCOMMANDS[options["format"]]
        for source_file in source_files:
            self.stdout.write(f"\n>>> etl {subcommand} -s {source_file} -mp --no-index")
            call_command("etl", subcommand, "-s", str(source_file), "-mp", "--no-index")

        self.stdout.write("\n>>> resources calculate_descriptors")
        call_command("resources", "calculate_descriptors", "-y")

        self.stdout.write("\n>>> arches_search reindex_database -mp")
        call_command("arches_search", "reindex_database", "-mp")

        self.stdout.write(self.style.SUCCESS("\nDone."))
