from django.db import models

from wagtail.admin.panels import FieldPanel
from wagtail.models import Page
from wagtail.contrib.routable_page.models import RoutablePageMixin
from wagtail.fields import StreamField
from wagtail.images import get_image_model_string

from blocks.models import BaseStreamBlock


class HomePage(RoutablePageMixin, Page):
    image_file = models.ForeignKey(
        get_image_model_string(),  # allows custom Wagtail image model
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",  # no reverse relation needed
    )
    body = StreamField(
        BaseStreamBlock(features=["bold", "italic", ]),
        verbose_name="Page body",
        blank=True,
        use_json_field=True
    )
    content_panels = Page.content_panels + [FieldPanel("body"), FieldPanel("image_file"),]
