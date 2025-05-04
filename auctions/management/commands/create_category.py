from django.core.management.base import BaseCommand
from django.utils.text import slugify
from auctions.models import Category

class Command(BaseCommand):
    help = 'Creates a new category or updates an existing one'

    def add_arguments(self, parser):
        parser.add_argument('--name', type=str, required=True, help='Category name')
        parser.add_argument('--description', type=str, default='', help='Category description (optional)')
        parser.add_argument('--slug', type=str, default=None, help='Category slug (optional, will be generated from name if not provided)')
        
    def handle(self, *args, **options):
        name = options['name']
        description = options['description']
        slug = options['slug'] or slugify(name)
        
        category, created = Category.objects.update_or_create(
            slug=slug,
            defaults={
                'name': name,
                'description': description
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Successfully created category "{name}" with slug "{slug}"'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Successfully updated category "{name}" with slug "{slug}"')) 