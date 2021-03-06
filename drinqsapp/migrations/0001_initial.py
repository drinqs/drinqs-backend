# Generated by Django 3.1.5 on 2021-01-24 12:42

import autoslug.fields
from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Cocktail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, unique=True)),
                ('slug', autoslug.fields.AutoSlugField(always_update=True, editable=False, max_length=128, populate_from='name', sep='--', unique=True)),
                ('alcoholic', models.IntegerField(blank=True, choices=[(0, 'not available'), (1, 'alcoholic'), (2, 'non alcoholic')], null=True)),
                ('category', models.CharField(blank=True, max_length=128, null=True)),
                ('preparation', models.TextField(blank=True, null=True)),
                ('thumbnail_url', models.CharField(blank=True, max_length=512, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Glass',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('liked', models.BooleanField(default=False, null=True)),
                ('bookmarked', models.BooleanField(default=False, null=True)),
                ('cocktail', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='drinqsapp.cocktail')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='IngredientTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, unique=True)),
                ('users', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, unique=True)),
                ('ingredient_tags', models.ManyToManyField(blank=True, to='drinqsapp.IngredientTag')),
            ],
        ),
        migrations.CreateModel(
            name='CocktailIngredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('measurement', models.IntegerField(choices=[(0, 'ml'), (1, 'oz'), (2, 'cup'), (3, 'tsp'), (4, 'Tbsp'), (5, 'package')])),
                ('amount', models.FloatField()),
                ('position', models.SmallIntegerField(blank=True, null=True)),
                ('cocktail', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='drinqsapp.cocktail')),
                ('ingredient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='drinqsapp.ingredient')),
            ],
        ),
        migrations.AddField(
            model_name='cocktail',
            name='glass',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='drinqsapp.glass'),
        ),
        migrations.AddField(
            model_name='cocktail',
            name='ingredients',
            field=models.ManyToManyField(through='drinqsapp.CocktailIngredient', to='drinqsapp.Ingredient'),
        ),
        migrations.AddField(
            model_name='cocktail',
            name='reviewers',
            field=models.ManyToManyField(through='drinqsapp.Review', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddConstraint(
            model_name='review',
            constraint=models.UniqueConstraint(fields=('user', 'cocktail'), name='unique_review'),
        ),
        migrations.AddConstraint(
            model_name='cocktailingredient',
            constraint=models.UniqueConstraint(fields=('cocktail', 'ingredient'), name='unique_cocktailingredients'),
        ),
        migrations.AddConstraint(
            model_name='cocktailingredient',
            constraint=models.UniqueConstraint(fields=('cocktail', 'position'), name='unique_cocktailposition'),
        ),
    ]
