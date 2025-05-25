# inventory/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Employee, ITAsset, Department, Position, AssetType, OwnerCompany, AssetHistory, Team, User, Role, Message
from .forms import EmployeeForm, ITAssetForm, UserForm, UserProfileForm, RoleForm, MessageForm
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
import openpyxl
from openpyxl import Workbook
from datetime import datetime, timedelta
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
import json
import time

@login_required
def home(request):
    # Get total counts
    total_assets = ITAsset.objects.count()
    total_employees = Employee.objects.count()
    available_assets = ITAsset.objects.filter(status='available').count()
    assigned_assets = ITAsset.objects.filter(status='assigned').count()
    maintenance_assets = ITAsset.objects.filter(status='maintenance').count()
    retired_assets = ITAsset.objects.filter(status='retired').count()

    # Get asset type distribution
    asset_types = AssetType.objects.all()
    asset_type_distribution = []
    for asset_type in asset_types:
        count = ITAsset.objects.filter(asset_type=asset_type).count()
        asset_type_distribution.append({
            'name': asset_type.display_name,
            'count': count
        })

    # Get owner company distribution
    owner_companies = OwnerCompany.objects.all()
    owner_company_distribution = []
    for company in owner_companies:
        count = ITAsset.objects.filter(owner=company).count()
        owner_company_distribution.append({
            'name': company.name,
            'count': count
        })

    # Get recent assets
    recent_assets = ITAsset.objects.select_related('asset_type', 'owner', 'assigned_to').order_by('-id')[:5]

    # Get assets with expiring warranty (within 3 months)
    today = datetime.now().date()
    three_months_later = today + timedelta(days=90)
    expiring_warranty_assets = ITAsset.objects.filter(
        warranty_expiry__gte=today,
        warranty_expiry__lte=three_months_later
    ).select_related('asset_type', 'owner', 'assigned_to')

    # Get recent asset history
    recent_history = AssetHistory.objects.select_related('asset', 'assigned_to').order_by('-date')[:5]

    context = {
        'total_assets': total_assets,
        'total_employees': total_employees,
        'available_assets': available_assets,
        'assigned_assets': assigned_assets,
        'maintenance_assets': maintenance_assets,
        'retired_assets': retired_assets,
        'asset_type_distribution': asset_type_distribution,
        'owner_company_distribution': owner_company_distribution,
        'recent_assets': recent_assets,
        'expiring_warranty_assets': expiring_warranty_assets,
        'recent_history': recent_history,
    }
    return render(request, 'inventory/home.html', context)

@login_required
def employee_list(request):
    # Get search and filter parameters
    search_query = request.GET.get('search', '')
    department_id = request.GET.get('department', '')
    company_id = request.GET.get('company', '')
    
    # Start with all employees
    employees = Employee.objects.all()
    
    # Apply search filter if provided
    if search_query:
        employees = employees.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(employee_id__icontains=search_query) |
            Q(national_id__icontains=search_query)  # Add national_id to search
        )
    
    # Apply department filter if provided
    if department_id:
        employees = employees.filter(department_id=department_id)
    
    # Apply company filter if provided
    if company_id:
        employees = employees.filter(company_id=company_id)
    
    # Get all departments for filter dropdown
    departments = Department.objects.all()
    
    # Get all companies for filter dropdown
    companies = OwnerCompany.objects.all()
    
    # Paginate the results
    paginator = Paginator(employees, 10)  # Show 10 employees per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Get the current page number
    current_page = page_obj.number
    total_pages = paginator.num_pages
    
    # Calculate the range of page numbers to show
    if total_pages <= 5:
        page_range = range(1, total_pages + 1)
    else:
        if current_page <= 3:
            page_range = range(1, 6)
        elif current_page >= total_pages - 2:
            page_range = range(total_pages - 4, total_pages + 1)
        else:
            page_range = range(current_page - 2, current_page + 3)
    
    context = {
        'employees': page_obj,
        'departments': departments,
        'companies': companies,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
        'page_range': page_range,
        'current_page': current_page,
        'total_pages': total_pages,
    }
    
    return render(request, 'inventory/employee_list.html', context)

