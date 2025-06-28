from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import RegexValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging
import pytz

logger = logging.getLogger(__name__)

def get_cairo_time():
    cairo_tz = pytz.timezone('Africa/Cairo')
    return timezone.now().astimezone(cairo_tz)

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_name_display(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'

class Employee(models.Model):
    STATUS_CHOICES = [
        ('employed', 'Employed'),
        ('on_leave', 'On Leave'),
        ('terminated', 'Terminated'),
        ('training', 'Training'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    employee_id = models.CharField(max_length=20, unique=True, help_text="Enter employee ID (e.g., 9970)")
    national_id = models.CharField(max_length=14, unique=True, help_text="Enter the 14-digit national ID number")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True)
    position = models.ForeignKey('Position', on_delete=models.SET_NULL, null=True)
    hire_date = models.DateField(null=True, blank=True)
    company = models.ForeignKey('OwnerCompany', on_delete=models.PROTECT, related_name='employees')
    employment_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='employed')
    retirement_date = models.DateField(null=True, blank=True)
    resignation_date = models.DateField(null=True, blank=True)
    training_start_date = models.DateField(null=True, blank=True)
    training_end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employee_id})"

class Team(models.Model):
    name = models.CharField(max_length=100)
    department = models.ForeignKey('Department', on_delete=models.CASCADE)
    manager = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_teams')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class TeamMember(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='members')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='team_memberships')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('team', 'employee')

    def __str__(self):
        return f"{self.employee} - {self.team}"

class Position(models.Model):
    name = models.CharField(max_length=100)
    department = models.ForeignKey('Department', on_delete=models.CASCADE, related_name='positions')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.department.name})"

    class Meta:
        ordering = ['department', 'name']

class OwnerCompany(models.Model):
    code = models.CharField(max_length=20, unique=True, null=True, blank=True)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Owner Company'
        verbose_name_plural = 'Owner Companies'

    def __str__(self):
        return self.name

class AssetType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    display_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_name']
        verbose_name = 'Asset Type'
        verbose_name_plural = 'Asset Types'

    def __str__(self):
        return self.display_name

class ITAsset(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('assigned', 'Assigned'),
        ('maintenance', 'In Maintenance'),
        ('return', 'Returned'),
        ('disposed', 'Disposed'),
    ]

    # Basic Information
    name = models.CharField(max_length=100, default='Unknown Asset')
    asset_type = models.ForeignKey(AssetType, on_delete=models.PROTECT)
    serial_number = models.CharField(max_length=50, unique=True)
    model = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100)
    owner = models.ForeignKey(OwnerCompany, on_delete=models.PROTECT)
    purchase_date = models.DateField()
    warranty_expiry = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    assigned_to = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)

    # Network Information
    mac_address_wifi = models.CharField(max_length=17, blank=True, verbose_name='Wi-Fi MAC Address')
    mac_address_ethernet = models.CharField(max_length=17, blank=True, verbose_name='Ethernet MAC Address')
    ip_address = models.CharField(max_length=15, blank=True, verbose_name='IP Address')

    # Delivery Information
    delivery_letter_code = models.CharField(max_length=50, blank=True)
    receipt_date = models.DateField(null=True, blank=True)

    # Computer Specifications (for laptops and desktops)
    processor = models.CharField(max_length=100, blank=True, null=True)
    ram_size = models.CharField(max_length=50, blank=True, null=True)
    hdd1_capacity = models.CharField(max_length=50, blank=True, null=True, verbose_name='Primary Storage')
    hdd2_capacity = models.CharField(max_length=50, blank=True, null=True, verbose_name='Secondary Storage')
    operating_system = models.CharField(max_length=50, blank=True, null=True)
    os_version = models.CharField(max_length=50, blank=True, null=True)

    # Monitor Specifications
    screen_size = models.CharField(max_length=20, blank=True, null=True)
    resolution = models.CharField(max_length=50, blank=True, null=True)
    refresh_rate = models.CharField(max_length=20, blank=True, null=True)
    panel_type = models.CharField(max_length=50, blank=True, null=True)
    vesa_mount = models.BooleanField(default=False)
    built_in_speakers = models.BooleanField(default=False)

    # Printer Specifications
    printer_type = models.CharField(max_length=50, blank=True, null=True)
    connection_type = models.CharField(max_length=50, blank=True, null=True)
    printer_department = models.CharField(max_length=100, blank=True, null=True)
    printer_responsible = models.CharField(max_length=100, blank=True, null=True)
    paper_size_support = models.CharField(max_length=100, blank=True, null=True)
    duplex_printing = models.BooleanField(default=False)
    toner_cartridge_model = models.CharField(max_length=100, blank=True, null=True)

    # UPS Specifications
    ups_capacity = models.IntegerField(blank=True, null=True, help_text='Capacity in VA')
    ups_battery_count = models.IntegerField(blank=True, null=True, help_text='Number of batteries')
    ups_battery_life = models.IntegerField(blank=True, null=True, help_text='Remaining battery life in months')
    ups_battery_replacement_date = models.DateField(blank=True, null=True)
    ups_manufacturer = models.CharField(max_length=100, blank=True, null=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if not is_new:
            old_instance = ITAsset.objects.get(pk=self.pk)
            if (old_instance.status != self.status or 
                old_instance.assigned_to != self.assigned_to):
                AssetHistory.objects.create(
                    asset=self,
                    status=self.status,
                    assigned_to=self.assigned_to,
                    notes=f"Status changed to {self.get_status_display()}"
                )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.serial_number})"

