from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .models import Refund
from .forms import RefundForm

@login_required
def refundCreateView(request, refund_id=None):
    user = request.user
    refund = None
    warning_message = None

    if refund_id:
        if user.is_organizer:
            refund = get_object_or_404(Refund, id=refund_id)
        else:
            refund = get_object_or_404(Refund, id=refund_id, user=user)

    if not refund_id and not user.is_organizer:
        pending_refunds = Refund.objects.filter(user=user, status='pending')
        if pending_refunds.exists():
            pending_tickets = [r.ticket_code for r in pending_refunds]
            warning_message = {
                'type': 'warning',
                'message': f"Tienes solicitudes de reembolso pendientes para los tickets: {', '.join(pending_tickets)}. "
                          "No podrás crear nuevas solicitudes para esos tickets hasta que sean procesadas."
            }

    if request.method == "POST":
        form = RefundForm(request.POST, instance=refund, user=user)
        if form.is_valid():
            refund = form.save(commit=False)
            refund.user = user
            refund.save()
            
            messages.success(request, 'Tu solicitud de reembolso ha sido enviada correctamente.')
            return redirect("/refunds/")
    else:
        form = RefundForm(instance=refund, user=user)

    context = {
        "form": form, 
        "refund": refund,
        "warning_message": warning_message
    }
    
    return render(request, "refunds/refund_page.html", context)

@login_required
def refundListView(request):
    user = request.user

    if not user.is_organizer:
        refunds = Refund.objects.filter(user=user).order_by("-created_at")
    else:
        refunds = Refund.objects.all().order_by("-created_at")
    
    return render(request, "refunds/refunds_list.html", {"refunds": refunds})

@login_required
def refundDeleteView(request, id):
    user = request.user
    refund = get_object_or_404(Refund, id=id)

    if not (user == refund.user and refund.status == 'pending'):
        messages.error(request, 'No puedes eliminar esta solicitud.')
        return redirect("/refunds/")

    if request.method == "POST":
        refund.delete()
        messages.success(request, 'Solicitud de reembolso eliminada correctamente.')
        return redirect("/refunds/")
        
    return render(request, "refunds/refund_confirm_delete.html", {"refund": refund})

@login_required
def refundConfirmActionView(request, id):
    user = request.user
    refund = get_object_or_404(Refund, id=id)

    if not user.is_organizer:
        messages.error(request, 'No tienes permisos para realizar esta acción.')
        return redirect('refunds:refund_list')

    if refund.status != 'pending':
        messages.warning(request, 'Esta solicitud ya ha sido procesada.')
        return redirect('refunds:refund_list')

    if request.method == "POST":
        action = request.POST.get('action')

        if action == 'approve':
            refund.status = 'approved'
            messages.success(request, f'Solicitud de reembolso aprobada para el ticket {refund.ticket_code}.')
        elif action == 'reject':
            refund.status = 'rejected'
            messages.success(request, f'Solicitud de reembolso rechazada para el ticket {refund.ticket_code}.')
        else:
            messages.error(request, 'Acción no válida.')
            return redirect('refunds:refund_list')
            
        refund.save()
        return redirect('refunds:refund_list')

    else: 
        action = request.GET.get('action')

        if action not in ['approve', 'reject']:
            messages.error(request, 'Acción no válida.')
            return redirect('refunds:refund_list')
            
        context = {
            'refund': refund,
            'action': action,
        }
        return render(request, "refunds/refund_confirm_action.html", context)