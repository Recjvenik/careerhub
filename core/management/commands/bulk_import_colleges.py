import csv
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import College


class Command(BaseCommand):
    help = 'Import colleges from CSV using bulk insert for optimal performance (handles 1M+ rows)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=5000,
            help='Number of records to insert per batch (default: 5000)'
        )
        parser.add_argument(
            '--file',
            type=str,
            default='data/colleges_202601031430_college_jan.csv',
            help='Path to CSV file'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing colleges before import'
        )

    def handle(self, *args, **options):
        csv_file = options['file']
        batch_size = options['batch_size']
        clear_existing = options['clear']

        self.stdout.write(f'Starting bulk import from {csv_file}...')
        self.stdout.write(f'Batch size: {batch_size}')

        if clear_existing:
            self.stdout.write('Clearing existing colleges...')
            College.objects.all().delete()

        try:
            # First pass: Get existing colleges to avoid duplicates
            existing_names = set(College.objects.values_list('name', flat=True))
            self.stdout.write(f'Found {len(existing_names)} existing colleges')

            # Read CSV and prepare batches
            colleges_to_create = []
            total_processed = 0
            total_created = 0
            skipped = 0

            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    total_processed += 1
                    name = row.get('name', '').strip()
                    short_name = row.get('short_name', '').strip()

                    if not name:
                        skipped += 1
                        continue

                    # Skip if already exists
                    if name in existing_names:
                        skipped += 1
                        continue

                    colleges_to_create.append(
                        College(name=name, short_name=short_name or '')
                    )
                    existing_names.add(name)  # Track to avoid duplicates in same batch

                    # Bulk insert when batch is full
                    if len(colleges_to_create) >= batch_size:
                        with transaction.atomic():
                            College.objects.bulk_create(
                                colleges_to_create,
                                ignore_conflicts=True
                            )
                        total_created += len(colleges_to_create)
                        self.stdout.write(
                            f'  Processed {total_processed:,} rows, created {total_created:,} colleges...'
                        )
                        colleges_to_create = []

                # Insert remaining records
                if colleges_to_create:
                    with transaction.atomic():
                        College.objects.bulk_create(
                            colleges_to_create,
                            ignore_conflicts=True
                        )
                    total_created += len(colleges_to_create)

            self.stdout.write(self.style.SUCCESS(
                f'\nImport complete!'
                f'\n  Total rows processed: {total_processed:,}'
                f'\n  Colleges created: {total_created:,}'
                f'\n  Skipped (duplicates/empty): {skipped:,}'
            ))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {csv_file}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
