from django.core.management.base import BaseCommand
from core.models import State, City, College, Branch

class Command(BaseCommand):
    help = 'Seeds core data for State, City, College, and Branch'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding data...')

        states = ['California', 'New York', 'Texas', 'Florida', 'Illinois', 'Pennsylvania', 'Ohio', 'Georgia', 'North Carolina', 'Michigan']
        cities_map = {
            'California': ['Los Angeles', 'San Francisco', 'San Diego'],
            'New York': ['New York City', 'Buffalo', 'Rochester'],
            'Texas': ['Houston', 'Austin', 'Dallas'],
            'Florida': ['Miami', 'Orlando', 'Tampa'],
            'Illinois': ['Chicago', 'Aurora', 'Naperville'],
            'Pennsylvania': ['Philadelphia', 'Pittsburgh', 'Allentown'],
            'Ohio': ['Columbus', 'Cleveland', 'Cincinnati'],
            'Georgia': ['Atlanta', 'Savannah', 'Augusta'],
            'North Carolina': ['Charlotte', 'Raleigh', 'Greensboro'],
            'Michigan': ['Detroit', 'Grand Rapids', 'Warren']
        }
        
        colleges = ['Stanford University', 'MIT', 'Harvard University', 'UC Berkeley', 'University of Oxford', 'University of Cambridge', 'Caltech', 'Princeton University', 'Yale University', 'University of Chicago']
        branches = ['Computer Science', 'Mechanical Engineering', 'Electrical Engineering', 'Civil Engineering', 'Chemical Engineering', 'Biomedical Engineering', 'Aerospace Engineering', 'Industrial Engineering', 'Environmental Engineering', 'Materials Science']

        for state_name in states:
            state, created = State.objects.get_or_create(name=state_name)
            if created:
                self.stdout.write(f'Created State: {state_name}')
            
            for city_name in cities_map.get(state_name, []):
                City.objects.get_or_create(name=city_name, state=state)

        for college_name in colleges:
            College.objects.get_or_create(name=college_name)

        for branch_name in branches:
            Branch.objects.get_or_create(name=branch_name)

        self.stdout.write(self.style.SUCCESS('Successfully seeded core data'))
