import uuid

from django.db import models


class FeaturedSearchItem(models.Model):
    featuredsearchitemid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    saved_search = models.ForeignKey(
        "arches_search.SavedSearch",
        on_delete=models.CASCADE,
        related_name="featured_items",
        limit_choices_to={"creator__is_staff": True},
    )
    presentation = models.JSONField(default=dict)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = "arches_rascolls_featured_search_items"
        ordering = ["sort_order", "featuredsearchitemid"]

    @property
    def display_label(self):
        return self.presentation.get("label") or self.saved_search.name

    @property
    def display_description(self):
        return self.presentation.get("description") or self.saved_search.description
