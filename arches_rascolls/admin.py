import re

from django import forms
from django.contrib import admin
from django.db import models
from django.forms import Textarea

from arches_rascolls.models import FeaturedSearchItem


class FeaturedSearchItemForm(forms.ModelForm):
    class Meta:
        model = FeaturedSearchItem
        fields = "__all__"
        exclude = ["featuredsearchitemid", "created_at"]

    def clean_presentation(self):
        data = self.cleaned_data["presentation"]
        if not isinstance(data, dict):
            raise forms.ValidationError(
                "presentation must be a JSON object, e.g. {'icon': 'pi-palette', 'color': '#0d9488'}"
            )
        if not re.fullmatch(r"pi-[a-z0-9-]+", data.get("icon", "")):
            raise forms.ValidationError(
                "icon must be a bare PrimeIcon suffix, e.g. 'pi-palette'"
            )
        if not re.fullmatch(r"#[0-9a-fA-F]{6}", data.get("color", "")):
            raise forms.ValidationError("color must be a #rrggbb hex value")
        return data

    def clean(self):
        cleaned = super().clean()
        query_definition = (
            cleaned.get("saved_search") and cleaned["saved_search"].query_definition
        )
        if query_definition is not None and not (
            {"terms", "groups"} & query_definition.keys()
        ):
            raise forms.ValidationError(
                "linked saved search has no terms/groups — it isn't a runnable dynamic query"
            )
        return cleaned


@admin.register(FeaturedSearchItem)
class FeaturedSearchItemAdmin(admin.ModelAdmin):
    form = FeaturedSearchItemForm
    list_display = ["display_label", "saved_search", "sort_order", "is_active"]
    list_editable = ["sort_order", "is_active"]
    autocomplete_fields = ["saved_search"]
    readonly_fields = ["featuredsearchitemid", "created_at"]
    formfield_overrides = {
        models.JSONField: {"widget": Textarea(attrs={"rows": 20, "cols": 80})},
    }
