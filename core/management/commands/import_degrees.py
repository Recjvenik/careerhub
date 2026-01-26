import csv
from django.core.management.base import BaseCommand
from core.models import Degree

class Command(BaseCommand):
    help = 'Import degrees from CSV file'

    def handle(self, *args, **options):
        csv_path = 'data/degrees.csv'
        
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            created_count = 0
            updated_count = 0
            
            for row in reader:
                degree, created = Degree.objects.update_or_create(
                    name=row['name'],
                    defaults={
                        'full_name': row['full_name'],
                        'category': row['category'],
                        'is_tech': row['is_tech'],
                    }
                )
                if created:
                    created_count += 1
                else:
                    updated_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully imported degrees: {created_count} created, {updated_count} updated')
        )