@login_required
def employee_create(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            employee = form.save()
            messages.success(request, f'Employee "{employee.get_full_name()}" was successfully created.')
            return redirect('inventory:employee_detail', pk=employee.pk)
    else:
        form = EmployeeForm()
    
    return render(request, 'inventory/employee_form.html', {'form': form})

@login_required
def employee_detail(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    return render(request, 'inventory/employee_detail.html', {'employee': employee})

@login_required
def employee_update(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            employee = form.save()
            messages.success(request, f'Employee "{employee.get_full_name()}" was successfully updated.')
            return redirect('inventory:employee_detail', pk=employee.pk)
    else:
        form = EmployeeForm(instance=employee)
    
    return render(request, 'inventory/employee_form.html', {'form': form, 'employee': employee})

@login_required
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    
    if request.method == 'POST':
        employee_name = employee.get_full_name()
        employee.delete()
        messages.success(request, f'Employee "{employee_name}" was successfully deleted.')
        return redirect('inventory:employee_list')
    
    return render(request, 'inventory/employee_confirm_delete.html', {'employee': employee})

@login_required
def employee_toggle_status(request, pk):
    """Toggle employee's active status."""
    employee = get_object_or_404(Employee, pk=pk)
    
    if request.method == 'POST':
        employee.is_active = not employee.is_active
        employee.save()
        
        status = 'activated' if employee.is_active else 'deactivated'
        messages.success(request, f'Employee "{employee.get_full_name()}" has been {status}.')
    
    return redirect('inventory:employee_detail', pk=employee.pk)

@login_required
def asset_assign(request):
    """View for assigning assets to employees."""
    if request.method == 'POST':
        asset_id = request.POST.get('asset')
        employee_id = request.POST.get('employee')
        
        try:
            asset = ITAsset.objects.get(pk=asset_id)
            employee = Employee.objects.get(pk=employee_id)
            
            asset.assigned_to = employee
            asset.status = 'assigned'
            asset.save()
            
            messages.success(request, f'Asset "{asset.name}" has been assigned to {employee.get_full_name()}.')
            return redirect('inventory:employee_detail', pk=employee.pk)
        except (ITAsset.DoesNotExist, Employee.DoesNotExist):
            messages.error(request, 'Invalid asset or employee selected.')
            return redirect('inventory:employee_list')
    
    # Get the employee from the query parameter
    employee_id = request.GET.get('employee')
    if employee_id:
        try:
            employee = Employee.objects.get(pk=employee_id)
        except Employee.DoesNotExist:
            messages.error(request, 'Employee not found.')
            return redirect('inventory:employee_list')
    else:
        employee = None
    
    # Get available assets
    available_assets = ITAsset.objects.filter(status='available')
    
    context = {
        'employee': employee,
        'available_assets': available_assets,
    }
    
    return render(request, 'inventory/asset_assign.html', context)

class ITAssetListView(LoginRequiredMixin, ListView):
    model = ITAsset
    template_name = 'inventory/asset_list.html'
    context_object_name = 'assets'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Get filter parameters
        search_query = self.request.GET.get('search', '')
        asset_type = self.request.GET.get('asset_type', '')
        status = self.request.GET.get('status', '')
        manufacturer = self.request.GET.get('manufacturer', '')
        
        # Apply search filter
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(serial_number__icontains=search_query) |
                Q(model__icontains=search_query) |
                Q(delivery_letter_code__icontains=search_query)
            )
        
        # Apply asset type filter
        if asset_type:
            queryset = queryset.filter(asset_type_id=asset_type)
        
        # Apply status filter
        if status:
            queryset = queryset.filter(status=status)
        
        # Apply manufacturer filter
        if manufacturer:
            queryset = queryset.filter(manufacturer=manufacturer)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['asset_types'] = AssetType.objects.all()
        context['status_choices'] = ITAsset.STATUS_CHOICES
        context['manufacturers'] = ITAsset.objects.exclude(manufacturer='').values_list('manufacturer', flat=True).distinct()
        return context

class ITAssetDetailView(LoginRequiredMixin, DetailView):
    model = ITAsset
    template_name = 'inventory/asset_detail.html'
    context_object_name = 'asset'

class ITAssetCreateView(LoginRequiredMixin, CreateView):
    model = ITAsset
    form_class = ITAssetForm
    template_name = 'inventory/asset_form.html'
    success_url = reverse_lazy('inventory:asset_list')

    def form_valid(self, form):
        messages.success(self.request, 'IT Asset created successfully.')
        return super().form_valid(form)

class ITAssetUpdateView(LoginRequiredMixin, UpdateView):
    model = ITAsset
    form_class = ITAssetForm
    template_name = 'inventory/asset_form.html'
    success_url = reverse_lazy('inventory:asset_list')

    def form_valid(self, form):
        messages.success(self.request, 'IT Asset updated successfully.')
        return super().form_valid(form)

class ITAssetDeleteView(LoginRequiredMixin, DeleteView):
    model = ITAsset
    template_name = 'inventory/asset_confirm_delete.html'
    success_url = reverse_lazy('inventory:asset_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'IT Asset deleted successfully.')
        return super().delete(request, *args, **kwargs)

@login_required
def employee_upload(request):
    if request.method == 'POST':
        excel_file = request.FILES.get('excel_file')
        if excel_file:
            try:
                wb = openpyxl.load_workbook(excel_file)
                ws = wb.active
                
                # Skip header row
                for row in ws.iter_rows(min_row=2):
                    try:
                        # Get or create department first
                        department_name = row[5].value
                        if department_name:
                            department, _ = Department.objects.get_or_create(name=department_name)
                            
                            # Get or create position with department
                            position_name = row[6].value
                            if position_name:
                                position, _ = Position.objects.get_or_create(
                                    name=position_name,
                                    department=department  # Set the department for the position
                                )
                            else:
                                position = None
                        else:
                            department = None
                            position = None
                        
                        # Get company
                        company_name = row[7].value
                        try:
                            company = OwnerCompany.objects.get(name=company_name)
                        except OwnerCompany.DoesNotExist:
                            messages.error(request, f'Row {row[0].row}: Company "{company_name}" not found. Please create it first.')
                            continue
                        
                        # Create employee
                        employee = Employee(
                            employee_id=row[0].value,
                            national_id=row[1].value,
                            first_name=row[2].value,
                            last_name=row[3].value,
                            email=row[4].value,
                            department=department,
                            position=position,
                            company=company,  # Use the company object
                            hire_date=row[8].value
                        )
                        employee.save()
                    except Exception as e:
                        messages.error(request, f'Error processing row: {str(e)}')
                        continue
                
                messages.success(request, 'Employees uploaded successfully!')
                return redirect('inventory:employee_list')
            except Exception as e:
                messages.error(request, f'Error uploading file: {str(e)}')
    
    return render(request, 'inventory/employee_upload.html')

@login_required
def download_employee_template(request):
    wb = Workbook()
    ws = wb.active
    
    # Add headers
    headers = [
        'Employee ID *',
        'National ID *',
        'First Name *',
        'Last Name *',
        'Email *',
        'Department *',
        'Position *',
        'Company *',
        'Hire Date *'
    ]
    ws.append(headers)
    
    # Add example row
    example = [
        'EMP001',
        '12345678901234',
        'John',
        'Doe',
        'john.doe@example.com',
        'IT',
        'Software Engineer',
        'CTP',
        '2024-01-01'
    ]
    ws.append(example)
    
    # Add available departments
    departments = Department.objects.all()
    if departments.exists():
        ws.append([])  # Add empty row
        ws.append(['Available Departments:'])
        for dept in departments:
            ws.append([dept.get_name_display()])
    
    # Add available companies
    companies = OwnerCompany.objects.all()
    if companies.exists():
        ws.append([])  # Add empty row
        ws.append(['Available Companies:'])
        for company in companies:
            ws.append([company.name])
    
    # Style the header row
    for cell in ws[1]:
        cell.font = openpyxl.styles.Font(bold=True)
    
    # Style the sections headers
    if departments.exists():
        dept_header = ws.cell(row=4, column=1)
        dept_header.font = openpyxl.styles.Font(bold=True)
    
    if companies.exists():
        company_header = ws.cell(row=departments.count() + 6, column=1)
        company_header.font = openpyxl.styles.Font(bold=True)
    
    # Add data validation for company column
    company_validation = DataValidation(type="list", formula1=f'"{",".join(companies.values_list("name", flat=True))}"')
    company_validation.add(f'H2:H{len(example) + 1}')
    ws.add_data_validation(company_validation)
    
    # Add data validation for department column
    department_validation = DataValidation(type="list", formula1=f'"{",".join(departments.values_list("name", flat=True))}"')
    department_validation.add(f'F2:F{len(example) + 1}')
    ws.add_data_validation(department_validation)
    
    # Adjust column widths
    for column in ws.columns:
        max_length = 0
        column_letter = get_column_letter(column[0].column)
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column_letter].width = adjusted_width
    
    # Create response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=employee_template.xlsx'
    
    wb.save(response)
    return response

@login_required
def download_employee_data(request):
    wb = Workbook()
    ws = wb.active
    
    # Add headers
    headers = [
        'Employee ID',
        'National ID',
        'First Name',
        'Last Name',
        'Email',
        'Department',
        'Position',
        'Company',
        'Hire Date'
    ]
    ws.append(headers)
    
    # Add employee data
    employees = Employee.objects.all()
    for employee in employees:
        row = [
            employee.employee_id,
            employee.national_id,
            employee.first_name,
            employee.last_name,
            employee.email,
            str(employee.department) if employee.department else '',
            str(employee.position) if employee.position else '',
            str(employee.company.name) if employee.company else '',  # Convert company to string
            employee.hire_date
        ]
        ws.append(row)
    
    # Style the header row
    for cell in ws[1]:
        cell.font = openpyxl.styles.Font(bold=True)
    
    # Adjust column widths
    for column in ws.columns:
        max_length = 0
        column_letter = get_column_letter(column[0].column)
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column_letter].width = adjusted_width
    
    # Create response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=employees.xlsx'
    
    wb.save(response)
    return response

@login_required
def download_asset_template(request):
    wb = Workbook()
    ws = wb.active
    
    # Add headers
    headers = [
        'Asset Name *',
        'Asset Type *',
        'Serial Number *',
        'Model *',
        'Manufacturer',
        'Owner Company *',
        'Assigned Employee ID',
        'Wi-Fi MAC Address',
        'Ethernet MAC Address *',
        'Delivery Letter Code',
        'Purchase Date',
        'Receipt Date',
        'Warranty Expiry',
        'Status *'  # Added status field
    ]
    ws.append(headers)
    
    # Add example row
    example = [
        'Laptop-001',
        'laptop',  # Use the internal name, not display name
        'SN123456',
        'ThinkPad X1',
        'Lenovo',
        'CTP',  # Company name
        'EMP001',  # Employee ID
        '00:1A:2B:3C:4D:5E',
        '00:1A:2B:3C:4D:5F',
        'DL-2024-001',
        '2024-01-01',
        '2024-01-15',
        '2027-01-01',
        'available'  # Default status
    ]
    ws.append(example)
    
    # Add available asset types
    ws.append([])  # Add empty row
    ws.append(['Available Asset Types:'])
    ws.append(['Internal Name - Display Name'])
    for asset_type in AssetType.objects.all().order_by('name'):
        ws.append([f'{asset_type.name} - {asset_type.display_name}'])
    
    # Add available statuses
    ws.append([])  # Add empty row
    ws.append(['Available Statuses:'])
    ws.append(['Internal Name - Display Name'])
    for status_code, status_name in ITAsset.STATUS_CHOICES:
        ws.append([f'{status_code} - {status_name}'])
    
    # Add owner companies section
    ws.append([])  # Add empty row
    ws.append(['Owner Companies:'])
    for company in OwnerCompany.objects.all().order_by('name'):
        ws.append([company.name])
    
    # Add available employees section
    ws.append([])  # Add empty row
    ws.append(['Available Employees:'])
    ws.append(['Format: Employee ID - Full Name (Company)'])
    ws.append([])
    
    # Group employees by company
    for company in OwnerCompany.objects.all():
        ws.append([f'--- {company.name} Employees ---'])
        employees = Employee.objects.filter(
            is_active=True,
            company=company
        ).order_by('employee_id')
        
        for employee in employees:
            ws.append([f"{employee.employee_id} - {employee.get_full_name()} ({company.name})"])
        ws.append([])  # Add empty row between companies
    
    # Style the header row
    for cell in ws[1]:
        cell.font = openpyxl.styles.Font(bold=True)
    
    # Style the sections headers
    ws.cell(row=4, column=1).font = openpyxl.styles.Font(bold=True)
    ws.cell(row=5, column=1).font = openpyxl.styles.Font(italic=True)  # Style the "Internal Name - Display Name" row
    
    # Find and style other section headers
    for row in range(1, ws.max_row + 1):
        cell = ws.cell(row=row, column=1)
        if cell.value in ['Owner Companies:', 'Available Employees:', 'Available Statuses:'] or \
           (cell.value and isinstance(cell.value, str) and cell.value.startswith('---')):
            cell.font = openpyxl.styles.Font(bold=True)
    
    # Add data validation for asset type column
    asset_types = AssetType.objects.all()
    if asset_types.exists():
        asset_type_validation = DataValidation(
            type="list",
            formula1=f'"{",".join(asset_types.values_list("name", flat=True))}"'
        )
        asset_type_validation.add(f'B2:B{len(example) + 1}')
        ws.add_data_validation(asset_type_validation)
    
    # Add data validation for company column
    companies = OwnerCompany.objects.all()
    if companies.exists():
        company_validation = DataValidation(
            type="list",
            formula1=f'"{",".join(companies.values_list("name", flat=True))}"'
        )
        company_validation.add(f'F2:F{len(example) + 1}')
        ws.add_data_validation(company_validation)
    
    # Add data validation for status column
    status_validation = DataValidation(
        type="list",
        formula1=f'"{",".join([status[0] for status in ITAsset.STATUS_CHOICES])}"'
    )
    status_validation.add(f'N2:N{len(example) + 1}')
    ws.add_data_validation(status_validation)
    
    # Adjust column widths
    for column in ws.columns:
        max_length = 0
        column_letter = get_column_letter(column[0].column)
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column_letter].width = adjusted_width
    
    # Create response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=asset_template.xlsx'
    
    wb.save(response)
    return response

