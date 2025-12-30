from django.core.management.base import BaseCommand
from assessments.models import Question, CareerPath
from courses.models import Course, CourseSkill

class Command(BaseCommand):
    help = 'Seeds the database with assessment questions, career paths, and course bundles'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding assessment data...')

        # 1. Questions
        questions_data = [
            {
                "question": "What is the main purpose of Python indentation?",
                "options": {
                    "A": "To improve performance",
                    "B": "To define code blocks",
                    "C": "To separate functions",
                    "D": "To avoid syntax errors only"
                },
                "correct_option": "B",
                "skill_tag": "python_basics",
                "difficulty": "easy"
            },
            {
                "question": "Which data type in Python is immutable?",
                "options": {
                    "A": "List",
                    "B": "Set",
                    "C": "Dictionary",
                    "D": "Tuple"
                },
                "correct_option": "D",
                "skill_tag": "python_core",
                "difficulty": "easy"
            },
            {
                "question": "Which Django component handles database queries?",
                "options": {
                    "A": "Views",
                    "B": "Templates",
                    "C": "ORM",
                    "D": "Middleware"
                },
                "correct_option": "C",
                "skill_tag": "django_core",
                "difficulty": "medium"
            },
            {
                "question": "What is the benefit of using QuerySet filtering instead of Python loops?",
                "options": {
                    "A": "Cleaner syntax",
                    "B": "Better database performance",
                    "C": "Less memory usage in Python",
                    "D": "All of the above"
                },
                "correct_option": "D",
                "skill_tag": "django_orm",
                "difficulty": "medium"
            },
            {
                "question": "Why is pagination important in APIs?",
                "options": {
                    "A": "Improves UI design",
                    "B": "Reduces database size",
                    "C": "Prevents large response payloads",
                    "D": "Avoids authentication"
                },
                "correct_option": "C",
                "skill_tag": "api_performance",
                "difficulty": "medium"
            },
            {
                "question": "Which practice helps in handling slow APIs in production?",
                "options": {
                    "A": "Adding print statements",
                    "B": "Using caching and query optimization",
                    "C": "Increasing server RAM only",
                    "D": "Disabling logs"
                },
                "correct_option": "B",
                "skill_tag": "production_backend",
                "difficulty": "hard"
            }
        ]

        Question.objects.all().delete()
        for q_data in questions_data:
            Question.objects.create(
                text=q_data['question'],
                options=q_data['options'],
                correct_option=q_data['correct_option'],
                skill_tag=q_data['skill_tag'],
                difficulty=q_data['difficulty'],
                category='technical'
            )

        # 2. Career Paths
        career_paths_data = [
            {
                "career_id": "backend_intern",
                "title": "Backend Developer Intern",
                "description": "Entry-level backend role focusing on Python, Django, and API development under guidance.",
                "min_score": 40,
                "required_skills": [
                    "python_basics",
                    "python_core",
                    "django_core"
                ]
            },
            {
                "career_id": "junior_backend_dev",
                "title": "Junior Backend Developer",
                "description": "Responsible for building APIs, working with Django ORM, and handling backend logic.",
                "min_score": 60,
                "required_skills": [
                    "python_core",
                    "advanced_python",
                    "django_core",
                    "django_orm",
                    "api_basics"
                ]
            },
            {
                "career_id": "api_developer",
                "title": "API / Django REST Developer",
                "description": "Specializes in REST APIs, authentication, performance optimization, and production readiness.",
                "min_score": 75,
                "required_skills": [
                    "advanced_python",
                    "django_orm",
                    "api_basics",
                    "api_performance",
                    "production_backend"
                ]
            }
        ]

        CareerPath.objects.all().delete()
        for cp_data in career_paths_data:
            CareerPath.objects.create(
                career_id=cp_data['career_id'],
                title=cp_data['title'],
                description=cp_data['description'],
                min_score=cp_data['min_score'],
                required_skills=cp_data['required_skills']
            )

        # 3. Courses and Skills
        courses_data = [
          {
            "title": "Python & Django Foundations",
            "slug": "python-django-foundations",
            "short_description": "Build strong Python fundamentals and understand Django backend basics.",
            "description": "This foundational course is designed for students who want to start a backend development career. It covers Python basics, core concepts, and an introduction to Django architecture and request handling.",
            "duration": "6 weeks",
            "price": 999.00,
            "original_price_inr": 2499.00,
            "level": "Beginner",
            "language": ["English"],
            "programs_included": [
              "Python Basics & Syntax",
              "Data Types & Control Flow",
              "Functions & Exception Handling",
              "Django Architecture Overview",
              "Request–Response Lifecycle"
            ],
            "ideal_for": [
              "Beginners in programming",
              "Students exploring backend development",
              "BA / BSc / Engineering students"
            ],
            "job_roles": [
              "Backend Developer Intern",
              "Junior Backend Trainee"
            ],
            "is_active": True,
            "skills": [
                "python_basics",
                "python_core",
                "django_core"
            ]
          },
          {
            "title": "Backend ORM & API Development",
            "slug": "backend-orm-api-development",
            "short_description": "Learn Django ORM, database relationships, and REST API fundamentals.",
            "description": "This course focuses on real-world backend development using Django ORM and API concepts. Students learn how to model data, optimize queries, and design clean APIs.",
            "duration": "5 weeks",
            "price": 1199.00,
            "original_price_inr": 2999.00,
            "level": "Beginner to Intermediate",
            "language": ["English"],
            "programs_included": [
              "Django Models & Relationships",
              "QuerySet Fundamentals",
              "Filtering, Sorting & Pagination",
              "REST API Basics",
              "JSON Handling"
            ],
            "ideal_for": [
              "Backend Interns",
              "Junior Developers",
              "Students with Python basics"
            ],
            "job_roles": [
              "Junior Backend Developer",
              "API Developer Intern"
            ],
            "is_active": True,
            "skills": [
                "django_orm",
                "api_basics"
            ]
          },
          {
            "title": "Production-Ready Backend Developer",
            "slug": "production-ready-backend-developer",
            "short_description": "Prepare your backend skills for real production environments.",
            "description": "This advanced course prepares students for real-world backend challenges such as performance optimization, caching, authentication, and debugging production issues.",
            "duration": "4 weeks",
            "price": 1499.00,
            "original_price_inr": 3999.00,
            "level": "Intermediate",
            "language": ["English"],
            "programs_included": [
              "Django REST Framework Deep Dive",
              "Authentication & Permissions",
              "Query Optimization Techniques",
              "Caching & Throttling",
              "Logging & Debugging APIs"
            ],
            "ideal_for": [
              "Junior Backend Developers",
              "API Developers",
              "Placement-focused students"
            ],
            "job_roles": [
              "API Developer",
              "Backend Developer"
            ],
            "is_active": True,
            "skills": [
                "api_performance",
                "production_backend"
            ]
          },
          {
            "title": "Backend Career Kickstart",
            "slug": "backend-career-kickstart",
            "short_description": "A complete roadmap from beginner to job-ready backend developer.",
            "description": "This bundled program combines Python, Django, APIs, and interview preparation to make students job-ready for backend roles. Ideal for students who want a guided, end-to-end learning path.",
            "duration": "10 weeks",
            "price": 1999.00,
            "original_price_inr": 4999.00,
            "level": "Beginner",
            "language": ["English"],
            "programs_included": [
              "Python & Django Foundations",
              "Backend ORM & API Development",
              "Production Backend Basics",
              "Interview & Resume Preparation"
            ],
            "ideal_for": [
              "Final-year students",
              "Career switchers",
              "Placement aspirants"
            ],
            "job_roles": [
              "Backend Developer Intern",
              "Junior Backend Developer"
            ],
            "is_active": True,
            "skills": [
                "python_basics",
                "django_core",
                "api_basics"
            ]
          }
        ]

        Course.objects.all().delete()
        # Note: Deleting courses might cascade delete CourseSkills, but let's be safe.
        CourseSkill.objects.all().delete()

        for c_data in courses_data:
            course = Course.objects.create(
                title=c_data['title'],
                slug=c_data['slug'],
                description=c_data['description'],
                short_description=c_data['short_description'],
                duration=c_data['duration'],
                price=c_data['price'],
                original_price_inr=c_data['original_price_inr'],
                level=c_data['level'],
                language=c_data['language'],
                programs_included=c_data['programs_included'],
                ideal_for=c_data['ideal_for'],
                job_roles=c_data['job_roles'],
                is_active=c_data['is_active']
            )
            
            for skill in c_data['skills']:
                CourseSkill.objects.create(
                    course=course,
                    skill_tag=skill
                )

        self.stdout.write(self.style.SUCCESS('Successfully seeded assessment data'))