class AssetHistory(models.Model):
    asset = models.ForeignKey(ITAsset, on_delete=models.CASCADE, related_name='history')
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=ITAsset.STATUS_CHOICES)
    assigned_to = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-date']
        verbose_name_plural = 'Asset Histories'

    def __str__(self):
        return f"{self.asset.name} - {self.get_status_display()} - {self.date}"

class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    permissions = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def has_permission(self, permission):
        """Check if the role has a specific permission."""
        logger.debug(f"Checking permission '{permission}' for role '{self.name}'")
        logger.debug(f"Role permissions: {self.permissions}")
        # Check if the permission exists in the permissions dict and is True
        has_perm = self.permissions.get(permission, False) is True
        logger.debug(f"Permission check result: {has_perm}")
        logger.debug(f"Permission value in dict: {self.permissions.get(permission)}")
        logger.debug(f"Permission type: {type(self.permissions.get(permission))}")
        return has_perm

    def get_all_permissions(self):
        """Get all permissions for this role."""
        perms = [perm for perm, value in self.permissions.items() if value is True]
        logger.debug(f"All permissions for role '{self.name}': {perms}")
        return perms

    def add_permission(self, permission):
        """Add a permission to the role."""
        logger.debug(f"Adding permission '{permission}' to role '{self.name}'")
        self.permissions[permission] = True
        self.save()
        logger.debug(f"Updated permissions: {self.permissions}")

    def remove_permission(self, permission):
        """Remove a permission from the role."""
        if permission in self.permissions:
            logger.debug(f"Removing permission '{permission}' from role '{self.name}'")
            del self.permissions[permission]
            self.save()
            logger.debug(f"Updated permissions: {self.permissions}")

    def clear_permissions(self):
        """Clear all permissions from the role."""
        logger.debug(f"Clearing all permissions for role '{self.name}'")
        self.permissions = {}
        self.save()

    @staticmethod
    def get_all_defined_permissions():
        """
        Returns a dictionary of all possible permissions, grouped by category.
        This is the single source of truth for permissions in the application.
        """
        return {
            'Company Management': {
                'view_company': 'View Companies', 'add_company': 'Add Companies',
                'change_company': 'Edit Companies', 'delete_company': 'Delete Companies',
            },
            'Asset Type Management': {
                'view_assettype': 'View Asset Types', 'add_assettype': 'Add Asset Types',
                'change_assettype': 'Edit Asset Types', 'delete_assettype': 'Delete Asset Types',
            },
            'Department Management': {
                'view_department': 'View Departments', 'add_department': 'Add Departments',
                'change_department': 'Edit Departments', 'delete_department': 'Delete Departments',
            },
            'Asset Management': {
                'view_asset': 'View Assets', 'add_asset': 'Add Assets',
                'change_asset': 'Edit Assets', 'delete_asset': 'Delete Assets',
                'download_asset': 'Download Assets', 'upload_asset': 'Upload Assets',
            },
            'Employee Management': {
                'view_employee': 'View Employees', 'add_employee': 'Add Employees',
                'change_employee': 'Edit Employees', 'delete_employee': 'Delete Employees',
            },
            'User Management': {
                'view_user': 'View Users', 'add_user': 'Add Users',
                'change_user': 'Edit Users', 'delete_user': 'Delete Users',
            },
            'Role Management': {
                'view_role': 'View Roles', 'add_role': 'Add Roles',
                'change_role': 'Edit Roles', 'delete_role': 'Delete Roles',
            },
            'Team Management': {
                'view_team': 'View Teams', 'add_team': 'Add Teams',
                'change_team': 'Edit Teams', 'delete_team': 'Delete Teams',
            },
            'Ticket Management': {
                'view_ticket': 'View Tickets', 'add_ticket': 'Create Tickets',
                'change_ticket': 'Edit Tickets', 'delete_ticket': 'Delete Tickets',
            },
        }

    def get_permission_count(self):
        """Returns the number of active permissions for the role."""
        if isinstance(self.permissions, dict):
            return sum(1 for permission_value in self.permissions.values() if permission_value is True)
        return 0

    class Meta:
        ordering = ['name']

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True, blank=True)
    team = models.ForeignKey('Team', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_seen = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

    @property
    def is_online(self):
        """Returns True if the user was last seen within the last 5 minutes."""
        if self.last_seen:
            return (timezone.now() - self.last_seen) < timezone.timedelta(minutes=5)
        return False

    def has_permission(self, permission):
        """Check if the user has a specific permission through their role."""
        logger.debug(f"Checking permission '{permission}' for user '{self.user.username}'")
        if self.role:
            logger.debug(f"User has role: {self.role.name}")
            has_perm = self.role.has_permission(permission)
            logger.debug(f"Permission check result: {has_perm}")
            return has_perm
        logger.debug("User has no role assigned")
        return False

    def get_all_permissions(self):
        """Get all permissions for this user through their role."""
        if self.role:
            perms = self.role.get_all_permissions()
            logger.debug(f"All permissions for user '{self.user.username}': {perms}")
            return perms
        return []

    class Meta:
        ordering = ['user__username']

class Ticket(models.Model):
    ticket_number = models.CharField(max_length=20, unique=True, blank=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_tickets')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_tickets')
    subject = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    parent_ticket = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    has_new_reply = models.BooleanField(default=False)
    asset = models.ForeignKey(ITAsset, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets')
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"#{self.ticket_number} - {self.subject}"

    def generate_ticket_number(self):
        """Generate a sequential ticket number in the format TICKET-YYYY-XXXX"""
        # Get the current year
        current_year = timezone.now().year
        
        # Get the last ticket number for the current year
        last_ticket = Ticket.objects.filter(
            ticket_number__startswith=f'TICKET-{current_year}-'
        ).order_by('-ticket_number').first()
        
        if last_ticket:
            # Extract the number part and increment it
            last_number = int(last_ticket.ticket_number.split('-')[-1])
            new_number = last_number + 1
        else:
            # If no tickets exist for this year, start with 1
            new_number = 1
            
        # Format the new ticket number without padding
        return f'TICKET-{current_year}-{new_number}'

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            self.ticket_number = self.generate_ticket_number()
        super().save(*args, **kwargs)

    def mark_as_read(self):
        self.is_read = True
        self.save(update_fields=['is_read'])

    def mark_replies_as_read(self):
        self.replies.filter(is_read=False).update(is_read=True)
        self.has_new_reply = False
        self.save(update_fields=['has_new_reply'])

    def get_replies(self):
        return self.replies.all().order_by('created_at')

# Monkey-patch the User model to use our custom role-based permissions
def custom_user_has_perm(self, perm, obj=None):
    """
    Checks if the user has a specific permission.
    - Superusers have all permissions.
    - Otherwise, it checks the user's role through their profile.
    """
    # Superusers have all permissions
    if self.is_active and self.is_superuser:
        return True

    # Check for custom role permissions via the user's profile
    if hasattr(self, 'profile'):
        # Extract the permission name (e.g., 'view_role' from 'inventory.view_role')
        permission_name = perm.split('.')[-1]
        return self.profile.has_permission(permission_name)

    # If no profile or other checks fail, deny permission
    return False

# Replace the default has_perm method with our custom one
User.add_to_class('has_perm', custom_user_has_perm)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Only create profile if it doesn't exist, without granting permissions
        UserProfile.objects.get_or_create(
            user=instance,
            defaults={'role': None}  # Don't set default role, let the view handle it
        )

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Only create profile if it doesn't exist, without granting permissions
    UserProfile.objects.get_or_create(
        user=instance,
        defaults={'role': None}  # Don't set default role, let the view handle it
    )
