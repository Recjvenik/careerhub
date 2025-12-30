from django.core.management.base import BaseCommand
from courses.models import Course
from decimal import Decimal

class Command(BaseCommand):
    help = 'Seeds the database with initial course data'

    def handle(self, *args, **kwargs):
        courses_data = [
            {
                "title": "Full Stack Web Development",
                "short_description": "Master frontend and backend development with React, Node.js, and Python.",
                "description": "Become a full-stack developer by learning the most in-demand technologies. This comprehensive course covers HTML, CSS, JavaScript, React, Django, and database management. You will build real-world projects and gain the skills needed to land a high-paying job.",
                "duration": "12 weeks",
                "price": Decimal("0.00"),
                "original_price_inr": Decimal("4999.00"),
                "level": "Beginner to Intermediate",
                "language": ["English", "Hindi"],
                "programs_included": ["Frontend Development", "Backend Development", "Database Management", "Deployment"],
                "ideal_for": ["Students", "Career Switchers", "Aspiring Developers"],
                "job_roles": ["Full Stack Developer", "Frontend Engineer", "Backend Developer"]
            },
            {
                "title": "Data Science with Python",
                "short_description": "Learn data analysis, visualization, and machine learning using Python.",
                "description": "Unlock the power of data with our Data Science course. Learn Python programming, data manipulation with Pandas, visualization with Matplotlib, and machine learning with Scikit-learn. Work on case studies and build a portfolio of data projects.",
                "duration": "10 weeks",
                "price": Decimal("0.00"),
                "original_price_inr": Decimal("5999.00"),
                "level": "Intermediate",
                "language": ["English"],
                "programs_included": ["Python Programming", "Data Analysis", "Machine Learning", "Data Visualization"],
                "ideal_for": ["Analysts", "Engineers", "Math/Stats Graduates"],
                "job_roles": ["Data Scientist", "Data Analyst", "ML Engineer"]
            },
            {
                "title": "Digital Marketing Mastery",
                "short_description": "Become a digital marketing expert with SEO, SEM, and Social Media strategies.",
                "description": "Master the art of digital marketing. Learn Search Engine Optimization (SEO), Search Engine Marketing (SEM), Social Media Marketing (SMM), and Content Marketing. Drive traffic, generate leads, and grow businesses online.",
                "duration": "8 weeks",
                "price": Decimal("0.00"),
                "original_price_inr": Decimal("3499.00"),
                "level": "Beginner",
                "language": ["English", "Hindi"],
                "programs_included": ["SEO", "Google Ads", "Social Media Marketing", "Email Marketing"],
                "ideal_for": ["Entrepreneurs", "Marketing Professionals", "Students"],
                "job_roles": ["Digital Marketing Manager", "SEO Specialist", "Social Media Manager"]
            },
             {
                "title": "UI/UX Design Fundamentals",
                "short_description": "Design beautiful and user-friendly interfaces using Figma and Adobe XD.",
                "description": "Learn the principles of User Interface (UI) and User Experience (UX) design. Master tools like Figma and Adobe XD to create wireframes, prototypes, and high-fidelity mockups. Understand user research and usability testing.",
                "duration": "6 weeks",
                "price": Decimal("0.00"),
                "original_price_inr": Decimal("3999.00"),
                "level": "Beginner",
                "language": ["English"],
                "programs_included": ["Design Thinking", "Wireframing", "Prototyping", "Figma Mastery"],
                "ideal_for": ["Designers", "Creative Minds", "Developers"],
                "job_roles": ["UI Designer", "UX Researcher", "Product Designer"]
            }
        ]

        for course_data in courses_data:
            course, created = Course.objects.get_or_create(
                title=course_data['title'],
                defaults=course_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Successfully created course "{course.title}"'))
            else:
                self.stdout.write(self.style.WARNING(f'Course "{course.title}" already exists'))
