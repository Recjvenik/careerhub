import csv
import json
from django.core.management.base import BaseCommand
from assessments.models import Question, CareerPath

class Command(BaseCommand):
    help = 'Import assessment questions and career paths from CSV files'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Clear existing data before import')

    def handle(self, *args, **options):
        if options.get('clear'):
            self.stdout.write('Clearing existing data...')
            Question.objects.all().delete()
            CareerPath.objects.all().delete()
        
        self.import_questions()
        self.import_careers()
        
        self.stdout.write(self.style.SUCCESS('Import completed!'))

    def import_questions(self):
        """Import questions from CSV. Options field should be JSON array."""
        csv_path = 'data/assessment_questions.csv'
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                created_count = 0
                
                for row in reader:
                    # Parse options - expects JSON array like ["A. Option 1", "B. Option 2"]
                    options_list = json.loads(row['options'])
                    
                    # Convert list to dictionary for template consistency
                    options = {}
                    if isinstance(options_list, list):
                        for opt in options_list:
                            # Split by first dot and space to separate Key and Value
                            # e.g. "A. Option Text" -> "A", "Option Text"
                            parts = opt.split('.', 1)
                            if len(parts) == 2:
                                key = parts[0].strip()
                                value = parts[1].strip()
                                options[key] = value
                            else:
                                # Fallback if format doesn't match
                                options[opt] = opt
                    else:
                        # Fallback if already dict or something else
                        options = options_list
                    
                    Question.objects.create(
                        text=row['text'],
                        options=options,
                        correct_option=row['correct_option'] if row['correct_option'] else None,
                        category=row['category'],
                        skill_tag=row.get('skill_tag', ''),
                        difficulty=row.get('difficulty', 'medium')
                    )
                    created_count += 1
            
            self.stdout.write(self.style.SUCCESS(f'Imported {created_count} questions'))
        except FileNotFoundError:
            self.stdout.write(self.style.WARNING(f'Questions file not found: {csv_path}'))

    def import_careers(self):
        """Import career paths from CSV."""
        csv_path = 'data/careers.csv'
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                created_count = 0
                
                for row in reader:
                    required_skills = []
                    if row.get('required_skills'):
                        required_skills = [s.strip() for s in row['required_skills'].split(';')]
                    
                    CareerPath.objects.update_or_create(
                        career_id=row['career_id'],
                        defaults={
                            'title': row['career_title'],
                            'description': row.get('career_description', ''),
                            'min_score': int(row.get('min_score', 0)),
                            'required_skills': required_skills,
                        }
                    )
                    created_count += 1
            
            self.stdout.write(self.style.SUCCESS(f'Imported {created_count} career paths'))
        except FileNotFoundError:
            self.stdout.write(self.style.WARNING(f'Careers file not found: {csv_path}'))
