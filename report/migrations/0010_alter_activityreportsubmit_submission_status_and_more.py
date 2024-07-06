# Generated by Django 4.2.10 on 2024-04-14 15:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_admin', '0004_submission_status'),
        ('report', '0009_alter_activityreportimpact_activityimpact'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activityreportsubmit',
            name='submission_status',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_admin.submission_status'),
        ),
        migrations.AlterField(
            model_name='activityreportsubmitapproval_f',
            name='approval_status',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_admin.approvalt_status'),
        ),
        migrations.AlterField(
            model_name='activityreportsubmitapproval_p',
            name='approval_status',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_admin.approvalf_status'),
        ),
        migrations.AlterField(
            model_name='activityreportsubmitapproval_t',
            name='approval_status',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_admin.approvalt_status'),
        ),
    ]