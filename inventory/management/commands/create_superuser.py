from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from inventory.models import Role, UserProfile
from django.db import transaction

class Command(BaseCommand):
    help = 'Creates a superuser with a default role'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username for the superuser')
        parser.add_argument('--email', type=str, help='Email for the superuser')
        parser.add_argument('--password', type=str, help='Password for the superuser')

    def handle(self, *args, **options):
        username = options.get('username') or 'admin'
        email = options.get('email') or 'admin@example.com'
        password = options.get('password') or 'admin123'

        try:
            with transaction.atomic():
                # Create superuser
                user = User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password
                )

                # Create default admin role if it doesn't exist
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

                # Create user profile with admin role
                UserProfile.objects.create(
                    user=user,
                    role=admin_role,
                    is_active=True
                )

                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created superuser "{username}" with admin role')
                )
                self.stdout.write(f'Username: {username}')
                self.stdout.write(f'Password: {password}')
                self.stdout.write('Please change the password after first login!')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating superuser: {str(e)}')
            ) 