from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Employee, ITAsset, Department, Position, AssetType, OwnerCompany, Team, Role, Ticket, UserProfile

class EmployeeForm(forms.ModelForm):
    """Form for creating and updating Employee records."""
    
    class Meta:
        model = Employee
        fields = [
            'employee_id',
            'national_id',
            'first_name',
            'last_name',
            'email',
            'phone',
            'department',
            'position',
            'hire_date',
            'company',
            'employment_status',
            'retirement_date',
            'resignation_date',
            'training_start_date',
            'training_end_date',
        ]
        widgets = {
            'employee_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter employee ID (e.g., 9970)',
                'pattern': '^\d+$',
                'title': 'Employee ID must contain only numbers'
            }),
            'national_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter 14-digit national ID',
                'pattern': '^\d{14}$',
                'title': 'National ID must be exactly 14 digits'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter last name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email address'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number'
            }),
            'department': forms.Select(attrs={
                'class': 'form-select',
                'onchange': 'updatePositions(this.value)'
            }),
            'position': forms.Select(attrs={'class': 'form-select'}),
            'hire_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'company': forms.Select(attrs={'class': 'form-select'}),
            'employment_status': forms.Select(attrs={'class': 'form-select'}),
            'retirement_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'resignation_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'training_start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'training_end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all form fields
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect)):
                field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' form-control'
            if field.required:
                field.widget.attrs['required'] = 'required'
        
        # Update department choices
        self.fields['department'].queryset = Department.objects.all().order_by('name')
        self.fields['department'].empty_label = "Select Department"
        
        # Update position choices based on department
        if self.instance and self.instance.department:
            self.fields['position'].queryset = Position.objects.filter(
                department=self.instance.department
            ).order_by('name')
        else:
            self.fields['position'].queryset = Position.objects.none()
        self.fields['position'].empty_label = "Select Position"
        
        # Update company choices
        self.fields['company'].queryset = OwnerCompany.objects.all().order_by('name')
        self.fields['company'].empty_label = "Select Company"

        # Add JavaScript to handle employment status changes
        self.fields['employment_status'].widget.attrs.update({
            'onchange': 'handleEmploymentStatusChange(this.value)'
        })

    def clean(self):
        cleaned_data = super().clean()
        department = cleaned_data.get('department')
        position = cleaned_data.get('position')

        if department and position:
            if not Position.objects.filter(department=department, id=position.id).exists():
                self.add_error('position', 'Please select a valid position for the selected department.')

        employment_status = cleaned_data.get('employment_status')

        if employment_status == 'training':
            training_start_date = cleaned_data.get('training_start_date')
            training_end_date = cleaned_data.get('training_end_date')

            if not training_start_date:
                self.add_error('training_start_date', 'This field is required when employment status is "Training".')
            if not training_end_date:
                self.add_error('training_end_date', 'This field is required when employment status is "Training".')
            
            # Clear other date fields
            cleaned_data['hire_date'] = None
            cleaned_data['retirement_date'] = None
            cleaned_data['resignation_date'] = None

        elif employment_status == 'employed':
            hire_date = cleaned_data.get('hire_date')
            if not hire_date:
                self.add_error('hire_date', 'Hire date is required for employed status.')
            
            # Clear other date fields
            cleaned_data['retirement_date'] = None
            cleaned_data['resignation_date'] = None
            cleaned_data['training_start_date'] = None
            cleaned_data['training_end_date'] = None

        elif employment_status == 'terminated':
            resignation_date = cleaned_data.get('resignation_date')
            if not resignation_date:
                self.add_error('resignation_date', 'Resignation date is required for terminated status.')
            
            # Clear other date fields
            cleaned_data['retirement_date'] = None
            cleaned_data['training_start_date'] = None
            cleaned_data['training_end_date'] = None

        elif employment_status == 'on_leave':
            # Clear all date fields except hire_date
            cleaned_data['retirement_date'] = None
            cleaned_data['resignation_date'] = None
            cleaned_data['training_start_date'] = None
            cleaned_data['training_end_date'] = None

        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Employee.objects.exclude(pk=self.instance.pk if self.instance else None).filter(email=email).exists():
            raise forms.ValidationError('This email is already in use.')
        return email

    def clean_employee_id(self):
        employee_id = self.cleaned_data.get('employee_id')
        if not employee_id:
            raise forms.ValidationError('Employee ID is required.')
        if not employee_id.isdigit():
            raise forms.ValidationError('Employee ID must contain only numbers.')
        if Employee.objects.exclude(pk=self.instance.pk if self.instance else None).filter(employee_id=employee_id).exists():
            raise forms.ValidationError('This employee ID is already in use.')
        return employee_id

    def clean_national_id(self):
        national_id = self.cleaned_data.get('national_id')
        if not national_id.isdigit() or len(national_id) != 14:
            raise forms.ValidationError('National ID must be exactly 14 digits.')
        if Employee.objects.exclude(pk=self.instance.pk if self.instance else None).filter(national_id=national_id).exists():
            raise forms.ValidationError('This national ID is already in use.')
        return national_id

    def clean_department(self):
        department = self.cleaned_data.get('department')
        if not department:
            raise forms.ValidationError('Please select a department.')
        return department

    def clean_company(self):
        company = self.cleaned_data.get('company')
        if not company:
            raise forms.ValidationError('Please select a company.')
        return company