@login_required
def asset_upload(request):
    if request.method == 'POST':
        excel_file = request.FILES.get('excel_file')
        if excel_file:
            try:
                wb = openpyxl.load_workbook(excel_file)
                ws = wb.active
                
                # Skip header row
                for row in ws.iter_rows(min_row=2):
                    try:
                        # Check required fields
                        required_fields = {
                            'name': row[0].value,
                            'asset_type': row[1].value,
                            'serial_number': row[2].value,
                            'model': row[3].value,
                            'owner_company': row[5].value,
                            'mac_address_ethernet': row[8].value,
                            'status': row[13].value  # Added status field
                        }
                        
                        # Validate required fields
                        missing_fields = [field for field, value in required_fields.items() if not value]
                        if missing_fields:
                            messages.error(request, f'Row {row[0].row}: Missing required fields: {", ".join(missing_fields)}')
                            continue

                        # Get or create asset type
                        asset_type_name = row[1].value
                        try:
                            asset_type = AssetType.objects.get(name__iexact=asset_type_name)
                        except AssetType.DoesNotExist:
                            messages.error(request, f'Row {row[0].row}: Asset Type "{asset_type_name}" not found. Please create it first.')
                            continue

                        # Get the owner company
                        owner_company_name = row[5].value
                        try:
                            owner_company = OwnerCompany.objects.get(name__iexact=owner_company_name)
                        except OwnerCompany.DoesNotExist:
                            messages.error(request, f'Row {row[0].row}: Owner Company "{owner_company_name}" not found. Please create it first.')
                            continue

                        # Validate status
                        status = row[13].value
                        if status not in dict(ITAsset.STATUS_CHOICES):
                            messages.error(request, f'Row {row[0].row}: Invalid status "{status}". Please use one of the available statuses.')
                            continue

                        # Get the assigned employee if provided
                        assigned_employee_id = row[6].value
                        assigned_employee = None
                        if assigned_employee_id:
                            try:
                                assigned_employee = Employee.objects.get(employee_id=assigned_employee_id)
                                # Verify employee belongs to the owner company
                                if assigned_employee.company != owner_company:
                                    messages.error(request, f'Row {row[0].row}: Employee {assigned_employee_id} does not belong to {owner_company_name}. Please assign an employee from the correct company.')
                                    continue
                            except Employee.DoesNotExist:
                                messages.error(request, f'Row {row[0].row}: Employee with ID {assigned_employee_id} not found. Please use a valid employee ID.')
                                continue
                        
                        # Create asset
                        asset = ITAsset(
                            name=row[0].value,
                            asset_type=asset_type,
                            serial_number=row[2].value,
                            model=row[3].value,
                            manufacturer=row[4].value,
                            owner=owner_company,
                            assigned_to=assigned_employee,
                            mac_address_wifi=row[7].value,
                            mac_address_ethernet=row[8].value,
                            delivery_letter_code=row[9].value,
                            status=status,  # Use the provided status
                            purchase_date=row[10].value,
                            receipt_date=row[11].value,
                            warranty_expiry=row[12].value
                        )
                        asset.save()
                        messages.success(request, f'Row {row[0].row}: Asset "{asset.name}" created successfully.')
                    except Exception as e:
                        messages.error(request, f'Row {row[0].row}: Error processing row: {str(e)}')
                        continue
                
                return redirect('inventory:asset_list')
            except Exception as e:
                messages.error(request, f'Error uploading file: {str(e)}')
    
    return render(request, 'inventory/asset_upload.html')

