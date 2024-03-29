# Generated by Django 4.2.10 on 2024-03-17 18:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conceptnote', '0003_activity_aworeda'),
    ]

    operations = [
        migrations.AddField(
            model_name='icn',
            name='cs_currency',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'USD'), (2, 'ETB')], default=1, null=True),
        ),
        migrations.AddField(
            model_name='icn',
            name='mc_currency',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'USD'), (2, 'ETB')], default=1, null=True),
        ),
    ]
