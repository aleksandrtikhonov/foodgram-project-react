import csv

from django.apps import apps
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Imports data from csv-file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Define file path')
        parser.add_argument('model', type=str, help='Define model')

    def handle(self, *args, **options):
        file_path = options["file_path"]
        model_cl = apps.get_model('recipes', options["model"])

        with open(file_path, "r", encoding="utf-8") as csv_file:
            reader = csv.reader(csv_file, delimiter=',')
            header = next(reader)
            for row in reader:
                obj_dict = {key: value for key, value in zip(header, row)}

                print(obj_dict)
                model_cl.objects.create(**obj_dict)

        self.stdout.write(
            self.style.SUCCESS(
                'File successfully imported'
            )
        )
