import json
import os
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from blog.models import BlogPage

class Command(BaseCommand):
    help = "Export all blog posts to a JSON file."

    def handle(self, *args, **options):
        timestamp_filename = timezone.now().strftime("%y_%m_%d")
        timestamp_logging = timezone.now().strftime("%d/%m/%y")

        filename = f"export__{timestamp_filename}.json"
        output_dir = os.path.join(settings.BASE_DIR, "blog", "post_exports")

        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)

        # get all posts, including drafts
        blog_posts = BlogPage.objects.all().order_by("-latest_revision_created_at")

        data = []
        for post in blog_posts:
            # serialize StreamField content
            if hasattr(post.body, "stream_data"):
                body_content = post.body.stream_data
            else:
                try:
                    body_content = json.loads(post.body)
                except (TypeError, json.JSONDecodeError):
                    body_content = str(post.body)

            data.append({
                "id": post.id,
                "title": post.title,
                "slug": post.slug,
                "introduction": post.introduction,
                "image_url": post.image_url,
                "image_file": post.image_file.file.url if post.image_file else None,
                "body": body_content,
                "date_published": post.date_published.isoformat() if post.date_published else None,
                "url": getattr(post, "url", None),
                "live": post.live,
                "last_modified": post.latest_revision_created_at.isoformat() if post.latest_revision_created_at else None,
            })

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        self.stdout.write(self.style.SUCCESS(f"Exported {len(data)} blog posts as of {timestamp_logging}"))

