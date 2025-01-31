from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("afrc", "0002_plugin"),
    ]

    forward_sql = """
        CREATE OR REPLACE FUNCTION __arches_get_searchable_values_for_resourceinstances(resourceinstance UUID[])
        RETURNS TABLE(value text) AS $$
        BEGIN
            RETURN QUERY
            SELECT distinct
                CASE 
                    WHEN n.datatype = 'string' THEN data.value::jsonb->'en'->>'value'
                    WHEN n.datatype = 'concept' THEN __arches_get_concept_label(data.value::uuid)
                    WHEN n.datatype = 'concept-list' THEN __arches_get_concept_list_label(data.value::jsonb, 'en')
                END AS value
            FROM 
                tiles t
            CROSS JOIN LATERAL jsonb_each_text(t.tiledata) AS data(nodeid, value) -- Extract key-value pairs from tiledata
            JOIN 
                nodes n ON data.nodeid::uuid = n.nodeid
            WHERE 
                t.resourceinstanceid = ANY(resourceinstance)
                AND n.datatype IN ('string', 'concept', 'concept-list')
                AND (
                    (n.datatype = 'string' AND data.value::jsonb->'en'->>'value' IS NOT NULL) OR
                    (n.datatype IN ('concept', 'concept-list') AND data.value IS NOT NULL)
                );
        END;
        $$ LANGUAGE plpgsql;
    """
    reverse_sql = """
        DROP FUNCTION IF EXISTS __arches_get_searchable_values_for_resourceinstances(UUID[]);
    """

    operations = [
        migrations.RunSQL(forward_sql, reverse_sql),
    ]
