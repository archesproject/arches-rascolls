from pathlib import Path

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count, Min
from django.utils import timezone

from arches.app.models.models import LoadErrors, LoadEvent

SOURCE_FILE_PATTERNS = ("*.xlsx", "*.zip")

MAX_REPORTED_ERRORS = 20

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

        self.stdout.write("\n>>> filter_configs load")
        call_command("filter_configs", "load")

        source_files = sorted(
            path for pattern in SOURCE_FILE_PATTERNS for path in data_dir.glob(pattern)
        )
        if not source_files:
            patterns = ", ".join(SOURCE_FILE_PATTERNS)
            raise CommandError(f"No {patterns} files found in '{data_dir}'.")

        subcommand = IMPORTER_SUBCOMMANDS[options["format"]]
        failed_files = []
        for source_file in source_files:
            self.stdout.write(f"\n>>> etl {subcommand} -s {source_file} -mp --no-index")
            started = timezone.now()
            call_command("etl", subcommand, "-s", str(source_file), "-mp", "--no-index")
            # etl does not raise when a load fails validation, so check the load event.
            if not self.load_succeeded(subcommand, started):
                failed_files.append(source_file.name)

        self.stdout.write("\n>>> resources calculate_descriptors")
        call_command("resources", "calculate_descriptors", "-y")

        self.stdout.write("\n>>> arches_search reindex_database -mp")
        call_command("arches_search", "reindex_database", "-mp")

        if failed_files:
            raise CommandError(f"Failed to load: {', '.join(failed_files)}")

        self.stdout.write(self.style.SUCCESS("\nDone."))

    def load_succeeded(self, subcommand, started):
        load_event = (
            LoadEvent.objects.filter(
                etl_module__componentname=subcommand, load_start_time__gte=started
            )
            .order_by("-load_start_time")
            .first()
        )
        if load_event is None:
            self.stderr.write("No load event was recorded.")
            return False
        if load_event.successful:
            return True

        self.stderr.write(
            self.style.ERROR(
                f"Load {load_event.loadid} did not complete (status: {load_event.status}). "
                f"{load_event.error_message or ''}"
            )
        )
        errors = (
            LoadErrors.objects.filter(load_event=load_event)
            .values("error", "node__name", "message")
            .annotate(count=Count("*"), example_value=Min("value"))
            .order_by("-count")
        )
        for error in errors[:MAX_REPORTED_ERRORS]:
            self.stderr.write(
                f"  {error['count']} x {error['error']} ({error['node__name']}): "
                f"{error['message'] or ''} e.g. {error['example_value']!r}"
            )
        remaining = errors.count() - MAX_REPORTED_ERRORS
        if remaining > 0:
            self.stderr.write(f"  ...and {remaining} more error type(s).")
        return False
