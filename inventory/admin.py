from django.contrib import admin
from django import forms
from django.utils.html import format_html
from .models import Employee, ITAsset, Department, Position, AssetType, OwnerCompany, Role

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('get_name_display', 'description', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    ordering = ('name',)

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'description', 'created_at', 'updated_at')
    list_filter = ('department',)
    search_fields = ('name', 'description')
    ordering = ('department', 'name')

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'first_name', 'last_name', 'email', 'department', 'position', 'employment_status')
    list_filter = ('department', 'employment_status')
    search_fields = ('employee_id', 'first_name', 'last_name', 'email', 'position')
    ordering = ('last_name', 'first_name')
    fieldsets = (
        ('Personal Information', {
            'fields': ('employee_id', 'first_name', 'last_name', 'email', 'phone_number')
        }),
        ('Employment Information', {
            'fields': ('department', 'position', 'hire_date', 'employment_status')
        }),
        ('Location Information', {
            'fields': ('office_location', 'desk_number')
        }),
        ('System Access', {
            'fields': ('system_username', 'system_password')
        }),
    )

@admin.register(AssetType)
class AssetTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_name')
    search_fields = ('name', 'display_name')
    ordering = ('display_name',)

@admin.register(OwnerCompany)
class OwnerCompanyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('code', 'name')
    ordering = ('name',)

@admin.register(ITAsset)
class ITAssetAdmin(admin.ModelAdmin):
    list_display = ('name', 'asset_type', 'serial_number', 'owner', 'status', 'assigned_to')
    list_filter = ('asset_type', 'owner', 'status')
    search_fields = ('name', 'serial_number', 'model', 'manufacturer')
    ordering = ('name',)
    fieldsets = (
        ('Asset Information', {
            'fields': ('name', 'asset_type', 'serial_number', 'model', 'manufacturer')
        }),
        ('Assignment Information', {
            'fields': ('status', 'assigned_to')
        }),
        ('Purchase Information', {
            'fields': ('purchase_date', 'warranty_expiry')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
    )

class RoleAdminForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['name', 'description', 'permissions']
        widgets = {
            'permissions': forms.HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        
        # Get all permissions and their current states
        all_permissions = Role.get_all_permissions()
        current_states = instance.permissions if instance else {}
        
        # Create fields for each permission group
        for group_name, permissions in all_permissions.items():
            # Add group header
            self.fields[f'group_{group_name}'] = forms.CharField(
                required=False,
                label=group_name,
                widget=forms.TextInput(attrs={
                    'class': 'permission-group-header',
                    'readonly': True,
                    'style': 'border: none; background: none; font-weight: bold; color: #417690;'
                })
            )
            
            # Add checkboxes for each permission
            for perm_key, perm_label in permissions.items():
                self.fields[perm_key] = forms.BooleanField(
                    required=False,
                    label=perm_label,
                    initial=current_states.get(perm_key, False),
                    widget=forms.CheckboxInput(attrs={'class': 'permission-checkbox'})
                )

    def clean(self):
        cleaned_data = super().clean()
        permissions = {}
        
        # Get all permission fields (excluding group headers)
        for field_name, value in cleaned_data.items():
            if not field_name.startswith('group_'):
                permissions[field_name] = value
        
        cleaned_data['permissions'] = permissions
        return cleaned_data

class RoleAdmin(admin.ModelAdmin):
    form = RoleAdminForm
    list_display = ['name', 'description', 'get_permission_count']
    search_fields = ['name', 'description']

    def get_permission_count(self, obj):
        if obj.permissions:
            active_permissions = sum(1 for v in obj.permissions.values() if v)
            return f"{active_permissions} permissions active"
        return "No permissions"
    get_permission_count.short_description = "Active Permissions"

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj and obj.name == 'Administrator':
            # Make all checkboxes readonly for Administrator role
            for field_name, field in form.base_fields.items():
                if isinstance(field, forms.BooleanField):
                    field.widget.attrs['disabled'] = 'disabled'
        return form

    class Media:
        css = {
            'all': ('admin/css/role_admin.css',)
        }
        js = ('admin/js/role_admin.js',)

admin.site.register(Role, RoleAdmin)
