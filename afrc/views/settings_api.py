from django.views.generic import View
from django.utils.translation import get_language, get_language_bidi

from arches.app.utils.response import JSONResponse
from arches.app.models.system_settings import settings


class SettingsAPI(View):
    def get(self, request):
        return JSONResponse(
            {
                "ACTIVE_LANGUAGE": get_language(),
                "ACTIVE_LANGUAGE_DIRECTION": "rtl" if get_language_bidi() else "ltr",
                "DEFAULT_BOUNDS": settings.DEFAULT_BOUNDS,
            }
        )
