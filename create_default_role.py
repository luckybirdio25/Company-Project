import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_app.settings')
django.setup()

from django.contrib.auth.models import User
from inventory.models import Role, UserProfile

def create_default_role():
    # Create default role with all permissions
    default_role, created = Role.objects.get_or_create(
        name='Superuser',
        defaults={
            'description': 'Superuser role with all permissions',
            'permissions': {
                'asset': ['view', 'add', 'edit', 'delete'],
                'employee': ['view', 'add', 'edit', 'delete'],
                'team': ['view', 'add', 'edit', 'delete'],
                'user': ['view', 'add', 'edit', 'delete'],
                'role': ['view', 'add', 'edit', 'delete'],
            }
        }
    )
    
    # Assign role to all superusers
    for user in User.objects.filter(is_superuser=True):
        UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'role': default_role,
                'is_active': True
            }
        )

if __name__ == '__main__':
    create_default_role() 