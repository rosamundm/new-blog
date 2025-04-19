from wagtail.models import Page
from wagtail.contrib.routable_page.models import RoutablePageMixin
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel
from blocks.index import BaseStreamBlock


class HomePage(RoutablePageMixin, Page):
    body = StreamField(
        BaseStreamBlock(features=["bold", "italic", ]),
        verbose_name="Page body",
        blank=True,
        use_json_field=True
    )
    content_panels = Page.content_panels + [FieldPanel("body"), ]
