import csv
from django.core.management.base import BaseCommand
from core.models import City, State, CityState


class Command(BaseCommand):
    help = 'Import city-state mappings from CSV file into City, State, and CityState models'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='data/city_state_jan.csv',
            help='Path to the CSV file (default: data/city_state_jan.csv)'
        )

    def handle(self, *args, **options):
        csv_file = options['file']
        
        self.stdout.write(self.style.NOTICE(f'Reading from {csv_file}...'))
        
        city_created_count = 0
        state_created_count = 0
        mapping_created_count = 0
        mapping_skipped_count = 0
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                
                # Skip header row
                header = next(reader)
                self.stdout.write(f'Header: {header}')
                
                for row in reader:
                    if len(row) < 4:
                        continue
                    
                    city_id_csv = row[0].strip()
                    city_name = row[1].strip()
                    state_id_csv = row[2].strip()
                    state_name = row[3].strip()
                    
                    if not city_name or not state_name:
                        mapping_skipped_count += 1
                        continue
                    
                    # Get or create City (unique by name)
                    city, city_created = City.objects.get_or_create(
                        name=city_name
                    )
                    if city_created:
                        city_created_count += 1
                    
                    # Get or create State (unique by name)
                    state, state_created = State.objects.get_or_create(
                        name=state_name
                    )
                    if state_created:
                        state_created_count += 1
                    
                    # Create CityState mapping if not exists (one city can be mapped to multiple states)
                    city_state, mapping_created = CityState.objects.get_or_create(
                        city=city,
                        state=state
                    )
                    if mapping_created:
                        mapping_created_count += 1
                    else:
                        mapping_skipped_count += 1
                        
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {csv_file}'))
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
            return
        
        self.stdout.write(self.style.SUCCESS(
            f'Import completed!\n'
            f'  Cities created: {city_created_count}\n'
            f'  States created: {state_created_count}\n'
            f'  CityState mappings created: {mapping_created_count}\n'
            f'  CityState mappings skipped (duplicates): {mapping_skipped_count}'
        ))
