from django import template
from taggit.models import Tag
from django.db.models import Count

register = template.Library()


@register.simple_tag
def get_popular_tags():
    return Tag.objects.annotate(count=Count("taggit_taggeditem_items")).order_by(
        "-count"
    )[:10]
