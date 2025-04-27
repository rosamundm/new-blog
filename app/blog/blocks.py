from django.utils.functional import cached_property
from wagtail.blocks import (
    CharBlock,
    ChoiceBlock,
    RichTextBlock,
    StreamBlock,
    StructBlock,
    URLBlock
)
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images import get_image_model


class CaptionedImageBlock(StructBlock):
    image_url = URLBlock(required=False)
    caption = CharBlock(required=False)
    attribution = CharBlock(required=False)

    @cached_property
    def preview_image(self):
        # Cache the image object for previews to avoid repeated queries
        return get_image_model().objects.last()

    def get_preview_value(self):
        return {
            **self.meta.preview_value,
            "image": self.preview_image,
            "caption": self.preview_image.description,
        }

    class Meta:
        icon = "image"
        template = "blocks/captioned_image_block.html"
        description = "An image with optional caption and attribution"


class HeadingBlock(StructBlock):
    heading_text = CharBlock(classname="title", required=True)
    size = ChoiceBlock(
        choices=[
            ("", "Select a header size"),
            ("h2", "H2"),
            ("h3", "H3"),
            ("h4", "H4"),
        ],
        blank=True,
        required=False,
    )

    class Meta:
        icon = "title"
        template = "blocks/heading_block.html"
        description = "A heading with level two, three, or four"


class QuoteBlock(StructBlock):
    text = RichTextBlock()
    attribute_name = CharBlock(blank=True, required=False)

    class Meta:
        icon = "openquote"
        template = "blocks/quote_block.html"


class BaseStreamBlock(StreamBlock):
    heading_block = HeadingBlock()
    paragraph_block = RichTextBlock(
        icon="pilcrow",
        template="blocks/paragraph_block.html",
        description="A rich text paragraph",
    )
    image_block = CaptionedImageBlock()
    quote_block = QuoteBlock()
    embed_block = EmbedBlock(
        help_text="Insert an embed URL e.g https://www.youtube.com/watch?v=SGJFWirQ3ks",
        icon="media",
        template="blocks/embed_block.html",
        preview_template="base/preview/static_embed_block.html",
        preview_value="https://www.youtube.com/watch?v=mwrGSfiB1Mg",
        description="An embedded video or other media",
    )