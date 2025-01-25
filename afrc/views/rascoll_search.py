from django.shortcuts import render
from arches.app.views.base import BaseManagerView
from django.utils.translation import gettext_lazy as _

class RascollSearchView(BaseManagerView):
    def get(self, request, graphid=None, resourceid=None):
        context = self.get_context_data(main_script="views/rascoll-search")
        context['page_title'] = _("RASCOLL Search")
        return render(request, "views/rascoll-search.htm", context)