# Generated by Django 3.1.5 on 2021-01-20 09:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drinqsapp', '0004_auto_20210120_0833'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='bookmarked',
            field=models.BooleanField(default=False, null=True),
        ),
        migrations.AlterField(
            model_name='review',
            name='liked',
            field=models.BooleanField(default=False, null=True),
        ),
    ]
