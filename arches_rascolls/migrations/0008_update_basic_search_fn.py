from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("arches_rascolls", "0007_load_controlled_lists"),
    ]

    update_table_name = """
        CREATE OR REPLACE FUNCTION __arches_rascolls_get_related_resources_by_searchable_values(
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
                FROM arches_search_terms sv
                JOIN resource_instances r ON r.resourceinstanceid = sv.resourceinstanceid
                WHERE to_tsquery(term) @@ sv.search_vector
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

    reverse_table_name = """
            CREATE OR REPLACE FUNCTION __arches_rascolls_get_related_resources_by_searchable_values(
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
                    FROM arches_rascolls_searchable_values sv
                    JOIN resource_instances r ON r.resourceinstanceid = sv.resourceinstanceid
                    WHERE to_tsquery(term) @@ sv.search_vector
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

    operations = [
        migrations.RunSQL(
            update_table_name,
            reverse_table_name,
        ),
    ]
