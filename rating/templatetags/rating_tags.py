from django import template
from django.db.models import Avg, Count
from django.utils.safestring import mark_safe

from ..forms import RatingForm
from ..models import Rating

register = template.Library()

@register.inclusion_tag("rating/rating_section.html", takes_context=True)
def render_rating(context, event):
    ratings = event.ratings.select_related("user")
    form = RatingForm()
    return {
        "event": event,
        "user": context["user"],
        "ratings": ratings,
        "form": form,
    }
