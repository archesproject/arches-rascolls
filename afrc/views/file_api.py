from arches.app.utils.response import JSONResponse
from arches.app.models.models import TileModel, ResourceXResource
from django.views.generic import View
from django.db.models.fields.json import KT


class FileAPI(View):
    def get(self, request):
        file_node_id = "8713d9ca-d860-11ef-98f5-0275dc2ded29"
        digital_resource_graph_id = "8713965e-d860-11ef-98f5-0275dc2ded29"
        resource_ids = request.GET.get("resourceids")
        is_item = request.GET.get("item", None)
        if is_item:
            digital_resource = ResourceXResource.objects.filter(resourceinstanceidfrom_id=resource_ids).filter(resourceinstanceto_graphid_id=digital_resource_graph_id)
            resource_ids = digital_resource.values_list('resourceinstanceidto_id', flat=True)
            resource_ids = [str(id) for id in resource_ids]
        else:
            resource_ids = resource_ids.split(",")

        res = TileModel.objects.filter(resourceinstance_id__in=resource_ids).filter(data__has_key=file_node_id).values('data')
        paths = []

        for tile in res:
            paths += [val['url'] for val in tile['data'][file_node_id]]

        return JSONResponse(
            paths,
        )
