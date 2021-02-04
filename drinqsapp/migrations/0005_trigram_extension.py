from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('drinqsapp', '0004_populate_database'),
    ]

    operations = [
        TrigramExtension(),
    ]
