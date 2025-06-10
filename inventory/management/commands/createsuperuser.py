from django.core.management.base import CommandError
from django.contrib.auth.management.commands import createsuperuser
from django.contrib.auth.models import User
from inventory.models import Role, UserProfile
from django.db import transaction

class Command(createsuperuser.Command):
    help = 'Creates a single, unique superuser with an assigned "Superuser" role.'

    def handle(self, *args, **options):
        # 1. Check if a superuser already exists
        if User.objects.filter(is_superuser=True).exists():
            raise CommandError('A superuser already exists. This system is designed to have only one superuser for security reasons.')
        
        try:
            # Use the default command's logic to create the user.
            # This will print "Superuser created successfully." if it works.
            super().handle(*args, **options)
            
            # The user is now created. We need to find it to assign the role.
            # We can reliably get it by finding the superuser with the highest ID (most recent).
            user = User.objects.filter(is_superuser=True).latest('id')

            # Ensure this user doesn't already have a profile, just in case.
            if hasattr(user, 'profile'):
                 self.stdout.write(self.style.WARNING(f"User '{user.username}' already has a profile. Skipping role assignment."))
                 return

            with transaction.atomic():
                # 2. Create and assign the "Superuser" role with all permissions
                role_name = "Superuser"
                role_description = "Full system access for the site superuser. This role is automatically assigned."
                
                # Get all permissions from the single source of truth in the Role model
                all_permission_groups = Role.get_all_defined_permissions()
                all_permissions = {}
                for group in all_permission_groups.values():
                    for perm_key in group:
                        all_permissions[perm_key] = True

                superuser_role, role_created = Role.objects.get_or_create(
                    name=role_name,
                    defaults={'description': role_description, 'permissions': all_permissions}
                )
                
                if not role_created:
                    superuser_role.permissions = all_permissions
                    superuser_role.save()

                # 3. Create the UserProfile linking the user to the role
                UserProfile.objects.create(user=user, role=superuser_role)

                self.stdout.write(self.style.SUCCESS(f"Successfully assigned the '{role_name}' role to superuser '{user.username}'."))

        except CommandError as e:
            # Re-raise the CommandError to show it to the user
            raise e
        except Exception as e:
            # Catch any other unexpected errors
            raise CommandError(f'An unexpected error occurred during superuser post-processing: {e}') 