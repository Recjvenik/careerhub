import csv
import logging
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import City, State, CityState

# Setup logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Bulk import cities, states, and their mappings from CSV with logging'

    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=1000,
            help='Number of records to insert per batch (default: 1000)'
        )
        parser.add_argument(
            '--file',
            type=str,
            default='data/city_state_jan.csv',
            help='Path to CSV file'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before import'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose logging'
        )

    def handle(self, *args, **options):
        csv_file = options['file']
        batch_size = options['batch_size']
        clear_existing = options['clear']
        verbose = options['verbose']

        # Configure logging level
        if verbose:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)

        self.log_info(f'Starting bulk import from {csv_file}')
        self.log_info(f'Batch size: {batch_size}')

        if clear_existing:
            self.log_info('Clearing existing data...')
            CityState.objects.all().delete()
            City.objects.all().delete()
            State.objects.all().delete()
            self.log_info('Existing data cleared')

        try:
            # Phase 1: Collect unique states and cities
            self.log_info('Phase 1: Reading CSV and collecting unique entries...')
            
            unique_states = {}  # name -> State object
            unique_cities = {}  # name -> City object
            city_state_pairs = []  # [(city_name, state_name), ...]
            
            total_rows = 0
            
            with open(csv_file, 'r', encoding='utf-8') as file:
                # Read header to understand structure
                header = file.readline().strip()
                self.log_info(f'CSV Header: {header}')
                
                # Handle CSV with duplicate 'name' columns
                # Expected format: city_id, name (city), state_id, name (state)
                # We'll read raw and parse by position
                
                for line in file:
                    total_rows += 1
                    
                    # Parse CSV line (handle quoted values)
                    parts = []
                    current = ''
                    in_quotes = False
                    for char in line.strip():
                        if char == '"':
                            in_quotes = not in_quotes
                        elif char == ',' and not in_quotes:
                            parts.append(current.strip().strip('"'))
                            current = ''
                        else:
                            current += char
                    parts.append(current.strip().strip('"'))
                    
                    if len(parts) >= 4:
                        # city_id, city_name, state_id, state_name
                        city_name = parts[1].strip()
                        state_name = parts[3].strip()
                        
                        if city_name and state_name:
                            unique_states[state_name] = None
                            unique_cities[city_name] = None
                            city_state_pairs.append((city_name, state_name))
                    
                    if total_rows % 10000 == 0:
                        self.log_info(f'  Read {total_rows:,} rows...')

            self.log_info(f'Total rows read: {total_rows:,}')
            self.log_info(f'Unique states: {len(unique_states):,}')
            self.log_info(f'Unique cities: {len(unique_cities):,}')
            self.log_info(f'City-State pairs: {len(city_state_pairs):,}')

            # Phase 2: Bulk create states
            self.log_info('Phase 2: Creating states...')
            existing_states = {s.name: s for s in State.objects.all()}
            
            states_to_create = []
            for state_name in unique_states.keys():
                if state_name not in existing_states:
                    states_to_create.append(State(name=state_name))
            
            if states_to_create:
                created_states = self._bulk_create_in_batches(
                    State, states_to_create, batch_size, 'states'
                )
                # Refresh existing_states dict
                for state in State.objects.filter(name__in=[s.name for s in states_to_create]):
                    existing_states[state.name] = state
            
            states_created = len(states_to_create)
            self.log_info(f'States created: {states_created:,}')

            # Phase 3: Bulk create cities
            self.log_info('Phase 3: Creating cities...')
            existing_cities = {c.name: c for c in City.objects.all()}
            
            cities_to_create = []
            for city_name in unique_cities.keys():
                if city_name not in existing_cities:
                    cities_to_create.append(City(name=city_name))
            
            if cities_to_create:
                self._bulk_create_in_batches(
                    City, cities_to_create, batch_size, 'cities'
                )
                # Refresh existing_cities dict
                for city in City.objects.filter(name__in=[c.name for c in cities_to_create]):
                    existing_cities[city.name] = city
            
            cities_created = len(cities_to_create)
            self.log_info(f'Cities created: {cities_created:,}')

            # Phase 4: Bulk create city-state mappings
            self.log_info('Phase 4: Creating city-state mappings...')
            
            # Get all existing mappings
            existing_mappings = set(
                CityState.objects.values_list('city__name', 'state__name')
            )
            
            mappings_to_create = []
            skipped_mappings = 0
            
            for city_name, state_name in city_state_pairs:
                if (city_name, state_name) in existing_mappings:
                    skipped_mappings += 1
                    continue
                
                city = existing_cities.get(city_name)
                state = existing_states.get(state_name)
                
                if city and state:
                    mappings_to_create.append(
                        CityState(city=city, state=state)
                    )
                    existing_mappings.add((city_name, state_name))
            
            if mappings_to_create:
                self._bulk_create_in_batches(
                    CityState, mappings_to_create, batch_size, 'city-state mappings',
                    ignore_conflicts=True
                )
            
            mappings_created = len(mappings_to_create)
            
            self.log_info('')
            self.stdout.write(self.style.SUCCESS(
                f'Import complete!\n'
                f'  Total rows processed: {total_rows:,}\n'
                f'  States created: {states_created:,}\n'
                f'  Cities created: {cities_created:,}\n'
                f'  Mappings created: {mappings_created:,}\n'
                f'  Mappings skipped (duplicates): {skipped_mappings:,}'
            ))

        except FileNotFoundError:
            self.log_error(f'File not found: {csv_file}')
            self.stdout.write(self.style.ERROR(f'File not found: {csv_file}'))
        except Exception as e:
            self.log_error(f'Error during import: {str(e)}')
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
            raise

    def _bulk_create_in_batches(self, model, objects, batch_size, label, ignore_conflicts=False):
        """Helper to bulk create objects in batches with progress logging"""
        total = len(objects)
        created = 0
        
        for i in range(0, total, batch_size):
            batch = objects[i:i + batch_size]
            with transaction.atomic():
                model.objects.bulk_create(batch, ignore_conflicts=ignore_conflicts)
            created += len(batch)
            self.log_debug(f'  Created {created:,}/{total:,} {label}')
        
        return created

    def log_info(self, message):
        logger.info(message)
        self.stdout.write(message)

    def log_debug(self, message):
        logger.debug(message)

    def log_error(self, message):
        logger.error(message)
