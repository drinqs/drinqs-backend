from abc import ABC
from django.core.management.base import BaseCommand
import autofixture
import numpy as np
import warnings

class Command(BaseCommand, ABC):
    def handle(self, *args, **kwargs):
        bo_list = [True, False]
        warnings.simplefilter(action='ignore', category=FutureWarning)
        for i in range(1, 25):
            bad_review = autofixture.create("drinqsapp.review", 15, field_values={'liked': True,
                                                                                  'bookmarked': np.random.choice(bo_list, 1)})
            middle_review = autofixture.create("drinqsapp.review", 15,field_values={'liked': np.random.choice(bo_list, 1),
                                                                                      'bookmarked':np.random.choice(bo_list, 1)})

