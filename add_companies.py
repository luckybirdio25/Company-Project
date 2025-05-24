import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory.settings')
django.setup()

from inventory.models import OwnerCompany

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
    print(f"Created company: {name}")

print("\nAll companies have been added successfully!") 