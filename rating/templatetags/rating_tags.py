from django import template
from ..forms import RatingForm
from ..models import Rating
from django.db.models import Avg, Count
from django.utils.safestring import mark_safe

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

@register.simple_tag
def event_rating_avg(event):
    sum = Rating.objects.filter(event=event).aggregate(
        avg=Avg('rating'),
        count=Count('id')
    )
    avg = sum['avg']
    count = sum['count']

    if count==0:
        return "Sin reseñas"

    avg_formatted = f"{avg:.1f}".replace('.', ',')
    return mark_safe(f"<strong>{avg_formatted}</strong> <i class='bi bi-star-fill text-warning'></i> ({count} Reseñas)")