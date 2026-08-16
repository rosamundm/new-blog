from django.db import models

from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.contrib.routable_page.models import RoutablePageMixin
from wagtail.fields import StreamField
from wagtail.images import get_image_model_string
from wagtail.models import Page
from wagtail.search import index

from blocks.models import BaseStreamBlock


class BlogPage(Page):
    introduction = models.TextField(blank=True)
    image_url = models.URLField(blank=True, null=True)
    image_file = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    body = StreamField(
        BaseStreamBlock(features=["bold", "italic", "footnotes, "]),
        verbose_name="Page body",
        blank=True,
        use_json_field=True
    )
    date_published = models.DateField(
        "Date article published",
        blank=True,
        null=True
    )
    content_panels = Page.content_panels + [
        FieldPanel("introduction"),
        FieldPanel("image_url"),
        FieldPanel("body"),
        FieldPanel("date_published"),
        InlinePanel("footnotes", label="Footnotes"),
    ]

    search_fields = Page.search_fields + [
        index.SearchField("body"),
    ]

    def get_next_post(self):
        # guard for posts still in the draft stage
        if not self.first_published_at:
            return None
        return (
            BlogPage.objects.live().public()
            .sibling_of(self)
            .filter(first_published_at__gt=self.first_published_at)
            .order_by("first_published_at")
            .first()
        )

    def get_previous_post(self):
        if not self.first_published_at:
            return None
        return (
            BlogPage.objects.live().public()
            .sibling_of(self)
            .filter(first_published_at__lt=self.first_published_at)
            .order_by("-first_published_at")
            .first()
        )


class BlogIndexPage(RoutablePageMixin, Page):
    """
    Index page for blog posts.

    Alters the page model's context to return the child page objects
    so that it works as an index page.
    """

    introduction = models.TextField(
        help_text="Text to describe the page",
        blank=True)
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Landscape mode only; horizontal width between 1000-3000px.",
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
