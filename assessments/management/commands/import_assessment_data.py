import csv
from django.core.management.base import BaseCommand
from assessments.models import Question, CareerPath
from courses.models import Course, CourseSkill


class Command(BaseCommand):
    help = 'Import assessment, career, and course data from CSV files'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting data import...'))
        
        # Import Assessment Questions
        self.import_questions()
        
        # Import Careers
        self.import_careers()
        
        # Import Career Required Skills (into JSONField)
        self.import_career_required_skills()
        
        # Import Course Bundles
        self.import_courses()
        
        # Import Course Skill Mappings
        self.import_course_skills()
        
        self.stdout.write(self.style.SUCCESS('All data imported successfully!'))

    def import_questions(self):
        csv_file = 'data/assessment_questions.csv'
        self.stdout.write(f'Importing questions from {csv_file}...')
        
        created = 0
        updated = 0
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    options = [
                        row['option_a'],
                        row['option_b'],
                        row['option_c'],
                        row['option_d']
                    ]
                    
                    # Map correct_option letter to actual option text
                    correct_map = {'a': 0, 'b': 1, 'c': 2, 'd': 3}
                    correct_idx = correct_map.get(row['correct_option'].lower(), 0)
                    correct_option = options[correct_idx]
                    
                    question, is_created = Question.objects.update_or_create(
                        text=row['question_text'],
                        defaults={
                            'options': options,
                            'correct_option': correct_option,
                            'category': 'technical',
                            'skill_tag': row['skill_tag'],
                            'difficulty': row['difficulty']
                        }
                    )
                    
                    if is_created:
                        created += 1
                    else:
                        updated += 1
                        
            self.stdout.write(self.style.SUCCESS(f'  Questions: {created} created, {updated} updated'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'  File not found: {csv_file}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  Error: {str(e)}'))

    def import_careers(self):
        csv_file = 'data/careers.csv'
        self.stdout.write(f'Importing careers from {csv_file}...')
        
        created = 0
        updated = 0
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    career, is_created = CareerPath.objects.update_or_create(
                        career_id=row['career_id'],
                        defaults={
                            'title': row['career_title'],
                            'description': row['career_description'],
                            'min_score': int(row['min_score']),
                            'required_skills': []
                        }
                    )
                    
                    if is_created:
                        created += 1
                    else:
                        updated += 1
                        
            self.stdout.write(self.style.SUCCESS(f'  Careers: {created} created, {updated} updated'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'  File not found: {csv_file}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  Error: {str(e)}'))

    def import_career_required_skills(self):
        """Import career required skills into the JSONField on CareerPath"""
        csv_file = 'data/career_required_skills.csv'
        self.stdout.write(f'Importing career required skills from {csv_file}...')
        
        # Build skills by career_id
        career_skills = {}
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    career_id = row['career_id']
                    if career_id not in career_skills:
                        career_skills[career_id] = []
                    
                    career_skills[career_id].append({
                        'skill_tag': row['skill_tag'],
                        'required_level': row['required_level']
                    })
            
            # Update each career with its skills
            updated = 0
            for career_id, skills in career_skills.items():
                try:
                    career = CareerPath.objects.get(career_id=career_id)
                    career.required_skills = skills
                    career.save()
                    updated += 1
                except CareerPath.DoesNotExist:
                    pass
                        
            self.stdout.write(self.style.SUCCESS(f'  Career Skills: {updated} careers updated'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'  File not found: {csv_file}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  Error: {str(e)}'))

    def import_courses(self):
        csv_file = 'data/course_bundles.csv'
        self.stdout.write(f'Importing courses from {csv_file}...')
        
        created = 0
        updated = 0
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    job_roles = [r.strip() for r in row['job_roles'].split('|')]
                    
                    course, is_created = Course.objects.update_or_create(
                        title=row['course_title'],
                        defaults={
                            'short_description': row['short_description'],
                            'description': row['short_description'],
                            'level': row['level'].capitalize(),
                            'duration': row['duration'],
                            'price': float(row['price_inr']),
                            'original_price_inr': float(row['price_inr']),
                            'job_roles': job_roles,
                            'language': ['English'],
                            'programs_included': [],
                            'ideal_for': []
                        }
                    )
                    
                    if is_created:
                        created += 1
                    else:
                        updated += 1
                        
            self.stdout.write(self.style.SUCCESS(f'  Courses: {created} created, {updated} updated'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'  File not found: {csv_file}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  Error: {str(e)}'))

    def import_course_skills(self):
        csv_file = 'data/course_skill_mapping.csv'
        self.stdout.write(f'Importing course skill mappings from {csv_file}...')
        
        created = 0
        skipped = 0
        
        # Build course lookup by title
        courses = {c.title: c for c in Course.objects.all()}
        
        # Load course bundles to map course_id to title
        course_id_map = {}
        try:
            with open('data/course_bundles.csv', 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    course_id_map[row['course_id']] = row['course_title']
        except:
            pass
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    course_title = course_id_map.get(row['course_id'])
                    if not course_title or course_title not in courses:
                        skipped += 1
                        continue
                    
                    course = courses[course_title]
                    
                    skill, is_created = CourseSkill.objects.update_or_create(
                        course=course,
                        skill_tag=row['skill_tag'],
                        defaults={
                            'coverage_level': row['coverage_level'],
                            'relevance_score': 100
                        }
                    )
                    
                    if is_created:
                        created += 1
                        
            self.stdout.write(self.style.SUCCESS(f'  Course Skills: {created} created, {skipped} skipped'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'  File not found: {csv_file}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  Error: {str(e)}'))
