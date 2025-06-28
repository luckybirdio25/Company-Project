from .models import Ticket
from django.db.models import Q

def unread_tickets(request):
    """Add unread tickets count and new replies status to all templates."""
    if request.user.is_authenticated:
        # Get unread tickets count (excluding replies and tickets sent by the user)
        unread_count = Ticket.objects.filter(
            ~Q(sender=request.user),  # Not sent by the current user
            recipient=request.user,
            is_read=False,
            parent_ticket__isnull=True  # Only count parent tickets
        ).count()
        
        # Check for new replies received by the user (not sent by the user)
        has_new_replies = Ticket.objects.filter(
            ~Q(sender=request.user),  # Sender is not the current user
            recipient=request.user,  # User is the recipient
            sender__isnull=False,  # Has a sender
            parent_ticket__isnull=False,  # Is a reply
            has_new_reply=True  # Has new reply flag
        ).exists()
        
        return {
            'unread_tickets_count': unread_count,
            'has_new_replies': has_new_replies
        }
    return {
        'unread_tickets_count': 0,
        'has_new_replies': False
    } 