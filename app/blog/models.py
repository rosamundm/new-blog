from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin
from wagtail.fields import StreamField
from wagtail.models import Page
from wagtail.search import index

from blocks.index import BaseStreamBlock


class BlogPage(Page):
    introduction = models.TextField(help_text="Text to describe the page", blank=True)
    image_url = models.URLField(blank=True, null=True)
    body = StreamField(
        BaseStreamBlock(features=["bold", "italic", ]), verbose_name="Page body", blank=True, use_json_field=True
    )
    date_published = models.DateField("Date article published", blank=True, null=True)

    content_panels = Page.content_panels + [
        FieldPanel("introduction"),
        FieldPanel("image_url"),
        FieldPanel("body"),
        FieldPanel("date_published"),
    ]

    search_fields = Page.search_fields + [
        index.SearchField("body"),
    ]


class BlogIndexPage(RoutablePageMixin, Page):
    """
    Index page for blogs.
    We need to alter the page model's context to return the child page objects,
    the BlogPage objects, so that it works as an index page

    RoutablePageMixin is used to allow for a custom sub-URL for the tag views
    defined above.
    """

    introduction = models.TextField(help_text="Text to describe the page", blank=True)
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Landscape mode only; horizontal width between 1000px and 3000px.",
    )

    content_panels = Page.content_panels + [
        FieldPanel("introduction"),
        FieldPanel("image"),
    ]

    subpage_types = ["BlogPage"]

    @property
    def children(self):
        return self.get_children().specific().live()

    def get_context(self, request):
        context = super(BlogIndexPage, self).get_context(request)
        context["posts"] = (
            BlogPage.objects
            .descendant_of(self)
            .live()
            .order_by("-date_published")
        )
        return context

    def get_posts(self, tag=None):
        return BlogPage.objects.live().descendant_of(self)

    def serve_preview(self, request, mode_name):
        return self.serve(request)
