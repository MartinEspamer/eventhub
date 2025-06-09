from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from app.models import Event, User

from .forms import NotificationForm
from .models import Notification, UserNotificationStatus


@login_required
def notification_management(request):
    notifications_created = Notification.objects.filter(creator=request.user)

    q = request.GET.get('q')
    event_filter = request.GET.get('event')
    priority_filter = request.GET.get('priority')

    if q:
        notifications_created = notifications_created.filter(title__icontains=q)
    if event_filter:
        notifications_created = notifications_created.filter(event_id=event_filter)
    if priority_filter:
        notifications_created = notifications_created.filter(priority=priority_filter)

    notifications_created = notifications_created.select_related('event').prefetch_related('recipients').order_by('-created_at')

    total_users_count = User.objects.filter(is_active=True).count()
    user_events = Event.objects.filter(organizer=request.user).order_by('-scheduled_at', 'title')

    return render(request, 'notifications/notification_management.html', {
        'notifications': notifications_created,
        'total_users_count': total_users_count,
        'user_events': user_events,
    })

@login_required
@transaction.atomic
def create_notification(request):
    if request.method == 'POST':
        form = NotificationForm(request.POST, user=request.user)
        if form.is_valid():
            notification = form.save(commit=False)
            notification.creator = request.user
            notification.save()
            recipients_list = list(form.cleaned_data.get('recipients', []))
            if recipients_list:
                statuses_to_create = [
                    UserNotificationStatus(user=recipient, notification=notification)
                    for recipient in recipients_list
                ]
                UserNotificationStatus.objects.bulk_create(statuses_to_create)
                messages.success(request, f'Notificación "{notification.title}" enviada a {len(recipients_list)} usuario(s).')
            else:
                 messages.warning(request, 'No se seleccionaron destinatarios.')
            return redirect('notifications:notification_management')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = NotificationForm(user=request.user)
    return render(request, 'notifications/create_notification.html', {
        'form': form
    })

@login_required
@transaction.atomic
def edit_notification(request, pk):
    notification = get_object_or_404(Notification, pk=pk, creator=request.user)
    if request.method == 'POST':
        form = NotificationForm(request.POST, instance=notification, user=request.user)
        if form.is_valid():
            notification = form.save(commit=False)

            desired_recipients_set = set(form.cleaned_data.get('recipients', []))
            current_statuses = UserNotificationStatus.objects.filter(notification=notification)
            current_recipients_set = set(status.user for status in current_statuses)

            users_to_add = desired_recipients_set - current_recipients_set
            users_to_remove = current_recipients_set - desired_recipients_set

            if users_to_remove:
                UserNotificationStatus.objects.filter(notification=notification, user__in=users_to_remove).delete()

            statuses_to_create = []
            for user_to_add in users_to_add:
                 statuses_to_create.append(
                      UserNotificationStatus(user=user_to_add, notification=notification)
                 )
            if statuses_to_create:
                 UserNotificationStatus.objects.bulk_create(statuses_to_create)

            notification.save()

            messages.success(request, f'Notificación "{notification.title}" actualizada exitosamente.')
            return redirect('notifications:notification_management')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = NotificationForm(instance=notification, user=request.user)
    return render(request, 'notifications/create_notification.html', {
        'form': form,
        'notification': notification
    })

@login_required
def delete_notification(request, pk):
    notification = get_object_or_404(Notification, pk=pk, creator=request.user)

    if request.method == 'POST':
        notification_title = notification.title
        notification.delete()
        messages.success(request, f'Notificación "{notification_title}" eliminada exitosamente.')
        return redirect('notifications:notification_management')
    else:
        return render(request, 'notifications/delete_confirm.html', {
            'notification': notification
        })

@login_required
def view_notification(request, pk):
    notification = get_object_or_404(
        Notification.objects.select_related('event', 'creator'),
        pk=pk,
        creator=request.user
    )
    recipient_statuses = UserNotificationStatus.objects.filter(notification=notification).select_related('user')
    return render(request, 'notifications/view_notification.html', {
        'notification': notification,
        'recipient_statuses': recipient_statuses
    })


@login_required
def user_notifications(request):
    user_statuses = UserNotificationStatus.objects.filter(user=request.user)\
        .select_related('notification', 'notification__creator', 'notification__event')\
        .order_by('-notification__created_at')

    unread_count = user_statuses.filter(is_read=False).count()

    context = {
        'user_statuses': user_statuses,
        'unread_count': unread_count,
    }
    return render(request, 'notifications/user_notifications.html', context)

@login_required
def mark_notification_read(request, pk):
    status = get_object_or_404(UserNotificationStatus, pk=pk, user=request.user)
    status.mark_as_read()
    messages.success(request, f'Notificación "{status.notification.title}" marcada como leída.')

    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect(reverse('notifications:user_notifications'))

@login_required
@transaction.atomic
def mark_all_notifications_read(request):
    if request.method == 'POST':
        statuses_to_update = UserNotificationStatus.objects.filter(user=request.user, is_read=False)
        count = statuses_to_update.count()
        if count > 0:
            statuses_to_update.update(is_read=True, read_at=timezone.now())
            messages.info(request, f'{count} notificaciones marcadas como leídas.')
        else:
            messages.info(request, 'No tenías notificaciones no leídas.')
    else:
         messages.warning(request, 'Acción no permitida.')
    return redirect(reverse('notifications:user_notifications'))

@login_required
def notification_detail(request, pk):
    status = get_object_or_404(
        UserNotificationStatus.objects.select_related(
            'notification', 'notification__creator', 'notification__event'
        ),
        pk=pk,
        user=request.user
    )
    status.mark_as_read()
    return render(request, 'notifications/notification_detail.html', {'status': status})