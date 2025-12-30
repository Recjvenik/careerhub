from django.core.management.base import BaseCommand
from assessments.models import Question

class Command(BaseCommand):
    help = 'Seeds initial assessment questions'

    def handle(self, *args, **kwargs):
        questions = [
            {
                'text': 'Do you enjoy solving complex logical puzzles?',
                'options': ['Yes, very much', 'Sometimes', 'No, not really'],
                'correct_option': 'Yes, very much',
                'category': 'aptitude'
            },
            {
                'text': 'How comfortable are you with working with numbers and data?',
                'options': ['Very comfortable', 'Somewhat comfortable', 'Not comfortable'],
                'correct_option': 'Very comfortable',
                'category': 'aptitude'
            },
            {
                'text': 'Do you prefer working in a team or independently?',
                'options': ['Team', 'Independently', 'Both'],
                'correct_option': 'Team',
                'category': 'psychometric'
            },
            {
                'text': 'Are you interested in how software applications work behind the scenes?',
                'options': ['Extremely interested', 'Curious', 'Not interested'],
                'correct_option': 'Extremely interested',
                'category': 'psychometric'
            },
            {
                'text': 'Can you explain a complex idea to a 5-year-old?',
                'options': ['Yes, easily', 'Maybe with effort', 'No, it is hard'],
                'correct_option': 'Yes, easily',
                'category': 'psychometric'
            }
        ]
        
        for q_data in questions:
            Question.objects.get_or_create(
                text=q_data['text'],
                defaults={
                    'options': q_data['options'],
                    'correct_option': q_data['correct_option'],
                    'category': q_data['category']
                }
            )
            
        self.stdout.write(self.style.SUCCESS('Successfully seeded questions'))
