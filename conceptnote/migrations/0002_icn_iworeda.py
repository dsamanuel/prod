# Generated by Django 4.2.10 on 2024-03-09 20:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('program', '0003_program_portfolio'),
        ('conceptnote', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='icn',
            name='iworeda',
            field=models.ManyToManyField(blank=True, related_name='program_woredas', to='program.implementationarea'),
        ),
    ]
