from django.db import migrations
from arches.app.models.system_settings import settings


class Migration(migrations.Migration):

    dependencies = [
        ("afrc", "0004_search_layer"),
    ]

    def add_function_to_graphs(apps, schema_editor):
        GraphModel = apps.get_model("models", "GraphModel")
        FunctionXGraph = apps.get_model("models", "FunctionXGraph")
        Function = apps.get_model("models", "Function")
        resource_models = GraphModel.objects.filter(isresource=True).exclude(
            graphid=settings.SYSTEM_SETTINGS_RESOURCE_ID
        )
        function = Function.objects.get(
            functionid="c75ebc8d-7aae-4c99-981d-4219dbb4b789"
        )
        config = function.defaultconfig
        for resource_model in resource_models:
            function_x_graph = FunctionXGraph(
                graph_id=resource_model.graphid,
                function_id=function.functionid,
                config=config,
            )
            function_x_graph.save()

    def remove_function_from_graphs(apps, schema_editor):
        GraphModel = apps.get_model("models", "GraphModel")
        resource_models = GraphModel.objects.filter(isresource=True).exclude(
            graphid=settings.SYSTEM_SETTINGS_RESOURCE_ID
        )
        for resource_model in resource_models:
            resource_model.functions.remove("c75ebc8d-7aae-4c99-981d-4219dbb4b789")
            resource_model.save()

    operations = [
        migrations.RunSQL(
            """
            UPDATE functions
            SET defaultconfig =
                concat('{"triggering_nodegroups": ["', (
                select string_agg(distinct nodegroupid::text, '","') from nodes 
                where datatype in ('string','non-localized-string','concept', 'concept-list') 
                and graphid != '1d0ac51c-131a-11f0-bf26-469c1cc4c080'
            ), '"]}')::jsonb
            WHERE functionid = 'c75ebc8d-7aae-4c99-981d-4219dbb4b789';
            """,
            """update functions set defaultconfig = '{}' where functionid = 'c75ebc8d-7aae-4c99-981d-4219dbb4b789';""",
        ),
        migrations.RunPython(add_function_to_graphs, remove_function_from_graphs),
    ]
