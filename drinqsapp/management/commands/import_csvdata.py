from abc import ABC
from django.core.management.base import BaseCommand
from drinqsapp.importer.data_handling import DataHandler

class Command(BaseCommand, ABC):
    def handle(self, *args, **kwargs):
        DataHandler().get_csv_data()
