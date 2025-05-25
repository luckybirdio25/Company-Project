from .models import Message
from django.db.models import Q

def unread_messages(request):
    """Add unread messages count and new replies status to all templates."""
    if request.user.is_authenticated:
        # Get unread messages count (excluding replies and messages sent by the user)
        unread_count = Message.objects.filter(
            ~Q(sender=request.user),  # Not sent by the current user
            recipient=request.user,
            is_read=False,
            parent_message__isnull=True  # Only count parent messages
        ).count()
        
        # Check for new replies received by the user (not sent by the user)
        has_new_replies = Message.objects.filter(
            ~Q(sender=request.user),  # Sender is not the current user
            recipient=request.user,  # User is the recipient
            sender__isnull=False,  # Has a sender
            parent_message__isnull=False,  # Is a reply
            has_new_reply=True  # Has new reply flag
        ).exists()
        
        return {
            'unread_messages_count': unread_count,
            'has_new_replies': has_new_replies
        }
    return {
        'unread_messages_count': 0,
        'has_new_replies': False
    } 