@login_required
def download_asset_data(request):
    wb = Workbook()
    ws = wb.active
    
    # Add headers
    headers = [
        'Asset Name',
        'Asset Type',
        'Serial Number',
        'Model',
        'Manufacturer',
        'Owner',
        'Wi-Fi MAC Address',
        'Ethernet MAC Address',
        'Delivery Letter Code',
        'Status',
        'Purchase Date',
        'Receipt Date',
        'Warranty Expiry'
    ]
    ws.append(headers)
    
    # Get filtered queryset using the same filters as the list view
    assets = ITAsset.objects.all()
    
    # Apply search filter
    search_query = request.GET.get('search', '')
    if search_query:
        assets = assets.filter(
            Q(name__icontains=search_query) |
            Q(serial_number__icontains=search_query) |
            Q(model__icontains=search_query) |
            Q(delivery_letter_code__icontains=search_query)
        )
    
    # Apply other filters
    asset_type = request.GET.get('asset_type', '')
    if asset_type:
        assets = assets.filter(asset_type_id=asset_type)
    
    status = request.GET.get('status', '')
    if status:
        assets = assets.filter(status=status)
    
    manufacturer = request.GET.get('manufacturer', '')
    if manufacturer:
        assets = assets.filter(manufacturer=manufacturer)
    
    # Add asset data
    for asset in assets:
        row = [
            asset.name,
            asset.asset_type.name,  # Use the internal name for consistency
            asset.serial_number,
            asset.model,
            asset.manufacturer,
            f"{asset.assigned_to.get_full_name()} ({asset.assigned_to.company})" if asset.assigned_to else '',
            asset.mac_address_wifi,
            asset.mac_address_ethernet,
            asset.delivery_letter_code,
            asset.status,  # Use the internal status value for consistency
            asset.purchase_date,
            asset.receipt_date,
            asset.warranty_expiry
        ]
        ws.append(row)
    
    # Style the header row
    for cell in ws[1]:
        cell.font = openpyxl.styles.Font(bold=True)
    
    # Adjust column widths
    for column in ws.columns:
        max_length = 0
        column_letter = get_column_letter(column[0].column)
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column_letter].width = adjusted_width
    
    # Create response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=assets.xlsx'
    
    wb.save(response)
    return response

