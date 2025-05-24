import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_app.settings')
django.setup()

from django.contrib.auth.models import User
from inventory.models import Role, UserProfile

def setup_admin():
    # Create admin role
    admin_role, created = Role.objects.get_or_create(
        name='Administrator',
        defaults={
            'description': 'Full system access',
            'permissions': {
                'view_company': True,
                'add_company': True,
                'change_company': True,
                'delete_company': True,
                'view_assettype': True,
                'add_assettype': True,
                'change_assettype': True,
                'delete_assettype': True,
                'view_department': True,
                'add_department': True,
                'change_department': True,
                'delete_department': True,
                'view_asset': True,
                'add_asset': True,
                'change_asset': True,
                'delete_asset': True,
                'view_employee': True,
                'add_employee': True,
                'change_employee': True,
                'delete_employee': True,
                'view_user': True,
                'add_user': True,
                'change_user': True,
                'delete_user': True,
                'view_role': True,
                'add_role': True,
                'change_role': True,
                'delete_role': True,
            }
        }
    )

    # Get the superuser
    admin_user = User.objects.get(username='admin')
    
    # Create or update user profile with admin role
    UserProfile.objects.update_or_create(
        user=admin_user,
        defaults={
            'role': admin_role,
            'is_active': True
        }
    )
    
    print("Successfully set up admin role and assigned it to the superuser")

if __name__ == '__main__':
    setup_admin() 