from arches.app.utils.response import JSONResponse
from arches.app.models.models import File, TileModel
from django.views.generic import View
from django.db.models.fields.json import KT


class FileAPI(View):
    def get(self, request):
        file_node_id = file_node_id
        resource_ids = request.GET.get("resourceids")
        if resource_ids:
            resource_ids = resource_ids.split(",")
        res = TileModel.objects.filter(resourceinstance_id__in=resource_ids).filter(data__has_key=file_node_id).values('data')
        paths = []
        for tile in res:
            paths += [val['url'] for val in tile['data'][file_node_id]]

        return JSONResponse(
            paths,
        )
