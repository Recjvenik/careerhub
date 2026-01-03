import csv
from django.core.management.base import BaseCommand
from core.models import Branch


class Command(BaseCommand):
    help = 'Import branches from CSV file into Branch model (name column only)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='data/branches_202601031513_city_jan.csv',
            help='Path to the CSV file (default: data/branches_202601031513_city_jan.csv)'
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
                    
                    if not name:
                        skipped_count += 1
                        continue
                    
                    # Create or update branch (short_name will be empty by default)
                    branch, created = Branch.objects.update_or_create(
                        name=name,
                        defaults={'short_name': ''}
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
