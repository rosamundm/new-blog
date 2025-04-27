from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin
from wagtail.fields import StreamField
from wagtail.models import Page

from blocks.models import BaseStreamBlock


class ProjectPage(Page):
    introduction = models.TextField(blank=True)
    image_url = models.URLField(blank=True, null=True)
    link_to_project = models.URLField(blank=True, null=True)
    body = StreamField(
        BaseStreamBlock(features=["bold", "italic", ]),
        verbose_name="Page body",
        blank=True,
        use_json_field=True
    )

    content_panels = Page.content_panels + [
        FieldPanel("introduction"),
        FieldPanel("image_url"),
        FieldPanel("link_to_project"),
        FieldPanel("body"),
    ]


class ProjectIndexPage(RoutablePageMixin, Page):
    subpage_types = ["ProjectPage"]

    @property
    def children(self):
        return self.get_children().specific().live()

    def get_context(self, request):
        context = super(ProjectIndexPage, self).get_context(request)
        context["projects"] = (
            ProjectPage.objects.descendant_of(self).live().order_by("-title")
        )
        return context

    def serve_preview(self, request, mode_name):
        return self.serve(request)

    def get_projects(self, tag=None):
        return ProjectPage.objects.live().descendant_of(self)
