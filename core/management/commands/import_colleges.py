import csv
from django.core.management.base import BaseCommand
from core.models import College


class Command(BaseCommand):
    help = 'Import colleges from CSV file into College model (name and short_name only)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='data/colleges_202601031430_college_jan.csv',
            help='Path to the CSV file (default: data/colleges_202601031430_college_jan.csv)'
        )

    def handle(self, *args, **options):
        csv_file = options['file']
        
        self.stdout.write(self.style.NOTICE(f'Reading from {csv_file}...'))
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    name = row.get('name', '').strip()
                    short_name = row.get('short_name', '').strip()
                    
                    if not name:
                        skipped_count += 1
                        continue
                    
                    # Use empty string if short_name is not provided
                    if not short_name:
                        short_name = ''
                    
                    # Create or update college
                    college, created = College.objects.update_or_create(
                        name=name,
                        defaults={'short_name': short_name}
                    )
                    
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                        
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {csv_file}'))
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
            return
        
        self.stdout.write(self.style.SUCCESS(
            f'Import completed!\n'
            f'  Created: {created_count}\n'
            f'  Updated: {updated_count}\n'
            f'  Skipped: {skipped_count}'
        ))
