from django.db import migrations
from arches.app.models.system_settings import settings


class Migration(migrations.Migration):

    dependencies = [
        ("afrc", "0002_plugin"),
    ]

    create_searchable_values_table = """
        CREATE SEQUENCE IF NOT EXISTS public."afrc_searchable_values_id_seq"
            INCREMENT 1
            START 1
            MINVALUE 1
            MAXVALUE 2147483647
            CACHE 1;

        CREATE TABLE IF NOT EXISTS public.afrc_searchable_values
        (
            id bigint NOT NULL DEFAULT nextval('afrc_searchable_values_id_seq'::regclass),
            tileid uuid,
            resourceinstanceid uuid,
            value text COLLATE pg_catalog."default",
            CONSTRAINT searchable_values_pkey PRIMARY KEY (id)
        )

        TABLESPACE pg_default;

        ALTER SEQUENCE public."afrc_searchable_values_id_seq"
            OWNED BY public."afrc_searchable_values".id;

        ALTER SEQUENCE public."afrc_searchable_values_id_seq"
            OWNER TO postgres;

        ALTER TABLE IF EXISTS public.afrc_searchable_values
            OWNER to postgres;
    """

    reverse_create_searchable_values_table = """
        DROP TABLE IF EXISTS public.afrc_searchable_values;
    """

    populate_searchable_values_table = """
        INSERT INTO afrc_searchable_values (tileid, resourceinstanceid, value)
        SELECT DISTINCT
            t.tileid,
            t.resourceinstanceid,
            CASE 
                WHEN n.datatype = 'string' THEN data.value::jsonb->'en'->>'value'
                WHEN n.datatype = 'concept' THEN __arches_get_concept_label(data.value::uuid)
                WHEN n.datatype = 'concept-list' THEN __arches_get_concept_list_label(data.value::jsonb, 'en')
            END AS value
        FROM 
            tiles t
        CROSS JOIN LATERAL jsonb_each_text(t.tiledata) AS data(nodeid, value) 
        JOIN 
            nodes n ON data.nodeid::uuid = n.nodeid
        WHERE 
            n.datatype IN ('string', 'concept', 'concept-list')
            AND (
                (n.datatype = 'string' AND data.value::jsonb->'en'->>'value' IS NOT NULL) OR
                (n.datatype IN ('concept', 'concept-list') AND data.value IS NOT NULL)
            );
    """

    reverse_populate_searchable_values_table = """
        DELETE FROM afrc_searchable_values;
    """

    create_function_to_update_searchable_values = """
        CREATE OR REPLACE FUNCTION __afrc_update_searchable_values_for_tile(_tileid UUID)
        RETURNS VOID AS $$
        BEGIN
            DELETE FROM afrc_searchable_values WHERE afrc_searchable_values.tileid = _tileid;
            INSERT INTO afrc_searchable_values (tileid, resourceinstanceid, value)
            SELECT DISTINCT
                t.tileid,
                t.resourceinstanceid,
                CASE 
                    WHEN n.datatype = 'string' THEN data.value::jsonb->'en'->>'value'
                    WHEN n.datatype = 'concept' THEN __arches_get_concept_label(data.value::uuid)
                    WHEN n.datatype = 'concept-list' THEN __arches_get_concept_list_label(data.value::jsonb, 'en')
                END AS value
            FROM 
                tiles t
            CROSS JOIN LATERAL jsonb_each_text(t.tiledata) AS data(nodeid, value) 
            JOIN 
                nodes n ON data.nodeid::uuid = n.nodeid
            WHERE 
                n.datatype IN ('string', 'concept', 'concept-list')
                AND (
                    (n.datatype = 'string' AND data.value::jsonb->'en'->>'value' IS NOT NULL) OR
                    (n.datatype IN ('concept', 'concept-list') AND data.value IS NOT NULL)
                )
                AND t.tileid = _tileid;
        END; 

        $$ LANGUAGE plpgsql;
    """

    reverse_create_function_to_update_searchable_values = """
        DROP FUNCTION IF EXISTS __afrc_update_searchable_values_for_tile(UUID);
    """

    create_function_to_do_through_search = """
        CREATE OR REPLACE FUNCTION __afrc_get_related_resources_by_searchable_values(
            search_terms TEXT[],
            target_graphid UUID
        )
        RETURNS TABLE(resourceinstance UUID) AS $$
        DECLARE
            term TEXT;
        BEGIN
            -- Create a temporary table to store intersection results
            CREATE TEMP TABLE temp_final_results (
                resourceinstanceid UUID PRIMARY KEY
            ) ON COMMIT DROP;

            -- Process each search term separately
            FOR term IN SELECT unnest(search_terms) LOOP
                -- Create a temporary table for this search term's results
                
                CREATE TEMP TABLE temp_related_resources (
                    resourceinstanceid UUID PRIMARY KEY,
                    graphid UUID,
                    is_matching BOOLEAN
                ) ON COMMIT DROP;

                -- Retrieve initial resourceinstanceid values based on the text search
                INSERT INTO temp_related_resources (resourceinstanceid, graphid, is_matching)
                SELECT sv.resourceinstanceid, r.graphid, r.graphid = target_graphid AS is_matching
                FROM afrc_searchable_values sv
                JOIN resource_instances r ON r.resourceinstanceid = sv.resourceinstanceid
                WHERE sv.value ILIKE '%' || term || '%'
                ON CONFLICT (resourceinstanceid) DO NOTHING;

                WITH first_level AS (
                    SELECT DISTINCT r.resourceinstanceidfrom AS resourceinstanceid, 
                        r.resourceinstancefrom_graphid AS graphid,
                        r.resourceinstancefrom_graphid = target_graphid AS is_matching
                    FROM resource_x_resource r
                    JOIN temp_related_resources tr ON r.resourceinstanceidto = tr.resourceinstanceid
                    WHERE tr.is_matching = FALSE
                
                    UNION
                
                    SELECT DISTINCT r.resourceinstanceidto as resourceinstanceid, 
                        r.resourceinstanceto_graphid AS graphid,
                        r.resourceinstanceto_graphid = target_graphid AS is_matching
                    FROM resource_x_resource r
                    JOIN temp_related_resources tr ON r.resourceinstanceidfrom = tr.resourceinstanceid
                    WHERE tr.is_matching = FALSE
                ),
                second_level AS (
                    SELECT DISTINCT r.resourceinstanceidfrom AS resourceinstanceid, 
                        r.resourceinstancefrom_graphid AS graphid
                    FROM resource_x_resource r
                    JOIN first_level fl ON r.resourceinstanceidto = fl.resourceinstanceid
                    WHERE fl.is_matching = FALSE
                
                    UNION
                
                    SELECT DISTINCT r.resourceinstanceidto AS resourceinstanceid, 
                        r.resourceinstanceto_graphid AS graphid
                    FROM resource_x_resource r
                    JOIN first_level fl ON r.resourceinstanceidfrom = fl.resourceinstanceid
                    WHERE fl.is_matching = FALSE

                    UNION 
                    -- Make sure we gather the first level results here too so that we can add those matches later
                    SELECT resourceinstanceid, graphid
                    FROM first_level fl
                )		
                INSERT INTO temp_related_resources
                SELECT resourceinstanceid, target_graphid, TRUE 
                FROM second_level
                WHERE graphid = target_graphid
                ON CONFLICT (resourceinstanceid) DO NOTHING;

                -- Intersect results across search terms
                IF term = search_terms[1] THEN
                    INSERT INTO temp_final_results 
                    SELECT DISTINCT resourceinstanceid FROM temp_related_resources WHERE is_matching = TRUE;
                ELSE
                    CREATE TEMP TABLE temp_intersection AS
                    SELECT resourceinstanceid FROM temp_final_results
                    INTERSECT
                    SELECT resourceinstanceid FROM temp_related_resources WHERE is_matching = TRUE;
                    
                    -- Replace the old table with the new one
                    TRUNCATE temp_final_results;
                    INSERT INTO temp_final_results SELECT * FROM temp_intersection;
                    DROP TABLE temp_intersection;
                END IF;

                -- Drop temporary table for this term
                DROP TABLE temp_related_resources;
            END LOOP;

            -- Return final intersected results
            RETURN QUERY SELECT resourceinstanceid FROM temp_final_results;
        END;
        $$ LANGUAGE plpgsql;

    """

    reverse_create_function_to_do_through_search = """
        DROP FUNCTION IF EXISTS __afrc_get_related_resources_by_searchable_values(TEXT[], UUID);
    """

    register_searchable_values_function = """
        INSERT INTO public.functions(
            functionid, 
            functiontype, 
            name, 
            description, 
            defaultconfig, 
            modulename, 
            classname, 
            component
        )
        VALUES (
            'c75ebc8d-7aae-4c99-981d-4219dbb4b789', 
            'search', 
            'Manage Searchable Values Function', 
            'Makes a tiles searchable values available for search', 
            '{}', 
            'manage_searchable_values.py', 
            'ManageSearchableValues', 
            'views/components/functions/manage-searchable-values'
        );
    """

    reverse_register_searchable_values_function = """
        DELETE FROM public.functions WHERE functionid = 'c75ebc8d-7aae-4c99-981d-4219dbb4b789';
    """


    configure_searchable_values_function = """
        UPDATE functions
        SET defaultconfig =
            concat('{"triggering_nodegroups": ["', (
            select string_agg(distinct nodegroupid::text, '","') from nodes 
            where datatype in ('string','non-localized-string','concept', 'concept-list') 
            and graphid != '1d0ac51c-131a-11f0-bf26-469c1cc4c080'
        ), '"]}')::jsonb
        WHERE functionid = 'c75ebc8d-7aae-4c99-981d-4219dbb4b789';
    """
    
    reverse_configure_searchable_values_function = """
        update functions set defaultconfig = '{}' where functionid = 'c75ebc8d-7aae-4c99-981d-4219dbb4b789';
    """

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
        Function = apps.get_model("models", "Function")
        fn = Function.objects.get(
            functionid="c75ebc8d-7aae-4c99-981d-4219dbb4b789"
        )
        resource_models = GraphModel.objects.filter(isresource=True).exclude(
            graphid=settings.SYSTEM_SETTINGS_RESOURCE_ID
        )
        for resource_model in resource_models:
            resource_model.functions.remove(fn)
            resource_model.save()


    operations = [
        migrations.RunSQL(
            create_searchable_values_table, reverse_create_searchable_values_table
        ),
        migrations.RunSQL(
            populate_searchable_values_table, reverse_populate_searchable_values_table
        ),
        migrations.RunSQL(
            create_function_to_update_searchable_values,
            reverse_create_function_to_update_searchable_values,
        ),
        migrations.RunSQL(
            create_function_to_do_through_search,
            reverse_create_function_to_do_through_search,
        ),
        migrations.RunSQL(
            register_searchable_values_function,
            reverse_register_searchable_values_function,
        ),
        migrations.RunSQL(
            configure_searchable_values_function,
            reverse_configure_searchable_values_function,
        ),
        migrations.RunPython(add_function_to_graphs, remove_function_from_graphs),
    ]
