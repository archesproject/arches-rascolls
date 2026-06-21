from django.views.generic import View

from arches.app.models.models import EditLog
from arches.app.utils.permission_backend import (
    user_can_read_resource,
    user_is_resource_reviewer,
)
from arches.app.utils.response import JSONResponse


class ResourceLastEditedAPI(View):
    def get(self, request, resourceid):
        if not user_can_read_resource(request.user, resourceid=str(resourceid)):
            return JSONResponse({"message": "Forbidden"}, status=403)

        last_edited = (
            EditLog.objects.filter(resourceinstanceid=str(resourceid))
            .order_by("-timestamp")
            .values_list("timestamp", flat=True)
            .first()
        )
        return JSONResponse(
            {
                "last_edited": last_edited,
                "user_is_reviewer": user_is_resource_reviewer(request.user),
            }
        )
