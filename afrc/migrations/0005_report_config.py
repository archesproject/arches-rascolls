import uuid
import os
import glob
from django.db import migrations
from pathlib import Path
from django.utils.translation import gettext as _
import json
from arches.app.models.system_settings import settings

config_to_graph_slug_mappings = {
    "reference_and_sample_collection_item": "reference_and_sample_collection_item_1",
}


class Migration(migrations.Migration):

    dependencies = [
        ("afrc", "0004_search_layer"),
        ("arches_modular_reports", "0002_add_modular_report"),
    ]

    def update_report_configs(apps, schema_editor):
        ReportConfig = apps.get_model("arches_modular_reports", "ReportConfig")
        Graph = apps.get_model("models", "GraphModel")
        ReportTemplate = apps.get_model("models", "ReportTemplate")
        editable_report_template = ReportTemplate.objects.get(
            name="Modular Report Template"
        )

        reports_dir = os.path.join(settings.APP_ROOT, "report_configs/**")
        config_dirs = glob.glob(reports_dir)
        for config_dir in config_dirs:
            for file in glob.glob(os.path.join(config_dir, "*.json")):
                with open(file) as f:
                    data = json.load(f)
                    graph_slug = config_to_graph_slug_mappings.get(
                        Path(config_dir).stem, None
                    )
                    if graph_slug:
                        try:
                            graph = Graph.objects.get(slug=graph_slug)
                            graph.template = editable_report_template
                            graph.save()
                            config = ReportConfig.objects.create(
                                graph=graph, config=data
                            )
                            config.clean()
                        except Graph.DoesNotExist:
                            message = (
                                f'\n\n     Graph with slug "{graph_slug}" not found. The report config found at '
                                f"\n     {config_dir} was skipped."
                                f"\n     Either update the graph slug reference in this migration or update the graph slug itself."
                            )
                            print(message)

    def revert_report_configs(apps, schema_editor):
        ReportConfig = apps.get_model("arches_modular_reports", "ReportConfig")
        Graph = apps.get_model("models", "GraphModel")
        ReportTemplate = apps.get_model("models", "ReportTemplate")
        basic_report_template = ReportTemplate.objects.get(name="No Header Template")

        reports_dir = os.path.join(settings.APP_ROOT, "report_configs/**")
        config_dirs = glob.glob(reports_dir)
        for config_dir in config_dirs:
            print("CONFIG_DIR", config_dir)
            graph_slug = config_to_graph_slug_mappings.get(Path(config_dir).stem, None)
            print("SLUG", graph_slug)
            if graph_slug:
                graph = Graph.objects.get(slug=graph_slug)
                graph.template = basic_report_template
                graph.save()
                ReportConfig.objects.filter(graph=graph).delete()

    operations = [
        migrations.RunPython(update_report_configs, revert_report_configs),
    ]
