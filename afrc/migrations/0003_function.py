from django.db import migrations


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
            target_graphid UUID -- Graph ID to filter results
        )
        RETURNS TABLE(resourceinstance UUID) AS $$
        DECLARE
            initial_ids UUID[];
            second_level_ids UUID[];
        BEGIN
            -- Step 1: Retrieve initial resourceinstanceid values based on the text search
            
            -- Should probably return resourceinstances that match our target graph here as well
            -- as those are direct hits of search values

            SELECT ARRAY(
                SELECT resourceinstanceid
                FROM afrc_searchable_values sv
                JOIN LATERAL (
                    SELECT term FROM unnest(search_terms) term 
                    WHERE sv.value ILIKE '%' || term || '%'
                ) matched_terms ON true
                GROUP BY sv.resourceinstanceid
                HAVING COUNT(DISTINCT matched_terms.term) = array_length(search_terms, 1)
            ) INTO initial_ids;

            -- If no matches found, return empty result
            IF initial_ids IS NULL OR array_length(initial_ids, 1) = 0 THEN
                RETURN;
            END IF;

            -- Step 2: Create a temporary table to store categorized first-level results
            CREATE TEMP TABLE temp_related_resources (
                resourceinstanceid UUID,
                graphid UUID,
                is_matching BOOLEAN -- TRUE if it matches the target_graphid
            ) ON COMMIT DROP;

            -- Insert first-level relationships into the temp table with categorization
            INSERT INTO temp_related_resources (resourceinstanceid, graphid, is_matching)
            SELECT DISTINCT 
                r.resourceinstanceidfrom AS resourceinstanceid,
                r.resourceinstancefrom_graphid AS graphid,
                r.resourceinstancefrom_graphid = target_graphid AS is_matching
            FROM resource_x_resource r
            WHERE r.resourceinstanceidto = ANY(initial_ids)
            
            UNION

            SELECT DISTINCT 
                r.resourceinstanceidto AS resourceinstanceid,
                r.resourceinstanceto_graphid AS graphid,
                r.resourceinstanceto_graphid = target_graphid AS is_matching
            FROM resource_x_resource r
            WHERE r.resourceinstanceidfrom = ANY(initial_ids);

            -- Step 2.5: Return matching results immediately
            RETURN QUERY 
            SELECT resourceinstanceid FROM temp_related_resources WHERE is_matching = TRUE;

            -- Step 3: Find second-level related resourceinstanceids using only non-matching first-level IDs
            RETURN QUERY
            SELECT DISTINCT r.resourceinstanceidfrom 
            FROM resource_x_resource r
            WHERE r.resourceinstanceidto IN (
                SELECT resourceinstanceid FROM temp_related_resources WHERE is_matching = FALSE
            )
            AND r.resourceinstancefrom_graphid = target_graphid
            
            UNION
            
            SELECT DISTINCT r.resourceinstanceidto
            FROM resource_x_resource r
            WHERE r.resourceinstanceidfrom IN (
                SELECT resourceinstanceid FROM temp_related_resources WHERE is_matching = FALSE
            )
            AND r.resourceinstanceto_graphid = target_graphid;

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
    ]
