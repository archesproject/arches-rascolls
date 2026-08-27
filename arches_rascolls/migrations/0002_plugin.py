from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("arches_rascolls", "0001_initial"),
    ]

    reverse_sql = """
        DELETE FROM public.plugins WHERE pluginid = '929e1b9b-a9dc-4603-ae0a-f129d89d8b66';
    """

    operations = [
        migrations.RunSQL(migrations.RunSQL.noop, reverse_sql),
    ]
