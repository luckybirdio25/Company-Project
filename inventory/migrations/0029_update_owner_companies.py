from django.db import migrations

def update_owner_companies(apps, schema_editor):
    OwnerCompany = apps.get_model('inventory', 'OwnerCompany')
    
    # Delete existing companies
    OwnerCompany.objects.all().delete()
    
    # Create new companies
    companies = [
        ('radioshack', 'RadioShack'),
        ('computer_shop', 'Computer Shop'),
        ('mobile_shop', 'Mobile Shop'),
        ('compu_me', 'Compu Me'),
        ('smart_home', 'Smart Home'),
        ('vodafone', 'Vodafone'),
    ]
    
    for code, name in companies:
        OwnerCompany.objects.create(
            code=code,
            name=name
        )

def reverse_update_owner_companies(apps, schema_editor):
    OwnerCompany = apps.get_model('inventory', 'OwnerCompany')
    
    # Delete all companies
    OwnerCompany.objects.all().delete()
    
    # Recreate original companies
    companies = [
        ('AMAN', 'Aman'),
        ('CTP', 'CTP'),
        ('MISR_ASSIST', 'Misr Assist'),
    ]
    
    for code, name in companies:
        OwnerCompany.objects.create(
            code=code,
            name=name
        )

class Migration(migrations.Migration):
    dependencies = [
        ('inventory', '0028_alter_employee_employee_id_alter_ownercompany_code'),
    ]

    operations = [
        migrations.RunPython(update_owner_companies, reverse_update_owner_companies),
    ] 