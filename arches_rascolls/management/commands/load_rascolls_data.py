from pathlib import Path

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

IMPORTER_SUBCOMMANDS = {
    "tile-excel": "tile-excel-importer",
    "branch-excel": "branch-excel-importer",
}


class Command(BaseCommand):
    help = (
        "Import RaSColls *.xlsx files and rebuild descriptors, search index, and report configs.\n\n"
        "Examples:\n"
        "  python manage.py load_rascolls_data ../rascolls-data-pkg\n"
        "  python manage.py load_rascolls_data ../rascolls-data-pkg --format branch-excel"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "data_dir",
            help="Path to the rascolls-data-pkg directory containing *.xlsx files.",
        )
        parser.add_argument(
            "--format",
            choices=list(IMPORTER_SUBCOMMANDS.keys()),
            default="tile-excel",
            help="Import format to use (default: tile-excel).",
        )
        parser.add_argument(
            "-mxp",
            "--max-processes",
            dest="mxp",
            type=int,
            default=5,
            help="Number of parallel processes to use for the ETL import and search reindex (default: 5).",
        )

    def handle(self, *args, **options):
        data_dir = Path(options["data_dir"]).resolve()
        if not data_dir.is_dir():
            raise CommandError(f"'{data_dir}' is not a directory.")

        self.stdout.write("\n>>> report_configs load")
        call_command("report_configs", "load")

        xlsx_files = sorted(data_dir.glob("*.xlsx"))
        if not xlsx_files:
            raise CommandError(f"No *.xlsx files found in '{data_dir}'.")

        subcommand = IMPORTER_SUBCOMMANDS[options["format"]]
        mxp = str(options["mxp"])
        for xlsx in xlsx_files:
            self.stdout.write(
                f"\n>>> etl {subcommand} -s {xlsx} -mp -mxp {mxp} --no-index"
            )
            call_command(
                "etl", subcommand, "-s", str(xlsx), "-mp", "-mxp", mxp, "--no-index"
            )

        self.stdout.write("\n>>> resources calculate_descriptors")
        call_command("resources", "calculate_descriptors", "-y")

        self.stdout.write(f"\n>>> arches_search reindex_database -mp -mxp {mxp}")
        call_command("arches_search", "reindex_database", "-mp", "-mxp", mxp)

        self.stdout.write(self.style.SUCCESS("\nDone."))
