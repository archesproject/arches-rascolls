from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("arches_rascolls", "0009_remove_manage_searchable_values"),
    ]

    bulk_data_manager_id = "7720e9fa-876c-4127-a77a-b099cd2a5d45"
    old_search_plugin_id = "929e1b9b-a9dc-4603-ae0a-f129d89d8b66"

    def make_bdm_visible(apps, schema_editor):
        bdm = apps.get_model("models", "Plugin")
        bdm.objects.filter(pluginid=Migration.bulk_data_manager_id).update(
            config={
                "show": True,
                "description": {"en": None},
                "i18n_properties": ["description"],
            }
        )

    def hide_bdm(apps, schema_editor):
        bdm = apps.get_model("models", "Plugin")
        bdm.objects.filter(pluginid=Migration.bulk_data_manager_id).update(
            config={
                "show": False,
                "description": {"en": None},
                "i18n_properties": ["description"],
            }
        )

    def hide_old_search(apps, schema_editor):
        bdm = apps.get_model("models", "Plugin")
        bdm.objects.filter(pluginid=Migration.old_search_plugin_id).update(
            config={
                "show": False,
                "description": {"en": None},
                "i18n_properties": ["description"],
            }
        )

    def show_old_search(apps, schema_editor):
        bdm = apps.get_model("models", "Plugin")
        bdm.objects.filter(pluginid=Migration.old_search_plugin_id).update(
            config={
                "show": True,
                "description": {"en": None},
                "i18n_properties": ["description"],
            }
        )

    operations = [
        migrations.RunPython(make_bdm_visible, hide_bdm),
        migrations.RunPython(hide_old_search, show_old_search),
    ]
