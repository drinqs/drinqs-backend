from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('drinqsapp', '0003_auto_20210124_1945'),
    ]

    operations = [
        TrigramExtension(),
    ]
