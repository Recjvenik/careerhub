import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from courses.models import CourseBundle
from core.models import Degree

class Command(BaseCommand):
    help = 'Import course bundles from CSV files'

    def handle(self, *args, **options):
        csv_files = [
            'data/course_bundles_arts_commerce.csv',
            'data/course_bundles_engineering.csv',
        ]
        
        total_created = 0
        total_updated = 0
        
        for csv_path in csv_files:
            self.stdout.write(f'Processing {csv_path}...')
            
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    # Parse date
                    next_batch_date = datetime.strptime(row['next_batch_date'], '%Y-%m-%d').date()
                    
                    # Create or update bundle
                    bundle, created = CourseBundle.objects.update_or_create(
                        career_title=row['career_title'],
                        defaults={
                            'skills_required': row['skills_required'],
                            'duration': row['duration'],
                            'original_price': row['original_price'],
                            'discounted_price': row['discounted_price'],
                            'next_batch_date': next_batch_date,
                            'initial_salary': int(row.get('initial_salary', 0)),
                            'is_active': True,
                        }
                    )
                    
                    # Link degrees (pipe-separated)
                    degree_names = row['degrees'].split('|')
                    degrees = Degree.objects.filter(name__in=degree_names)
                    bundle.degrees.add(*degrees)
                    
                    if created:
                        total_created += 1
                    else:
                        total_updated += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully imported bundles: {total_created} created, {total_updated} updated')
        )
