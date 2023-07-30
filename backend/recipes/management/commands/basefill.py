import csv
import os

from django.core.management.base import BaseCommand

from foodgram.settings import BASE_DIR
from recipes.models import Ingredient


def get_reader(file_name):
    csv_path = os.path.join(BASE_DIR, 'static/data/', file_name)
    csv_file = open(csv_path, 'r', encoding='utf-8')
    reader = csv.reader(csv_file, delimiter=',')
    return reader


class Command(BaseCommand):
    help = 'Заполнение базы данных'

    def handle(self, *args, **options):
        reader = get_reader('ingredients.csv')
        next(reader, None)
        for row in reader:
            obj, created = Ingredient.objects.get_or_create(
                name=row[0],
                measurement_unit=row[1]
            )
