from django.core.management.base import BaseCommand
from inventory.models import Role

class Command(BaseCommand):
    help = 'Creates default roles with their permissions'

    def handle(self, *args, **kwargs):
        # Create Administrator role with all permissions
        admin_permissions = {}
        for group in Role.get_all_permissions().values():
            for perm_key in group.keys():
                admin_permissions[perm_key] = True

        admin_role, admin_created = Role.objects.get_or_create(
            name='Administrator',
            defaults={
                'description': 'Full system access with all permissions',
                'permissions': admin_permissions
            }
        )
        if admin_created:
            self.stdout.write(self.style.SUCCESS('Successfully created Administrator role'))
        else:
            admin_role.permissions = admin_permissions
            admin_role.save()
            self.stdout.write(self.style.SUCCESS('Updated Administrator role permissions'))

        # Create Manager role with specific permissions
        manager_permissions = {
            'view_dashboard': True,
            'view_employee': True,
            'add_employee': True,
            'change_employee': True,
            'view_asset': True,
            'add_asset': True,
            'change_asset': True,
            'assign_asset': True,
            'view_asset_history': True,
            'view_department': True,
            'view_team': True,
            'manage_team_members': True,
            'view_asset_type': True,
            'view_owner_company': True,
            'view_user': True,
            'view_role': True,
            'view_message': True,
            'send_message': True,
            'delete_message': True,
        }

        manager_role, manager_created = Role.objects.get_or_create(
            name='Manager',
            defaults={
                'description': 'Department and team management access',
                'permissions': manager_permissions
            }
        )
        if manager_created:
            self.stdout.write(self.style.SUCCESS('Successfully created Manager role'))
        else:
            manager_role.permissions = manager_permissions
            manager_role.save()
            self.stdout.write(self.style.SUCCESS('Updated Manager role permissions'))

        # Create User role with basic permissions
        user_permissions = {
            'view_dashboard': True,
            'view_employee': True,
            'view_asset': True,
            'view_department': True,
            'view_team': True,
            'view_asset_type': True,
            'view_owner_company': True,
            'view_message': True,
            'send_message': True,
            'delete_message': True,
        }

        user_role, user_created = Role.objects.get_or_create(
            name='User',
            defaults={
                'description': 'Basic system access',
                'permissions': user_permissions
            }
        )
        if user_created:
            self.stdout.write(self.style.SUCCESS('Successfully created User role'))
        else:
            user_role.permissions = user_permissions
            user_role.save()
            self.stdout.write(self.style.SUCCESS('Updated User role permissions')) 