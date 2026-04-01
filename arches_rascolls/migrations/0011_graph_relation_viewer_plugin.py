import uuid

from django.db import migrations

PLUGIN_ID = uuid.UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567890")


class Migration(migrations.Migration):

    dependencies = [
        ("arches_rascolls", "0010_plugin_visibility"),
    ]

    forward_sql = f"""
        INSERT INTO public.plugins(
            pluginid, name, icon, component, componentname, config, slug, sortorder, helptemplate)
        VALUES (
            '{PLUGIN_ID}',
            '{{"en": "Graph Relation Viewer"}}',
            'fa fa-project-diagram',
            'views/components/plugins/graph-relation-viewer',
            'graph-relation-viewer',
            '{{"show": true}}',
            'graph-relation-viewer',
            2,
            ''
        );
    """

    reverse_sql = f"""
        DELETE FROM public.plugins WHERE pluginid = '{PLUGIN_ID}';
    """

    operations = [
        migrations.RunSQL(forward_sql, reverse_sql),
    ]
