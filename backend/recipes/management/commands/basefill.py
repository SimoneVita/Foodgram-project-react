import csv
import os

from django.core.management.base import BaseCommand

from foodgram import settings
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импорт данных из csv файла'

    def handle(self, *args, **options):
        print('Начинаю заполнять базу.')
        path = os.path.join(settings.BASE_DIR, 'ingredients.csv')
        with open(path, 'r') as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                try:
                    Ingredient.objects.get_or_create(
                        name=row[0],
                        measurement_unit=row[1],
                    )
                except Exception as error:
                    print(f'Ошибка в строке {row}: {error}')

        print('База заполнена.')
