from django.core.management import BaseCommand
from recipes.models import Tag


class Command(BaseCommand):
    help = 'Loads tags'

    def handle(self, *args, **kwargs):
        data = [
            {'name': 'Завтрак', 'color': '#E26C2D', 'slug': 'breakfast'},
            {'name': 'Обед', 'color': '#138808', 'slug': 'lunch'},
            {'name': 'Ужин', 'color': '#960a08', 'slug': 'dinner'},
        ]
        Tag.objects.bulk_create(Tag(**tag) for tag in data)
        self.stdout.write(self.style.SUCCESS('Тэги загружены'))