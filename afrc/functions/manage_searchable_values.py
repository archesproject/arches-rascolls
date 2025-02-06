from django.db import connection

from arches.app.functions.base import BaseFunction

details = {
    "name": "Manage Searchable Values Function",
    "type": "node",
    "description": "Makes a tiles searchable values available for search",
    "defaultconfig": {"selected_nodegroup": ""},
    "classname": "ManageSearchableValues",
    "component": "views/components/functions/manage-searchable-values",
}


class ManageSearchableValues(BaseFunction):

    def get(self, *args, **kwargs):
        raise NotImplementedError

    def save(self, *args, **kwargs):
        raise NotImplementedError

    # occurrs after Tile.save
    def post_save(self, tile, request, context):
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM __afrc_update_searchable_values_for_tile(%s)",
                [tile.tileid],
            )

    def delete(self, tile, request):
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM afrc_searchable_values WHERE tileid = %s",
                [tile.tileid],
            )

    def on_import(self, *args, **kwargs):
        raise NotImplementedError

    # saves changes to the function itself
    def after_function_save(self, *args, **kwargs):
        raise NotImplementedError
