from abc import ABC
from django.core.management.base import BaseCommand
import autofixture
import numpy as np
import warnings

class Command(BaseCommand, ABC):
    def handle(self, *args, **kwargs):
        bo_list = [True, False]
        warnings.simplefilter(action='ignore', category=FutureWarning)

        bad_review = autofixture.create("drinqsapp.review", 50, field_values={'liked': True,
                                                                              'bookmarked': np.random.choice(bo_list, 1)})
        middle_review = autofixture.create("drinqsapp.review", 50,field_values={'liked': bool(np.random.choice(bo_list, 1))})