# Asset Type Views
class AssetTypeListView(LoginRequiredMixin, ListView):
    model = AssetType
    template_name = 'inventory/asset_type_list.html'
    context_object_name = 'asset_types'

class AssetTypeCreateView(LoginRequiredMixin, CreateView):
    model = AssetType
    template_name = 'inventory/asset_type_form.html'
    fields = ['name', 'display_name']
    success_url = reverse_lazy('inventory:asset_type_list')

    def form_valid(self, form):
        messages.success(self.request, 'Asset Type created successfully.')
        return super().form_valid(form)

class AssetTypeUpdateView(LoginRequiredMixin, UpdateView):
    model = AssetType
    template_name = 'inventory/asset_type_form.html'
    fields = ['name', 'display_name']
    success_url = reverse_lazy('inventory:asset_type_list')

    def form_valid(self, form):
        messages.success(self.request, 'Asset Type updated successfully.')
        return super().form_valid(form)

class AssetTypeDeleteView(LoginRequiredMixin, DeleteView):
    model = AssetType
    template_name = 'inventory/asset_type_confirm_delete.html'
    success_url = reverse_lazy('inventory:asset_type_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Asset Type deleted successfully.')
        return super().delete(request, *args, **kwargs)

# Owner Company Views
class OwnerCompanyListView(LoginRequiredMixin, ListView):
    model = OwnerCompany
    template_name = 'inventory/owner_company_list.html'
    context_object_name = 'companies'

class OwnerCompanyCreateView(LoginRequiredMixin, CreateView):
    model = OwnerCompany
    template_name = 'inventory/owner_company_form.html'
    fields = ['name']
    success_url = reverse_lazy('inventory:owner_company_list')

    def form_valid(self, form):
        # Generate code from name: lowercase and replace multiple spaces with single underscore
        name = form.cleaned_data['name']
        code = '_'.join(name.lower().split())
        
        # Limit code to 20 characters
        if len(code) > 20:
            code = code[:20]
        
        # Set the code before saving
        form.instance.code = code
        
        messages.success(self.request, 'Owner Company created successfully.')
        return super().form_valid(form)

class OwnerCompanyUpdateView(LoginRequiredMixin, UpdateView):
    model = OwnerCompany
    template_name = 'inventory/owner_company_form.html'
    fields = ['name']
    success_url = reverse_lazy('inventory:owner_company_list')

    def form_valid(self, form):
        # Generate code from name: lowercase and replace multiple spaces with single underscore
        name = form.cleaned_data['name']
        code = '_'.join(name.lower().split())
        
        # Limit code to 20 characters
        if len(code) > 20:
            code = code[:20]
        
        # Set the code before saving
        form.instance.code = code
        
        messages.success(self.request, 'Owner Company updated successfully.')
        return super().form_valid(form)

class OwnerCompanyDeleteView(LoginRequiredMixin, DeleteView):
    model = OwnerCompany
    template_name = 'inventory/owner_company_confirm_delete.html'
    success_url = reverse_lazy('inventory:owner_company_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Owner Company deleted successfully.')
        return super().delete(request, *args, **kwargs)

# Department Views
class DepartmentListView(LoginRequiredMixin, ListView):
    model = Department
    template_name = 'inventory/department_list.html'
    context_object_name = 'departments'

class DepartmentCreateView(LoginRequiredMixin, CreateView):
    model = Department
    template_name = 'inventory/department_form.html'
    fields = ['name', 'description']
    success_url = reverse_lazy('inventory:department_list')

    def form_valid(self, form):
        messages.success(self.request, 'Department created successfully.')
        return super().form_valid(form)

class DepartmentUpdateView(LoginRequiredMixin, UpdateView):
    model = Department
    template_name = 'inventory/department_form.html'
    fields = ['name', 'description']
    success_url = reverse_lazy('inventory:department_list')

    def form_valid(self, form):
        messages.success(self.request, 'Department updated successfully.')
        return super().form_valid(form)

class DepartmentDeleteView(LoginRequiredMixin, DeleteView):
    model = Department
    template_name = 'inventory/department_confirm_delete.html'
    success_url = reverse_lazy('inventory:department_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Department deleted successfully.')
        return super().delete(request, *args, **kwargs)

