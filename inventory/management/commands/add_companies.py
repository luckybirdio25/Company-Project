from django.core.management.base import BaseCommand
from inventory.models import OwnerCompany

class Command(BaseCommand):
    help = 'Adds the initial companies to the database'

    def handle(self, *args, **kwargs):
        # Delete existing companies
        OwnerCompany.objects.all().delete()
        self.stdout.write('Deleted existing companies')

        # Create new companies
        companies = [
            'RadioShack',
            'Computer Shop',
            'Mobile Shop',
            'Compu Me',
            'Smart Home',
            'Vodafone',
        ]

        for name in companies:
            # Generate code from name: lowercase and replace spaces with underscores
            code = name.lower().replace(' ', '_')
            
            OwnerCompany.objects.create(
                code=code,
                name=name
            )
            self.stdout.write(self.style.SUCCESS(f'Created company: {name} (code: {code})'))

        self.stdout.write(self.style.SUCCESS('\nAll companies have been added successfully!')) 