from django.views.generic import View

from arches.app.utils.response import JSONResponse

from arches_rascolls.models import FeaturedSearchItem


class FeaturedItemsAPI(View):
    def get(self, request):
        items = FeaturedSearchItem.objects.filter(is_active=True).select_related(
            "saved_search"
        )
        return JSONResponse(
            {
                "results": [
                    {
                        "id": str(item.featuredsearchitemid),
                        "label": item.display_label,
                        "description": item.display_description,
                        "icon": item.presentation.get("icon"),
                        "color": item.presentation.get("color"),
                        "search_definition": item.saved_search.query_definition,
                    }
                    for item in items
                ]
            }
        )