class AssetHistoryListView(LoginRequiredMixin, ListView):
    model = AssetHistory
    template_name = 'inventory/asset_history.html'
    context_object_name = 'history_entries'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().select_related('asset', 'assigned_to')
        
        # Get filter parameters
        search_query = self.request.GET.get('search', '')
        status = self.request.GET.get('status', '')
        
        # Apply search filter
        if search_query:
            queryset = queryset.filter(
                Q(asset__name__icontains=search_query) |
                Q(asset__serial_number__icontains=search_query) |
                Q(assigned_to__first_name__icontains=search_query) |
                Q(assigned_to__last_name__icontains=search_query)
            )
        
        # Apply status filter
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = ITAsset.STATUS_CHOICES
        return context

# Team Views
class TeamListView(LoginRequiredMixin, ListView):
    model = Team
    template_name = 'inventory/team_list.html'
    context_object_name = 'teams'

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(department__name__icontains=search_query) |
                Q(manager__first_name__icontains=search_query) |
                Q(manager__last_name__icontains=search_query)
            )
        return queryset.select_related('department', 'manager')

class TeamCreateView(LoginRequiredMixin, CreateView):
    model = Team
    template_name = 'inventory/team_form.html'
    fields = ['name', 'department', 'manager', 'description']
    success_url = reverse_lazy('inventory:team_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['manager'].queryset = Employee.objects.filter(is_active=True)
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['available_employees'] = Employee.objects.filter(is_active=True)
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        # Handle team members
        team_members = self.request.POST.getlist('team_members')
        if team_members:
            employees = Employee.objects.filter(id__in=team_members)
            for employee in employees:
                employee.team = form.instance
                employee.save()
        return response

class TeamUpdateView(LoginRequiredMixin, UpdateView):
    model = Team
    template_name = 'inventory/team_form.html'
    fields = ['name', 'department', 'manager', 'description']
    success_url = reverse_lazy('inventory:team_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['manager'].queryset = Employee.objects.filter(is_active=True)
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['available_employees'] = Employee.objects.filter(
            is_active=True,
            department=self.object.department
        )
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        # Handle team members
        team_members = self.request.POST.getlist('team_members')
        
        # Remove all current members
        Employee.objects.filter(team=form.instance).update(team=None)
        
        # Add selected members
        if team_members:
            employees = Employee.objects.filter(id__in=team_members)
            for employee in employees:
                employee.team = form.instance
                employee.save()
        return response

class TeamDeleteView(LoginRequiredMixin, DeleteView):
    model = Team
    template_name = 'inventory/team_confirm_delete.html'
    success_url = reverse_lazy('inventory:team_list')

    def delete(self, request, *args, **kwargs):
        team = self.get_object()
        # Update all team members to remove team association
        Employee.objects.filter(team=team).update(team=None)
        return super().delete(request, *args, **kwargs)

class TeamDetailView(LoginRequiredMixin, DetailView):
    model = Team
    template_name = 'inventory/team_detail.html'
    context_object_name = 'team'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['members'] = self.object.members.all().select_related('department', 'company')
        context['available_employees'] = Employee.objects.filter(
            is_active=True,
            department=self.object.department,
            team__isnull=True
        ).select_related('department', 'company')
        
        # Check if user has an employee profile before accessing it
        try:
            context['is_manager'] = self.object.manager == self.request.user.employee_profile
        except:
            context['is_manager'] = False
            
        return context

@login_required
def add_team_member(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    
    # Check if user is the team manager
    if request.user.employee_profile != team.manager:
        messages.error(request, 'Only the team manager can add members.')
        return redirect('inventory:team_detail', pk=team_id)
    
    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        if employee_id:
            employee = get_object_or_404(Employee, id=employee_id)
            if employee.department == team.department:
                employee.team = team
                employee.save()
                messages.success(request, f'{employee.get_full_name()} has been added to the team.')
            else:
                messages.error(request, 'Employee must be from the same department as the team.')
    return redirect('inventory:team_detail', pk=team_id)

@login_required
def remove_team_member(request, team_id, employee_id):
    team = get_object_or_404(Team, id=team_id)
    
    # Check if user is the team manager
    if request.user.employee_profile != team.manager:
        messages.error(request, 'Only the team manager can remove members.')
        return redirect('inventory:team_detail', pk=team_id)
    
    employee = get_object_or_404(Employee, id=employee_id)
    if employee.team == team:
        employee.team = None
        employee.save()
        messages.success(request, f'{employee.get_full_name()} has been removed from the team.')
    return redirect('inventory:team_detail', pk=team_id)

@login_required
def my_teams(request):
    """View for team managers to see their teams."""
    managed_teams = Team.objects.filter(manager=request.user.employee_profile)
    return render(request, 'inventory/my_teams.html', {
        'teams': managed_teams
    })

# User Management Views
class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'inventory/user_list.html'
    context_object_name = 'users'

    def get_queryset(self):
        return User.objects.select_related('profile', 'profile__role', 'profile__employee')

class UserCreateView(LoginRequiredMixin, CreateView):
    model = User
    form_class = UserForm
    template_name = 'inventory/user_form.html'
    success_url = reverse_lazy('inventory:user_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['profile_form'] = UserProfileForm(self.request.POST)
        else:
            context['profile_form'] = UserProfileForm()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        profile_form = context['profile_form']
        if profile_form.is_valid():
            user = form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            return redirect(self.success_url)
        return self.render_to_response(self.get_context_data(form=form))

class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'inventory/user_form.html'
    success_url = reverse_lazy('inventory:user_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['profile_form'] = UserProfileForm(self.request.POST, instance=self.object.profile)
        else:
            context['profile_form'] = UserProfileForm(instance=self.object.profile)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        profile_form = context['profile_form']
        if profile_form.is_valid():
            user = form.save()
            profile_form.save()
            return redirect(self.success_url)
        return self.render_to_response(self.get_context_data(form=form))

class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = 'inventory/user_confirm_delete.html'
    success_url = reverse_lazy('inventory:user_list')

    def get(self, request, *args, **kwargs):
        # Check if this is the last user
        if User.objects.count() <= 1:
            messages.error(request, 'Cannot delete the last user in the system.')
            return redirect('inventory:user_list')

        # Get the user to be deleted
        user_to_delete = self.get_object()
        
        # Check if trying to delete an admin user
        if user_to_delete.profile.role and user_to_delete.profile.role.name == 'Administrator':
            # Only allow deletion if the current user is also an admin
            if not request.user.profile.role or request.user.profile.role.name != 'Administrator':
                messages.error(request, 'Only administrators can delete administrator users.')
                return redirect('inventory:user_list')

        return super().get(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        # Check if this is the last user
        if User.objects.count() <= 1:
            messages.error(request, 'Cannot delete the last user in the system.')
            return redirect('inventory:user_list')

        # Get the user to be deleted
        user_to_delete = self.get_object()
        
        # Check if trying to delete an admin user
        if user_to_delete.profile.role and user_to_delete.profile.role.name == 'Administrator':
            # Only allow deletion if the current user is also an admin
            if not request.user.profile.role or request.user.profile.role.name != 'Administrator':
                messages.error(request, 'Only administrators can delete administrator users.')
                return redirect('inventory:user_list')
            
        messages.success(request, 'User deleted successfully.')
        return super().delete(request, *args, **kwargs)

# Role Management Views
class RoleListView(LoginRequiredMixin, ListView):
    model = Role
    template_name = 'inventory/role_list.html'
    context_object_name = 'roles'

class RoleCreateView(LoginRequiredMixin, CreateView):
    model = Role
    form_class = RoleForm
    template_name = 'inventory/role_form.html'
    success_url = reverse_lazy('inventory:role_list')

    def form_valid(self, form):
        messages.success(self.request, 'Role created successfully.')
        return super().form_valid(form)

class RoleUpdateView(LoginRequiredMixin, UpdateView):
    model = Role
    form_class = RoleForm
    template_name = 'inventory/role_form.html'
    success_url = reverse_lazy('inventory:role_list')

    def form_valid(self, form):
        messages.success(self.request, 'Role updated successfully.')
        return super().form_valid(form)

class RoleDeleteView(LoginRequiredMixin, DeleteView):
    model = Role
    template_name = 'inventory/role_confirm_delete.html'
    success_url = reverse_lazy('inventory:role_list')

    def get(self, request, *args, **kwargs):
        role = self.get_object()
        
        # Prevent deletion of Administrator role
        if role.name == 'Administrator':
            messages.error(request, 'Cannot delete the Administrator role.')
            return redirect('inventory:role_list')
            
        return super().get(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        role = self.get_object()
        
        # Prevent deletion of Administrator role
        if role.name == 'Administrator':
            messages.error(request, 'Cannot delete the Administrator role.')
            return redirect('inventory:role_list')
            
        messages.success(request, 'Role deleted successfully.')
        return super().delete(request, *args, **kwargs)

# Authentication Views
@login_required
def logout_view(request):
    # Set last_activity to None before logging out
    if hasattr(request.user, 'profile'):
        profile = request.user.profile
        profile.last_activity = None
        profile.save(update_fields=['last_activity'])
    logout(request)
    return redirect('/accounts/login/')

# Message Views
class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'inventory/message_list.html'
    context_object_name = 'messages'
    paginate_by = 10

    def get_queryset(self):
        return Message.objects.filter(
            recipient=self.request.user,
            parent_message__isnull=True  # Only show parent messages
        ).select_related('sender', 'recipient', 'asset', 'employee')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unread_messages_count'] = Message.objects.filter(
            recipient=self.request.user,
            is_read=False
        ).count()
        # Check for new replies received by the user
        context['has_new_replies'] = Message.objects.filter(
            recipient=self.request.user,
            replies__has_new_reply=True
        ).exists()
        return context

class SentMessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'inventory/sent_message_list.html'
    context_object_name = 'messages'
    paginate_by = 10

    def get_queryset(self):
        return Message.objects.filter(
            sender=self.request.user,
            parent_message__isnull=True  # Only show parent messages, not replies
        ).select_related('recipient')

    def get(self, request, *args, **kwargs):
        # Clear any existing messages before rendering the view
        storage = messages.get_messages(request)
        storage.used = True
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Clear any existing messages
        storage = messages.get_messages(self.request)
        storage.used = True
        context['unread_messages_count'] = Message.objects.filter(
            recipient=self.request.user,
            is_read=False
        ).count()
        return context

class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'inventory/message_form.html'
    success_url = reverse_lazy('inventory:sent_message_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = User.objects.filter(is_active=True).exclude(id=self.request.user.id).order_by('username')
        context['unread_messages_count'] = Message.objects.filter(
            recipient=self.request.user,
            is_read=False
        ).count()
        return context

    def form_valid(self, form):
        try:
            recipient_id = self.request.POST.get('recipient')
            if not recipient_id:
                messages.error(self.request, 'Please select a recipient.')
                return self.form_invalid(form)
            
            recipient = get_object_or_404(User, id=recipient_id)
            message = form.save(commit=False)
            message.sender = self.request.user
            message.recipient = recipient
            message.save()
            return redirect(self.success_url)
        except Exception as e:
            messages.error(self.request, f'Error sending message: {str(e)}')
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'There was an error sending your message. Please check the form and try again.')
        return self.render_to_response(self.get_context_data(form=form))

class MessageDetailView(LoginRequiredMixin, DetailView):
    model = Message
    template_name = 'inventory/message_detail.html'
    context_object_name = 'message'

    def get_queryset(self):
        return Message.objects.filter(
            Q(sender=self.request.user) | Q(recipient=self.request.user)
        ).select_related('sender', 'recipient', 'asset', 'employee')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        message = self.get_object()
        
        # Mark message as read if the current user is the recipient
        if self.request.user == message.recipient and not message.is_read:
            message.mark_as_read()
        
        # Get all replies to this message
        replies = message.get_replies()
        
        # Mark replies as read and clear has_new_reply flag when viewing the message
        if self.request.user == message.recipient:
            # Mark all replies as read and clear has_new_reply flag
            Message.objects.filter(
                parent_message=message,
                recipient=self.request.user,
                is_read=False
            ).update(
                is_read=True,
                has_new_reply=False
            )
            
            # Also clear has_new_reply flag on the parent message
            message.has_new_reply = False
            message.save(update_fields=['has_new_reply'])
        
        context['replies'] = replies
        context['unread_messages_count'] = Message.objects.filter(
            recipient=self.request.user,
            is_read=False
        ).count()
        return context

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        if self.object.recipient == request.user and not self.object.is_read:
            Message.objects.filter(pk=self.object.pk).update(is_read=True)
            self.object.refresh_from_db()
        return response

class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    template_name = 'inventory/message_confirm_delete.html'

    def get_queryset(self):
        # Allow deleting messages where user is either sender or recipient
        return Message.objects.filter(
            Q(sender=self.request.user) | Q(recipient=self.request.user)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unread_messages_count'] = Message.objects.filter(
            recipient=self.request.user,
            is_read=False
        ).count()
        # Add the source URL to the context
        context['source_url'] = self.request.GET.get('source', 'inbox')
        return context

    def get_success_url(self):
        # Get the source from the URL parameter
        source = self.request.GET.get('source', 'inbox')
        
        if source == 'sent':
            return reverse_lazy('inventory:sent_message_list')
        elif source == 'detail':
            # If deleting from detail view, redirect back to the message
            message = self.get_object()
            if message.parent_message:
                return reverse_lazy('inventory:message_detail', kwargs={'pk': message.parent_message.id})
            return reverse_lazy('inventory:message_detail', kwargs={'pk': message.id})
        return reverse_lazy('inventory:message_list')

    def delete(self, request, *args, **kwargs):
        message = self.get_object()
        
        # Check if user is either sender or recipient
        if message.sender != request.user and message.recipient != request.user:
            messages.error(request, 'You can only delete your own messages.')
            return redirect('inventory:message_list')
        
        # If this is a parent message, only delete this specific message
        # Don't delete replies
        if not message.parent_message:
            message.delete()
        else:
            # If this is a reply, just delete the reply
            message.delete()
        
        return redirect(self.get_success_url())

class MessageReplyView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'inventory/message_reply.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        original_message = get_object_or_404(Message, pk=self.kwargs['pk'])
        context['original_message'] = original_message
        context['unread_messages_count'] = Message.objects.filter(
            recipient=self.request.user,
            is_read=False
        ).count()
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        original_message = get_object_or_404(Message, pk=self.kwargs['pk'])
        kwargs['original_message'] = original_message
        return kwargs

    def form_valid(self, form):
        try:
            original_message = get_object_or_404(Message, pk=self.kwargs['pk'])
            message = form.save(commit=False)
            message.sender = self.request.user
            message.recipient = original_message.sender
            message.parent_message = original_message
            message.has_new_reply = True  # Set has_new_reply on the reply
            message.save()

            # Set has_new_reply flag on the parent message
            original_message.has_new_reply = True
            original_message.save(update_fields=['has_new_reply'])

            # Redirect back to the message detail page
            return redirect('inventory:message_detail', pk=original_message.id)
        except Exception as e:
            messages.error(self.request, f'Error sending reply: {str(e)}')
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'There was an error sending your reply. Please check the form and try again.')
        return self.render_to_response(self.get_context_data(form=form))

def message_notifications(request):
    """Stream message notifications using Server-Sent Events."""
    def event_stream():
        last_check = time.time()
        while True:
            # Check for new messages
            new_messages = Message.objects.filter(
                recipient=request.user,
                created_at__gt=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_check))
            ).exists()
            
            if new_messages:
                data = json.dumps({'has_new_messages': True})
                yield f"data: {data}\n\n"
            
            last_check = time.time()
            time.sleep(5)  # Check every 5 seconds
    
    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response

@login_required
def check_replies(request, pk):
    """Check if there are new replies to a message."""
    message = get_object_or_404(Message, pk=pk)
    
    # Get the last reply timestamp from the request
    last_check = request.GET.get('last_check')
    if last_check:
        try:
            last_check = datetime.fromisoformat(last_check.replace('Z', '+00:00'))
            has_new_replies = message.replies.filter(created_at__gt=last_check).exists()
        except (ValueError, TypeError):
            has_new_replies = False
    else:
        has_new_replies = False
    
    return JsonResponse({'has_new_replies': has_new_replies})

def message_context_processor(request):
    """Add message-related context to all templates."""
    if request.user.is_authenticated:
        return {
            'unread_messages_count': Message.objects.filter(
                recipient=request.user,
                is_read=False
            ).count(),
            'has_new_replies': Message.objects.filter(
                recipient=request.user,
                replies__has_new_reply=True
            ).exists()
        }
    return {
        'unread_messages_count': 0,
        'has_new_replies': False
    }  