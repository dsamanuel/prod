# Generated by Django 4.2.10 on 2024-04-14 15:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('conceptnote', '0020_alter_activitysubmit_submission_status_and_more'),
        ('report', '0008_alter_icnreportsubmit_submission_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activityreportimpact',
            name='activityimpact',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='conceptnote.activityimpact'),
        ),
    ]