class ITAssetForm(forms.ModelForm):
    """Form for creating and updating ITAsset records."""
    
    class Meta:
        model = ITAsset
        fields = [
            # Basic Information
            'name',
            'asset_type',
            'serial_number',
            'model',
            'manufacturer',
            'owner',
            'purchase_date',
            'warranty_expiry',
            'status',
            'assigned_to',
            'notes',
            
            # Network Information
            'mac_address_wifi',
            'mac_address_ethernet',
            'ip_address',
            'delivery_letter_code',
            'receipt_date',
            
            # Computer Specifications
            'processor',
            'ram_size',
            'hdd1_capacity',
            'hdd2_capacity',
            'operating_system',
            'os_version',
            
            # Monitor Specifications
            'screen_size',
            'resolution',
            'refresh_rate',
            'panel_type',
            'vesa_mount',
            'built_in_speakers',
            
            # Printer Specifications
            'printer_type',
            'connection_type',
            'printer_department',
            'printer_responsible',
            'paper_size_support',
            'duplex_printing',
            'toner_cartridge_model',
            
            # UPS Specifications
            'ups_capacity',
            'ups_battery_count',
            'ups_battery_life',
            'ups_battery_replacement_date',
            'ups_manufacturer',
        ]
        widgets = {
            # Basic Information
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'asset_type': forms.Select(attrs={'class': 'form-select'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control'}),
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'manufacturer': forms.TextInput(attrs={'class': 'form-control'}),
            'owner': forms.Select(attrs={'class': 'form-select'}),
            'purchase_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'warranty_expiry': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            
            # Network Information
            'mac_address_wifi': forms.TextInput(attrs={'class': 'form-control'}),
            'mac_address_ethernet': forms.TextInput(attrs={'class': 'form-control'}),
            'ip_address': forms.TextInput(attrs={'class': 'form-control'}),
            'delivery_letter_code': forms.TextInput(attrs={'class': 'form-control'}),
            'receipt_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            
            # Computer Specifications
            'processor': forms.TextInput(attrs={'class': 'form-control'}),
            'ram_size': forms.TextInput(attrs={'class': 'form-control'}),
            'hdd1_capacity': forms.TextInput(attrs={'class': 'form-control'}),
            'hdd2_capacity': forms.TextInput(attrs={'class': 'form-control'}),
            'operating_system': forms.TextInput(attrs={'class': 'form-control'}),
            'os_version': forms.TextInput(attrs={'class': 'form-control'}),
            
            # Monitor Specifications
            'screen_size': forms.TextInput(attrs={'class': 'form-control'}),
            'resolution': forms.TextInput(attrs={'class': 'form-control'}),
            'refresh_rate': forms.TextInput(attrs={'class': 'form-control'}),
            'panel_type': forms.TextInput(attrs={'class': 'form-control'}),
            'vesa_mount': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'built_in_speakers': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            
            # Printer Specifications
            'printer_type': forms.TextInput(attrs={'class': 'form-control'}),
            'connection_type': forms.TextInput(attrs={'class': 'form-control'}),
            'printer_department': forms.TextInput(attrs={'class': 'form-control'}),
            'printer_responsible': forms.TextInput(attrs={'class': 'form-control'}),
            'paper_size_support': forms.TextInput(attrs={'class': 'form-control'}),
            'duplex_printing': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'toner_cartridge_model': forms.TextInput(attrs={'class': 'form-control'}),
            
            # UPS Specifications
            'ups_capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'ups_battery_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'ups_battery_life': forms.NumberInput(attrs={'class': 'form-control'}),
            'ups_battery_replacement_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'ups_manufacturer': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data 

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=False)
    confirm_password = forms.CharField(widget=forms.PasswordInput(), required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:  # If creating new user
            self.fields['password'].required = True
            self.fields['confirm_password'].required = True

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords don't match")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data.get('password'):
            user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class UserProfileForm(forms.ModelForm):
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.none(),  # Will be populated in __init__
        required=False,
        label="Assign to Employee",
        help_text="Optional: assign this user to an existing employee profile.",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = UserProfile
        fields = ['role', 'department', 'team']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'team': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Get employees that don't have a user yet
        unassigned_employees = Employee.objects.filter(user__isnull=True)
        
        current_employee = None
        # Only check for an existing employee if we are updating a saved profile
        if self.instance and self.instance.pk:
            if hasattr(self.instance.user, 'employee_profile'):
                current_employee = self.instance.user.employee_profile

        if current_employee:
            # Combine unassigned employees with the current employee
            self.fields['employee'].queryset = unassigned_employees | Employee.objects.filter(pk=current_employee.pk)
            # Set the initial value for the employee field
            self.fields['employee'].initial = current_employee
        else:
            self.fields['employee'].queryset = unassigned_employees

class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['subject', 'content', 'asset', 'employee']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'asset': forms.Select(attrs={'class': 'form-select'}),
            'employee': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter employees to show only employed ones
        self.fields['employee'].queryset = Employee.objects.filter(employment_status='employed').order_by('first_name', 'last_name')
        self.fields['employee'].empty_label = "Select Employee"
        
        # Filter assets to show only available ones
        self.fields['asset'].queryset = ITAsset.objects.filter(status='available').order_by('name')
        self.fields['asset'].empty_label = "Select Asset"

class AssetTypeForm(forms.ModelForm):
    class Meta:
        model = AssetType
        fields = ['name', 'display_name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'display_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class DepartmentForm(forms.ModelForm):
    positions = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': '3',
            'placeholder': 'Enter positions (one per line)'
        }),
        required=False,
        help_text='Enter positions for this department, one per line'
    )

    class Meta:
        model = Department
        fields = ['name', 'description', 'positions']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': '3'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            # Get existing positions for this department
            positions = Position.objects.filter(department=self.instance).order_by('name')
            self.fields['positions'].initial = '\n'.join(p.name for p in positions)

    def save(self, commit=True):
        department = super().save(commit=False)
        if commit:
            department.save()
            # Update positions
            if 'positions' in self.cleaned_data:
                # Delete existing positions
                Position.objects.filter(department=department).delete()
                # Create new positions
                positions_text = self.cleaned_data['positions'].strip()
                if positions_text:
                    for position_name in positions_text.split('\n'):
                        position_name = position_name.strip()
                        if position_name:
                            Position.objects.create(
                                name=position_name,
                                department=department
                            )
        return department

class CompanyForm(forms.ModelForm):
    class Meta:
        model = OwnerCompany
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'department', 'manager', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter team name'
            }),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'manager': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter team description',
                'rows': 3
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all form fields
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect)):
                field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' form-control'
            if field.required:
                field.widget.attrs['required'] = 'required'
        
        # Update department choices
        self.fields['department'].queryset = Department.objects.all().order_by('name')
        self.fields['department'].empty_label = "Select Department"
        
        # Update manager choices to only show employed employees
        self.fields['manager'].queryset = Employee.objects.filter(
            employment_status=Employee.STATUS_EMPLOYED
        ).order_by('first_name', 'last_name')
        self.fields['manager'].empty_label = "Select Team Manager" 