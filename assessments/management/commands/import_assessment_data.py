import csv
from django.core.management.base import BaseCommand
from assessments.models import Question, CareerPath
from courses.models import Course, CourseSkill


class Command(BaseCommand):
    help = 'Import assessment, career, and course data from CSV files'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting data import...'))
        
        # Clear existing data first
        self.stdout.write('Clearing existing data...')
        Question.objects.all().delete()
        CareerPath.objects.all().delete()
        CourseSkill.objects.all().delete()
        Course.objects.all().delete()
        
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
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Store options as dictionary with keys A, B, C, D
                    options = {
                        'A': row['option_a'],
                        'B': row['option_b'],
                        'C': row['option_c'],
                        'D': row['option_d']
                    }
                    
                    Question.objects.create(
                        text=row['question_text'],
                        options=options,
                        correct_option=row['correct_option'].upper(),
                        category='technical',
                        skill_tag=row['skill_tag'],
                        difficulty=row['difficulty']
                    )
                    created += 1
                        
            self.stdout.write(self.style.SUCCESS(f'  Questions: {created} created'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'  File not found: {csv_file}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  Error: {str(e)}'))

    def import_careers(self):
        csv_file = 'data/careers.csv'
        self.stdout.write(f'Importing careers from {csv_file}...')
        
        created = 0
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    CareerPath.objects.create(
                        career_id=row['career_id'],
                        title=row['career_title'],
                        description=row['career_description'],
                        min_score=int(row['min_score']),
                        required_skills=[]  # Will be populated by import_career_required_skills
                    )
                    created += 1
                        
            self.stdout.write(self.style.SUCCESS(f'  Careers: {created} created'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'  File not found: {csv_file}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  Error: {str(e)}'))

    def import_career_required_skills(self):
        """Import career required skills into the JSONField on CareerPath"""
        csv_file = 'data/career_required_skills.csv'
        self.stdout.write(f'Importing career required skills from {csv_file}...')
        
        # Build skills by career_id (as simple list like seed pattern)
        career_skills = {}
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    career_id = row['career_id']
                    if career_id not in career_skills:
                        career_skills[career_id] = []
                    career_skills[career_id].append(row['skill_tag'])
            
            # Update each career with its skills
            updated = 0
            for career_id, skills in career_skills.items():
                try:
                    career = CareerPath.objects.get(career_id=career_id)
                    career.required_skills = skills  # Simple list like seed pattern
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
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Parse pipe-separated fields
                    programs = [p.strip() for p in row['programs_included'].split('|')]
                    ideal_for = [i.strip() for i in row['ideal_for'].split('|')]
                    job_roles = [j.strip() for j in row['job_roles'].split('|')]
                    
                    Course.objects.create(
                        title=row['course_title'],
                        slug=row['slug'],
                        short_description=row['short_description'],
                        description=row['description'],
                        duration=row['duration'],
                        price=float(row['price']),
                        original_price_inr=float(row['original_price_inr']),
                        level=row['level'],
                        language=['English'],
                        programs_included=programs,
                        ideal_for=ideal_for,
                        job_roles=job_roles,
                        is_active=True
                    )
                    created += 1
                        
            self.stdout.write(self.style.SUCCESS(f'  Courses: {created} created'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'  File not found: {csv_file}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  Error: {str(e)}'))

    def import_course_skills(self):
        csv_file = 'data/course_skill_mapping.csv'
        self.stdout.write(f'Importing course skill mappings from {csv_file}...')
        
        created = 0
        
        # Build course lookup by id from course_bundles
        course_id_map = {}
        try:
            with open('data/course_bundles.csv', 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    course_id_map[row['course_id']] = row['slug']
        except:
            pass
        
        courses = {c.slug: c for c in Course.objects.all()}
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    slug = course_id_map.get(row['course_id'])
                    if not slug or slug not in courses:
                        continue
                    
                    CourseSkill.objects.create(
                        course=courses[slug],
                        skill_tag=row['skill_tag']
                    )
                    created += 1
                        
            self.stdout.write(self.style.SUCCESS(f'  Course Skills: {created} created'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'  File not found: {csv_file}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  Error: {str(e)}'))
