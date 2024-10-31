from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.decorators.csrf import ensure_csrf_cookie

from arches.app.views.base import BaseManagerView


class Search(BaseManagerView):
    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        context = self.get_context_data(main_script="views/search")
        context["page_title"] = _("Search")
        return render(request, "views/search.htm", context)
