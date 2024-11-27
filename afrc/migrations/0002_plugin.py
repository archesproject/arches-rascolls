from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("afrc", "0001_initial"),
    ]

    forward_sql = """
        INSERT INTO public.plugins(
            pluginid, name, icon, component, componentname, config, slug, sortorder, helptemplate)
            VALUES ('929e1b9b-a9dc-4603-ae0a-f129d89d8b66', 
            '{"en": "Search Reference Collections"}', 
            'fa fa-search', 
            'views/components/plugins/afrc-search-plugin', 
            'afrc-search-plugin', 
            '{"show": true, "description": {"en": null}, "i18n_properties": ["description"]}', 
            'afrc-search', 
            1, 
            ''
        );
    """
    reverse_sql = """
        DELETE FROM public.plugins WHERE pluginid = '929e1b9b-a9dc-4603-ae0a-f129d89d8b66';
    """

    operations = [
        migrations.RunSQL(forward_sql, reverse_sql),
    ]
