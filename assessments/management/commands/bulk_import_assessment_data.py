import csv
import logging
from django.core.management.base import BaseCommand
from django.db import transaction
from assessments.models import Question, CareerPath
from courses.models import Course, CourseSkill

# Setup logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Bulk import assessment data (questions, careers, courses) with error handling and logging'

    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=500,
            help='Number of records to insert per batch (default: 500)'
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
        batch_size = options['batch_size']
        clear_existing = options['clear']
        verbose = options['verbose']

        # Configure logging
        log_level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

        self.errors = []  # Collect all errors
        
        self.log_info('=' * 60)
        self.log_info('Starting bulk assessment data import')
        self.log_info(f'Batch size: {batch_size}')
        self.log_info('=' * 60)

        if clear_existing:
            self.log_info('Clearing existing data...')
            self._clear_data()

        # Import in order
        self.import_questions(batch_size)
        self.import_careers(batch_size)
        self.import_career_skills()
        self.import_courses(batch_size)
        self.import_course_skills(batch_size)

        # Summary
        self.log_info('')
        self.log_info('=' * 60)
        if self.errors:
            self.stdout.write(self.style.WARNING(f'Import completed with {len(self.errors)} errors'))
            self.log_info('Errors:')
            for error in self.errors[:20]:  # Show first 20 errors
                self.log_error(f'  {error}')
            if len(self.errors) > 20:
                self.log_info(f'  ... and {len(self.errors) - 20} more errors')
        else:
            self.stdout.write(self.style.SUCCESS('Import completed successfully with no errors!'))
        self.log_info('=' * 60)

    def _clear_data(self):
        """Clear all existing data"""
        try:
            CourseSkill.objects.all().delete()
            Course.objects.all().delete()
            CareerPath.objects.all().delete()
            Question.objects.all().delete()
            self.log_info('Existing data cleared')
        except Exception as e:
            self.log_error(f'Error clearing data: {e}')

    def import_questions(self, batch_size):
        """Import questions from CSV"""
        csv_file = 'data/assessment_questions.csv'
        self.log_info(f'\n--- Importing Questions from {csv_file} ---')
        
        try:
            questions_to_create = []
            row_num = 0
            skipped = 0
            
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    row_num += 1
                    try:
                        # Validate required fields
                        if not row.get('question_text'):
                            self.errors.append(f'Questions row {row_num}: Missing question_text')
                            skipped += 1
                            continue
                        
                        # Build options dict
                        options = {
                            'A': row.get('option_a', '').strip(),
                            'B': row.get('option_b', '').strip(),
                            'C': row.get('option_c', '').strip(),
                            'D': row.get('option_d', '').strip()
                        }
                        
                        # Validate options
                        if not all(options.values()):
                            self.errors.append(f'Questions row {row_num}: Missing one or more options')
                            skipped += 1
                            continue
                        
                        # Validate correct_option
                        correct_option = row.get('correct_option', '').upper().strip()
                        if correct_option not in ['A', 'B', 'C', 'D']:
                            self.errors.append(f'Questions row {row_num}: Invalid correct_option "{correct_option}"')
                            skipped += 1
                            continue
                        
                        # Validate difficulty
                        difficulty = row.get('difficulty', 'medium').lower().strip()
                        if difficulty not in ['easy', 'medium', 'hard']:
                            difficulty = 'medium'
                        
                        questions_to_create.append(Question(
                            text=row['question_text'].strip(),
                            options=options,
                            correct_option=correct_option,
                            category='technical',
                            skill_tag=row.get('skill_tag', '').strip(),
                            difficulty=difficulty
                        ))
                        
                    except Exception as e:
                        self.errors.append(f'Questions row {row_num}: {str(e)}')
                        skipped += 1
            
            # Bulk create
            if questions_to_create:
                created = self._bulk_create(Question, questions_to_create, batch_size)
                self.log_info(f'Questions: {created} created, {skipped} skipped')
            else:
                self.log_info('No questions to create')
                
        except FileNotFoundError:
            self.log_error(f'File not found: {csv_file}')
        except Exception as e:
            self.log_error(f'Error importing questions: {e}')

    def import_careers(self, batch_size):
        """Import careers from CSV"""
        csv_file = 'data/careers.csv'
        self.log_info(f'\n--- Importing Careers from {csv_file} ---')
        
        try:
            careers_to_create = []
            row_num = 0
            skipped = 0
            
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    row_num += 1
                    try:
                        # Validate required fields
                        career_id = row.get('career_id', '').strip()
                        title = row.get('career_title', '').strip()
                        
                        if not career_id or not title:
                            self.errors.append(f'Careers row {row_num}: Missing career_id or career_title')
                            skipped += 1
                            continue
                        
                        # Validate min_score
                        try:
                            min_score = int(row.get('min_score', 0))
                        except ValueError:
                            self.errors.append(f'Careers row {row_num}: Invalid min_score')
                            skipped += 1
                            continue
                        
                        careers_to_create.append(CareerPath(
                            career_id=career_id,
                            title=title,
                            description=row.get('career_description', '').strip(),
                            min_score=min_score,
                            required_skills=[]
                        ))
                        
                    except Exception as e:
                        self.errors.append(f'Careers row {row_num}: {str(e)}')
                        skipped += 1
            
            # Bulk create
            if careers_to_create:
                created = self._bulk_create(CareerPath, careers_to_create, batch_size)
                self.log_info(f'Careers: {created} created, {skipped} skipped')
            else:
                self.log_info('No careers to create')
                
        except FileNotFoundError:
            self.log_error(f'File not found: {csv_file}')
        except Exception as e:
            self.log_error(f'Error importing careers: {e}')

    def import_career_skills(self):
        """Import career required skills from CSV into CareerPath.required_skills JSONField"""
        csv_file = 'data/career_required_skills.csv'
        self.log_info(f'\n--- Importing Career Skills from {csv_file} ---')
        
        try:
            career_skills = {}  # career_id -> [skill_tags]
            row_num = 0
            
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    row_num += 1
                    career_id = row.get('career_id', '').strip()
                    skill_tag = row.get('skill_tag', '').strip()
                    
                    if not career_id or not skill_tag:
                        self.errors.append(f'Career Skills row {row_num}: Missing career_id or skill_tag')
                        continue
                    
                    if career_id not in career_skills:
                        career_skills[career_id] = []
                    career_skills[career_id].append(skill_tag)
            
            # Update careers
            updated = 0
            for career_id, skills in career_skills.items():
                try:
                    career = CareerPath.objects.get(career_id=career_id)
                    career.required_skills = skills
                    career.save()
                    updated += 1
                except CareerPath.DoesNotExist:
                    self.errors.append(f'Career Skills: Career not found: {career_id}')
            
            self.log_info(f'Career Skills: {updated} careers updated')
            
        except FileNotFoundError:
            self.log_error(f'File not found: {csv_file}')
        except Exception as e:
            self.log_error(f'Error importing career skills: {e}')

    def import_courses(self, batch_size):
        """Import courses from CSV"""
        csv_file = 'data/course_bundles.csv'
        self.log_info(f'\n--- Importing Courses from {csv_file} ---')
        
        try:
            courses_to_create = []
            row_num = 0
            skipped = 0
            
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    row_num += 1
                    try:
                        title = row.get('course_title', '').strip()
                        slug = row.get('slug', '').strip()
                        
                        if not title or not slug:
                            self.errors.append(f'Courses row {row_num}: Missing course_title or slug')
                            skipped += 1
                            continue
                        
                        # Parse price
                        try:
                            price = float(row.get('price', 0))
                            original_price = float(row.get('original_price_inr', price))
                        except ValueError:
                            self.errors.append(f'Courses row {row_num}: Invalid price')
                            skipped += 1
                            continue
                        
                        # Parse pipe-separated fields
                        programs = [p.strip() for p in row.get('programs_included', '').split('|') if p.strip()]
                        ideal_for = [i.strip() for i in row.get('ideal_for', '').split('|') if i.strip()]
                        job_roles = [j.strip() for j in row.get('job_roles', '').split('|') if j.strip()]
                        
                        courses_to_create.append(Course(
                            title=title,
                            slug=slug,
                            short_description=row.get('short_description', '').strip(),
                            description=row.get('description', '').strip(),
                            duration=row.get('duration', '').strip(),
                            price=price,
                            original_price_inr=original_price,
                            level=row.get('level', 'Beginner').strip(),
                            language=['English'],
                            programs_included=programs,
                            ideal_for=ideal_for,
                            job_roles=job_roles,
                            is_active=True
                        ))
                        
                    except Exception as e:
                        self.errors.append(f'Courses row {row_num}: {str(e)}')
                        skipped += 1
            
            # Bulk create
            if courses_to_create:
                created = self._bulk_create(Course, courses_to_create, batch_size)
                self.log_info(f'Courses: {created} created, {skipped} skipped')
            else:
                self.log_info('No courses to create')
                
        except FileNotFoundError:
            self.log_error(f'File not found: {csv_file}')
        except Exception as e:
            self.log_error(f'Error importing courses: {e}')

    def import_course_skills(self, batch_size):
        """Import course-skill mappings from CSV"""
        csv_file = 'data/course_skill_mapping.csv'
        self.log_info(f'\n--- Importing Course Skills from {csv_file} ---')
        
        try:
            # Build course lookup
            course_id_to_slug = {}
            with open('data/course_bundles.csv', 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    course_id_to_slug[row.get('course_id', '')] = row.get('slug', '')
            
            courses = {c.slug: c for c in Course.objects.all()}
            
            skills_to_create = []
            row_num = 0
            skipped = 0
            
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    row_num += 1
                    try:
                        course_id = row.get('course_id', '').strip()
                        skill_tag = row.get('skill_tag', '').strip()
                        
                        if not course_id or not skill_tag:
                            self.errors.append(f'Course Skills row {row_num}: Missing course_id or skill_tag')
                            skipped += 1
                            continue
                        
                        slug = course_id_to_slug.get(course_id)
                        if not slug or slug not in courses:
                            self.errors.append(f'Course Skills row {row_num}: Course not found for id {course_id}')
                            skipped += 1
                            continue
                        
                        skills_to_create.append(CourseSkill(
                            course=courses[slug],
                            skill_tag=skill_tag
                        ))
                        
                    except Exception as e:
                        self.errors.append(f'Course Skills row {row_num}: {str(e)}')
                        skipped += 1
            
            # Bulk create
            if skills_to_create:
                created = self._bulk_create(CourseSkill, skills_to_create, batch_size, ignore_conflicts=True)
                self.log_info(f'Course Skills: {created} created, {skipped} skipped')
            else:
                self.log_info('No course skills to create')
                
        except FileNotFoundError:
            self.log_error(f'File not found: {csv_file}')
        except Exception as e:
            self.log_error(f'Error importing course skills: {e}')

    def _bulk_create(self, model, objects, batch_size, ignore_conflicts=False):
        """Bulk create objects in batches"""
        total = len(objects)
        created = 0
        
        for i in range(0, total, batch_size):
            batch = objects[i:i + batch_size]
            try:
                with transaction.atomic():
                    model.objects.bulk_create(batch, ignore_conflicts=ignore_conflicts)
                created += len(batch)
            except Exception as e:
                self.errors.append(f'Bulk create error at batch {i//batch_size + 1}: {str(e)}')
        
        return created

    def log_info(self, message):
        logger.info(message)
        self.stdout.write(message)

    def log_error(self, message):
        logger.error(message)
        self.stdout.write(self.style.ERROR(message))
