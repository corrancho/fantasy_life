"""
Management command to create initial categories.
"""
from django.core.management.base import BaseCommand
from wishes.models import Category


class Command(BaseCommand):
    help = 'Create initial wish categories'

    def handle(self, *args, **options):
        categories = [
            {
                'name': 'Deseo',
                'description': 'Deseos generales y variados',
                'is_adult': False,
                'max_wishes_per_period': 1,
                'min_days_to_complete': 7,
                'max_days_to_complete': 30,
            },
            {
                'name': 'Fantasía',
                'description': 'Fantasías íntimas y personales',
                'is_adult': True,
                'max_wishes_per_period': 1,
                'min_days_to_complete': 7,
                'max_days_to_complete': 30,
            },
            {
                'name': 'Plan',
                'description': 'Planes y actividades juntos',
                'is_adult': False,
                'max_wishes_per_period': 2,
                'min_days_to_complete': 3,
                'max_days_to_complete': 30,
            },
            {
                'name': 'Sorpresa',
                'description': 'Sorpresas especiales',
                'is_adult': False,
                'max_wishes_per_period': 1,
                'min_days_to_complete': 1,
                'max_days_to_complete': 14,
            },
            {
                'name': 'Reto',
                'description': 'Retos divertidos',
                'is_adult': False,
                'max_wishes_per_period': 1,
                'min_days_to_complete': 7,
                'max_days_to_complete': 21,
            },
        ]
        
        created = 0
        updated = 0
        
        for cat_data in categories:
            category, is_created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            
            if is_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f'Created category: {category.name}'))
            else:
                updated += 1
                self.stdout.write(f'Category already exists: {category.name}')
        
        self.stdout.write(self.style.SUCCESS(
            f'\n=== Summary: {created} created, {updated} already existed ===\n'
        ))