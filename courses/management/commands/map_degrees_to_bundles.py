import csv
from django.core.management.base import BaseCommand
from courses.models import CourseBundle
from core.models import Degree

class Command(BaseCommand):
    help = 'Map degrees to course bundles based on explicit mapping CSV'

    def handle(self, *args, **options):
        csv_path = 'data/degree_bundle_mapping.csv'
        
        self.stdout.write('Clearing existing bundle-degree relationships...')
        # Optional: Clear existing relationships if you want a fresh start
        # CourseBundle.degrees.through.objects.all().delete()
        
        # Or just clear relationships for bundles that are being mapped?
        # For now, let's just add relationships. If we want to replace, we should clear.
        # Given "clear degree table" request earlier, user probably wants clean slate.
        # But clearing ALL relationships might affect bundles not in CSV (if any).
        # Let's iterate and link.
        
        # Better approach: Clear all relationships first to ensure valid state as per new mapping
        for bundle in CourseBundle.objects.all():
            bundle.degrees.clear()
            
        self.stdout.write('Cleared existing relationships. Starting mapping...')

        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            count = 0
            missing_degrees = set()
            missing_bundles = set()
            
            for row in reader:
                degree_name = row['degree_name'].strip()
                career_title = row['career_title'].strip()
                
                try:
                    degree = Degree.objects.get(name__iexact=degree_name)
                except Degree.DoesNotExist:
                    missing_degrees.add(degree_name)
                    continue
                    
                try:
                    # Case insensitive search for title
                    bundle = CourseBundle.objects.get(career_title__iexact=career_title)
                except CourseBundle.DoesNotExist:
                    missing_bundles.add(career_title)
                    continue
                    
                bundle.degrees.add(degree)
                count += 1
        
        if missing_degrees:
            self.stdout.write(self.style.WARNING(f'Missing Degrees: {", ".join(missing_degrees)}'))
            
        if missing_bundles:
            self.stdout.write(self.style.WARNING(f'Missing Bundles: {", ".join(missing_bundles)}'))

        self.stdout.write(self.style.SUCCESS(f'Successfully mapped {count} degree-bundle relationships'))
