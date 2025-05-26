import datetime

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.contrib import messages
from django.urls import reverse
from django.db.models import Exists, OuterRef, Value, BooleanField # Asegúrate de tener estas importaciones

from tickets.models import Ticket

from category.models import Category

from .models import Event, User, Favorite


def register(request):
    if request.method == "POST":
        email = request.POST.get("email")
        username = request.POST.get("username")
        is_organizer = request.POST.get("is-organizer") is not None
        password = request.POST.get("password")
        password_confirm = request.POST.get("password-confirm")

        errors = User.validate_new_user(email, username, password, password_confirm)

        if len(errors) > 0:
            return render(
                request,
                "accounts/register.html",
                {
                    "errors": errors,
                    "data": request.POST,
                },
            )
        else:
            user = User.objects.create_user(
                email=email, username=username, password=password, is_organizer=is_organizer
            )
            login(request, user)
            return redirect("events")

    return render(request, "accounts/register.html", {})


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is None:
            return render(
                request, "accounts/login.html", {"error": "Usuario o contraseña incorrectos"}
            )

        login(request, user)
        return redirect("events")

    return render(request, "accounts/login.html")


def home(request):
    return render(request, "home.html")


@login_required
def events(request):
    user = request.user
    url_name = request.resolver_match.url_name
    print(f"Parámetro GET 'favorites_only': {request.GET.get('favorites_only')}")
    favorites_only = request.GET.get("favorites_only") == "on"
    print(f"Valor booleano de favorites_only: {favorites_only}")
    show_past = (url_name == "events_all")

    if show_past:
        current_events = Event.get_all_events()
    else:
        current_events = Event.get_upcoming_events()

    if favorites_only and user.is_authenticated:
       current_events = current_events.filter(favorites__user=user)

    if user.is_authenticated:
       final_events = current_events.annotate(
            is_favorite=Exists(Favorite.objects.filter(user=user, event=OuterRef('pk')))
        )
    else:
        final_events = current_events.annotate(
            is_favorite=Value(False, output_field=BooleanField())
        )
    
    final_events = final_events.order_by('-scheduled_at')


    return render(
        request,
        "app/events.html",
        { "events": final_events, "user_is_organizer": user.is_organizer, "favorites_only": favorites_only },
    )


@login_required
def event_detail(request, id):
    event = get_object_or_404(Event, pk=id)
    if request.user.is_authenticated:
        user_has_tickets = Ticket.objects.filter(event=event, user=request.user).exists()
    return render(request, "app/event_detail.html", {"event": event,  
                                                     "user_is_organizer": request.user.is_organizer,
                                                     'user_has_tickets': user_has_tickets})


@login_required
def event_delete(request, id):
    user = request.user
    if not user.is_organizer:
        return redirect("events")

    if request.method == "POST":
        event = get_object_or_404(Event, pk=id)
        event.delete()
        return redirect("events")

    return redirect("events")


@login_required
def event_form(request, id=None):
    user = request.user

    if not user.is_organizer:
        return redirect("events")

    categories = Category.objects.filter(is_active=True)

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        date = request.POST.get("date")
        time = request.POST.get("time")
        category_ids = request.POST.getlist("categories")

        [year, month, day] = date.split("-")
        [hour, minutes] = time.split(":")

        scheduled_at = timezone.make_aware(
            datetime.datetime(int(year), int(month), int(day), int(hour), int(minutes))
        )

        if id is None:
            event = Event.objects.create( title=title, description=description, scheduled_at=scheduled_at, organizer=request.user)
            event.categories.set(category_ids)
        else:
            event = get_object_or_404(Event, pk=id)
            event.update(title, description, scheduled_at, request.user)
            event.categories.set(category_ids)

        return redirect("events")

    event = {}
    if id is not None:
        event = get_object_or_404(Event, pk=id)

    return render(
        request,
        "app/event_form.html",
        {
            "event": event,
            "categories": categories,
            "user_is_organizer": request.user.is_organizer,
        },
    )


@login_required
def event_form_view(request, id):
    categories = Category.objects.filter(is_active=True)
    event = get_object_or_404(Event, pk=id)

    return render(request, "event_form.html", {
        "event": event,
        "categories": categories,
    })

@login_required
def toggle_favorite(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    user = request.user
    favorite, created = Favorite.objects.get_or_create(user=user, event=event)

    if not created:
        favorite.delete()
        messages.success(request, "Evento eliminado de favoritos")
    else:
        messages.success(request, "Evento agregado a favoritos")

    referer = request.META.get('HTTP_REFERER', reverse('events'))
    return HttpResponseRedirect(referer)