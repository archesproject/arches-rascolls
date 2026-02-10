from django.db import migrations
from arches.app.models.system_settings import settings
from django.core.exceptions import ObjectDoesNotExist


class Migration(migrations.Migration):

    dependencies = [
        ("arches_rascolls", "0008_update_basic_search_fn"),
    ]

    reverse_create_searchable_values_table = """
        DROP TABLE IF EXISTS public.arches_rascolls_searchable_values;
    """

    reverse_create_function_to_update_searchable_values = """
        DROP FUNCTION IF EXISTS __arches_rascolls_update_searchable_values_for_tile(UUID);
    """

    reverse_create_function_to_do_through_search = """
        DROP FUNCTION IF EXISTS __arches_rascolls_get_related_resources_by_searchable_values(TEXT[], UUID);
    """

    def remove_function_from_graphs(apps, schema_editor):
        GraphModel = apps.get_model("models", "GraphModel")
        Function = apps.get_model("models", "Function")
        try:
            fn = Function.objects.get(classname="ManageSearchableValues")
        except ObjectDoesNotExist:
            return
        resource_models = GraphModel.objects.filter(isresource=True).exclude(
            graphid=settings.SYSTEM_SETTINGS_RESOURCE_ID
        )
        for resource_model in resource_models:
            resource_model.functions.remove(fn)
            resource_model.save()
        fn.delete()

    operations = [
        migrations.RunSQL(
            reverse_create_searchable_values_table,
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            reverse_create_function_to_update_searchable_values,
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            reverse_create_function_to_do_through_search,
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunPython(
            remove_function_from_graphs, reverse_code=migrations.RunPython.noop
        ),
    ]
