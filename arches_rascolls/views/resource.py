import uuid

from django.views import View
from django.shortcuts import redirect

from arches.app.models import models


class ModularReportAddResourceView(View):
    def get(self, request, graphid):
        resourceid = str(uuid.uuid4())
        models.ResourceInstance.objects.create(
            graph_id=graphid, resourceinstanceid=resourceid
        )
        return redirect("resource_report", resourceid=resourceid)


class ModularReportUpdateResourceView(View):
    def get(self, request, resourceid):
        return redirect("resource_report", resourceid=resourceid)
